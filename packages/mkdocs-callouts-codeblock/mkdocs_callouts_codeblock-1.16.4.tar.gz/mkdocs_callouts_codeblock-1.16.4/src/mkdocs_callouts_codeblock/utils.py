import re

CALLOUT_BLOCK_REGEX = re.compile(r"^(\s*)((?:> ?)+) *\[!([^\]]*)\]([\-\+]?)(.*)?")
# (1): leading whitespace (all tabs and 4x spaces get reused)
# (2): indents (all leading '>' symbols)
# (3): callout type ([!'capture'] or [!'capture | attribute'] excl. brackets and leading !)
# (4): foldable token (+ or - or <blank>)
# (5): title

CALLOUT_CONTENT_SYNTAX_REGEX = re.compile(r"^(\s*)((?:> ?)+)")


# (1): leading whitespace (all tabs and 4x spaces get reused)
# (2): indents (all leading '>' symbols)


def convert_tabed_codeblocks_to_mkdocs_tabs(md_text: str) -> str:
    """
    将 Obsidian 带 tab 缩进的代码块转为 mkdocs-material 的多标签代码块。
    支持自动分组，连续的同组代码块合并为同一个多标签块。
    """
    import re
    lines = md_text.split('\n')
    result = []
    i = 0
    def parse_codeblock_params(param_str):
        # 解析所有属性，支持各种分隔符和顺序，严格只保留 title/hl_lines/linenums
        import re
        params = {}
        # 匹配所有 key=value 或 key:"value" 或 key='value' 或 key:value
        for m in re.finditer(r'(\w+)\s*(=|:)\s*(["\']?)([^"\'\s]+)\3', param_str):
            k, v = m.group(1).strip().lower(), m.group(4).strip()
            if k == 'file':
                params['title'] = v
            elif k == 'title':
                params['title'] = v
            elif k in ['hl', 'hl_lines']:
                params['hl'] = v
            elif k in ['ln', 'linenums']:
                params['linenums'] = v
            elif k in ['note', 'imp']:
                params[k] = v
            # 其他属性全部忽略
        return params

    def build_codeblock_params(params):
        # 只允许 title, hl_lines, linenums
        out = []
        if 'title' in params:
            out.append(f'title="{params["title"]}"')
        if 'hl_lines' in params:
            out.append(f'hl_lines="{params["hl_lines"]}"')
        if 'linenums' in params:
            out.append(f'linenums="{params["linenums"]}"')
        return ' '.join(out)

    def merge_hl_ln(params):
        # hl/ln/note/imp 统一处理
        hl = params.get('hl') or params.get('hl_lines')
        note = params.get('note')
        imp = params.get('imp')
        ln = params.get('ln') or params.get('linenums')
        # hl/note/imp 合并，ln 只单独作为 linenums，hl_lines 需偏移
        hl_nums = []
        def parse_hl(s):
            res = []
            for part in s.split(','):
                if '-' in part:
                    a, b = part.split('-')
                    res.extend(list(range(int(a), int(b)+1)))
                else:
                    res.append(int(part))
            return res
        for s in [hl, note, imp]:
            if s:
                hl_nums.extend(parse_hl(s))
        # 偏移
        offset = int(ln) - 1 if ln else 0
        hl_nums = [n - offset for n in hl_nums if n - offset > 0]
        # 去重、排序
        hl_nums = sorted(set(hl_nums))
        # 合并为区间字符串
        def merge_ranges(nums):
            if not nums:
                return ''
            nums = sorted(nums)
            ranges = []
            start = prev = nums[0]
            for n in nums[1:]:
                if n == prev + 1:
                    prev = n
                else:
                    ranges.append((start, prev))
                    start = prev = n
            ranges.append((start, prev))
            return ' '.join([f'{a}-{b}' if a != b else f'{a}' for a, b in ranges])
        hl_str = merge_ranges(hl_nums)
        if hl_str:
            params['hl_lines'] = hl_str
        else:
            params.pop('hl_lines', None)
        params.pop('hl', None)
        params.pop('note', None)
        params.pop('imp', None)
        # linenums 只保留 ln/linenums
        if ln:
            params['linenums'] = ln
            params.pop('ln', None)
        else:
            params.pop('linenums', None)
        # 移除所有非 title/hl_lines/linenums
        for k in list(params.keys()):
            if k not in ('title', 'hl_lines', 'linenums'):
                params.pop(k)
        return params

    while i < len(lines):
        # 匹配所有代码块（无论是否带tab）
        m = re.match(r'^```(\w+)((?: [^`]*)?)', lines[i])
        if m:
            lang = m.group(1)
            param_str = m.group(2)
            # 提取 tab（如有）
            tab_match = re.search(r'tab="([^"]+)"', param_str)
            tab = tab_match.group(1) if tab_match else None
            # 移除 group="..." 字段
            param_str = re.sub(r'group="[^"]*"', '', param_str)
            # 处理 title:xxx, file="xxx" 等
            params = parse_codeblock_params(param_str)
            # 传递语言给 build_codeblock_params 用于 emoji
            params['__lang__'] = lang
            # hl/ln/note/imp 处理
            params = merge_hl_ln(params)
            # 只保留 title/hl_lines/linenums
            param_out = build_codeblock_params(params)
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            # 跳过代码块结尾
            if i < len(lines) and lines[i].startswith('```'):
                i += 1
            if tab:
                result.append(f'=== "{tab}"\n')
                result.append('    ```' + lang + (f' {param_out}' if param_out else ''))
                for l in code_lines:
                    result.append('    ' + l)
                result.append('    ```\n')
            else:
                result.append('```' + lang + (f' {param_out}' if param_out else ''))
                result.extend(code_lines)
                result.append('```')
            continue
        # 非代码块，原样输出
        result.append(lines[i])
        i += 1
    return '\n'.join(result)


class CalloutParser:
    """Class to parse callout blocks from markdown and convert them to mkdocs supported admonitions."""

    # From https://help.obsidian.md/How+to/Use+callouts#Types
    aliases = {
        "abstract": ["summary", "tldr"],
        "tip": ["hint", "important"],
        "success": ["check", "done"],
        "question": ["help", "faq"],
        "warning": ["caution", "attention"],
        "failure": ["fail", "missing"],
        "danger": ["error"],
        "quote": ["cite"],
    }
    alias_tuples = [
        (alias, c_type) for c_type, aliases in aliases.items() for alias in aliases
    ]

    def __init__(self, convert_aliases: bool = True, breakless_lists: bool = True):
        # Stack to keep track of the current indentation level
        self.indent_levels: list[int] = list()
        # Whether to convert aliases or not
        self.convert_aliases: bool = convert_aliases

        # Breakless list allow for lists to be created without a blank line between them
        # (Obsidian's default behavior, but not within the scope of the CommonMark spec)
        self.breakless_lists: bool = breakless_lists
        # Flags to keep track of the previous line's content for breakless list handling
        self.text_in_prev_line: bool = False
        self.list_in_prev_line: bool = False

        # Check that the callout isn't inside a codefence (list of codefence indices)
        self.in_codefence: list = list()

    def _get_indent(self, indent_level: int, is_block: bool = False) -> str:
        """
        Returns the correct indent string for the current indent level.
        """
        indent = ""
        # If we are parsing a block, then we should not add a tab for the last indent level (only content needs it)
        for i in range(indent_level - int(is_block)):
            # If the indent level exists in the list, add a tab (callout), otherwise add a '> ' (blockquote)
            indent += "\t" if i + 1 in self.indent_levels else "> "

        # Blockquotes use spaces instead of tabs for consistent indentation (must be 4 spaces into the callout)
        # When not using blockquotes, a tab should count as 4 spaces by default because of no preceding symbols
        # blockquote:   > !!! note "Title"   ||   blockquote:   > !!! note "Title"
        # with \t       > SSContent (wrong)  ||   with spaces   > SSSSContent (correct)
        is_part_of_blockquote = (
            "> " in indent
        )  # indent should only be '\t' symbols if false.
        if is_part_of_blockquote:
            indent = indent.replace("\t", " " * 4)

        return indent

    def _parse_block_syntax(self, block) -> str:
        """
        Converts the callout syntax from obsidian into the mkdocs syntax
        Takes an argument block, which is a regex match.
        """
        # Group 1: Leading whitespace (we need to reuse tabs and 4x spaces)
        whitespace = block.group(1).replace("    ", "\t")
        whitespace = "\t" * whitespace.count("\t")  # Ignore everything but tabs

        # Group 2: Leading > symbols (indentation, for nested callouts)
        indent_level = block.group(2).count(">")
        indent = (
            f"{whitespace}{self._get_indent(indent_level=indent_level, is_block=True)}"
        )

        # Group 3: Callout block type (note, warning, info, etc.) + inline block syntax
        c_type = block.group(3).lower()
        # Get a clean version of the callout type for the title, if it exists in order
        # to use it as a fallback if the title is empty & we are using an alias
        clean_c_type = c_type.split("|")[0].strip()
        c_type = re.sub(r" *\| *(inline|left) *$", " inline", c_type)
        c_type = re.sub(r" *\| *(inline end|right) *$", " inline end", c_type)
        c_type = re.sub(r" *\|.*", "", c_type)
        # Convert aliases, if enabled
        if self.convert_aliases:
            c_type = self._convert_aliases(c_type)

        # Group 4: Foldable callouts
        syntax = {"-": "???", "+": "???+"}
        syntax = syntax.get(block.group(4), "!!!")

        # Group 5: Title, add leading whitespace and quotation marks, if it exists
        title = block.group(5).strip()
        # If we are using an alias without a title, use the alias
        # We use startswith to avoid issues with the inline block syntax
        if not title and not c_type.lower().startswith(clean_c_type.lower()):
            title = clean_c_type.capitalize()

        # Render the title according to the syntax
        if title in ['""', "''"]:
            title = ' ""'  # Quotes = does not render the heading, only block content
        elif title:
            title = f' "{title}"'  # Title was provided, add quotation marks
        else:
            title = ""  # No title provided, use the default (Note, Warning, etc.)

        # Construct the new callout syntax ({indent}!!! note "Title")
        return f"{indent}{syntax} {c_type}{title}"

    @staticmethod
    def _convert_aliases(c_type: str) -> str:
        """Converts aliases to their respective callout type, if its enabled"""
        for alias, identifier in CalloutParser.alias_tuples:
            c_type = re.sub(rf"^{alias}\b", identifier, c_type)
        return c_type

    def _breakless_list_handler(self, line: str) -> str:
        """
        Handles a breakless list by adding a newline if the previous line was text

        This is a workaround for Obsidian's default behavior, which allows for lists to be created
        without a blank line between them.
        """
        is_list = re.search(r"^\s*(?:[-+*]|\d+\.)\s", line)
        if is_list and self.text_in_prev_line:
            # If the previous line was a list, keep the line as is
            if self.list_in_prev_line:
                return line
            # If the previous line was text, add a newline before the list
            indent = re.search(r"^\t*", line).group()
            line = f"{indent}\n{line}"
        else:
            # Set text_in_prev_line according to the current line
            self.text_in_prev_line = line.strip() != ""
        self.list_in_prev_line = is_list
        return line

    def _convert_block(self, line: str) -> str:
        """Calls parse_block_syntax if regex matches, which returns a converted callout block"""
        match = re.search(CALLOUT_BLOCK_REGEX, line)
        if match:
            # Store the current indent level and add it to the list if it doesn't exist
            indent_level = match.group(2).count(">")

            # If the indent level is not in the indent levels, add it to the list
            if indent_level not in self.indent_levels:
                self.indent_levels.append(indent_level)
            return self._parse_block_syntax(match)

    def _reset_states(self):
        """
        Resets the states of the parser, including the indent levels and breakless list flags.
        """
        self.indent_levels = list()
        # These are unused if breakless_lists is disabled
        self.list_in_prev_line = False
        self.text_in_prev_line = False

    def _convert_content(self, line: str) -> str:
        """
        Converts the callout content by replacing leading '>' symbols with '\t'.

        Will return the original line if active_callout is false or if line is missing leading '>' symbols.
        """
        match = re.search(CALLOUT_CONTENT_SYNTAX_REGEX, line)
        if match and self.indent_levels:
            # Group 1: Leading whitespace (we need to reuse tabs and 4x spaces)
            whitespace = match.group(1).replace("    ", "\t")
            whitespace = "\t" * whitespace.count("\t")  # Ignore everything but tabs

            # Remove any higher level indents compared to the current indent level
            # i.e. if we are at 1, and indent_levels is [1, 2, 3], remove 2 and 3
            try:
                while match.group(2).count(">") < self.indent_levels[-1]:
                    self.indent_levels = self.indent_levels[:-1]
            except IndexError:
                # If the indent levels list is empty, reset the states and return the line
                # (we were in a blockquote, not a callout)
                self._reset_states()
                return line

            # Construct the new indent level
            indent = (
                f"{whitespace}{self._get_indent(indent_level=max(self.indent_levels))}"
            )

            line = re.sub(rf"^\s*(?:> ?){{{self.indent_levels[-1]}}}", indent, line)

            # Handle breakless lists before returning the line, if enabled
            if self.breakless_lists:
                line = self._breakless_list_handler(line)
        else:
            self._reset_states()
        return line

    def _toggle_codefence_at_index(self, index: int):
        """
        Adds or removes a codefence index to the list of active codefences.

        Only keeps track of 2 values, a primary one and a nested one.
        - 0 = primary codefence
        - 1 = nested codefence

        We could keep track of all indices, but it might cause more issues than it solves. (even though it shouldn't)
        """
        if index != 0:
            index = 1
        if index in self.in_codefence:
            self.in_codefence.remove(index)
        else:
            self.in_codefence.append(index)

    def convert_line(self, line: str) -> str:
        """
        Converts the syntax for callouts to admonitions for a single line of markdown
        returns _convert_block if line matches that of a callout block syntax,
        if line is not a block syntax, it will return _convert_content.
        """
        # Toggle codefence indices if we encounter a codefence
        # (If a line starts with '```' before any meaningful content, it's a codefence)
        if re.match(r"^\s*(?:>\s*)*```", line):
            self._toggle_codefence_at_index(line.index("```"))
        # Codefences get treated like content (because they could contain callouts inside them that should not convert)
        if self.in_codefence and self.indent_levels:
            return self._convert_content(line)
        elif self.in_codefence:
            return line
        return self._convert_block(line) or self._convert_content(line)

    def parse(self, markdown: str) -> str:
        """Takes a markdown file input returns a version with converted callout and codeblock tab syntax"""
        self.indent_levels = list()  # Reset (redundant in conjunction with mkdocs)
        # 先处理 callout
        if re.search(r"> *\[!", markdown):
            markdown = "\n".join(self.convert_line(line) for line in markdown.split("\n"))
        # 再处理代码块 tab
        markdown = convert_tabbed_codeblocks_to_mkdocs_tabs(markdown)
        return markdown
