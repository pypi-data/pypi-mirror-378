# mkdocs-callouts-codeblock

Based on the mkdocs-callouts extension.

## Dependency package

Obsidian-Plugin: codeblock-customizer

## Setup
Install the plugin using pip:

`pip install mkdocs-callouts-codeblock`

Activate the plugin in `mkdocs.yml`, note that some markdown_extensions are required for this plugin to function correctly:

```yaml
markdown_extensions:
  - nl2br
  - admonition
  - pymdownx.details
  - pymdownx.superfences

plugins:
  - search
  - callouts
```

> **Note:** If you have no `plugins` entry in your config file yet, you'll likely also want to add the `search` plugin. MkDocs enables it by default if there is no `plugins` entry set, but now you have to enable it explicitly.

## Usage
mkdocs-callouts converts the following:
```
> [!INFO] Title
> An information callout from Obsidian
> inspired by the syntax from the Microsoft Docs
```
and turns it into:
```
!!! info "Title"
    An admonition block for MkDocs.
    Allowing you to edit your notes
    with confidence using Obsidian.
```

mkdocs-codeblock converts the following:

```js file:packages\locales\src\langs\zh-CN\authentication.json hl="13,14" ln="1" group="中英语言" tab="中文"
{
  "welcomeBack": "欢迎回来",
  "pageTitle": "测试项目系统",
  "pageDesc": "更快、更简单、更安全的测试项目系统",
  ...
  }
```
```js file:packages\locales\src\langs\en-US\authentication.json hl="13,14" ln="11" group="中英语言" tab="English"
{
  "welcomeBack": "Welcome Back",
  "pageTitle": "Test System",
  "pageDesc": "Faster, simpler and safer Test projects",
  ...
}
```

and turns it into:

=== "中文"

    ```js title="packages\locales\src\langs\zh-CN\authentication.json" hl_lines="3 4" linenums="11" 
    {
      "welcomeBack": "欢迎回来",
      "pageTitle": "测试项目系统",
      "pageDesc": "更快、更简单、更安全的测试项目系统",
      ...
      }
    ```

=== "English"

    ```js title="packages\locales\src\langs\en-US\authentication.json" hl_lines="3 4" linenums="11" 
    {
      "welcomeBack": "Welcome Back",
      "pageTitle": "Test System",
      "pageDesc": "Faster, simpler and safer Test projects",
      ...
    }
    ```


### Foldable blocks
Foldable blocks are also supported. (`> [!INFO]- Foldable closed by default`, `> [!INFO]+ Foldable open by default`)

### Inline blocks
To turn a callout block into an inline block you can use the `|left` or `|right` syntax in the type notation like so:
```
> [!INFO|left] -> !!! info inline (alt: [!INFO | left])
> [!INFO|inline] -> !!! info inline

> [!INFO|right] -> !!! info inline end 
> [!INFO|inline end] -> !!! info inline end
```

The following also works, but Obsidian may not render the block type correctly.
```
> [!INFO inline] --> !!! info inline
> [!INFO inline end] --> !!! info inline end
```
To get more information about inline blocks, or how to add your own custom callout blocks, check the [Material Mkdocs Documentation](https://squidfunk.github.io/mkdocs-material/reference/admonitions/#inline-blocks).

### Aliases
Obsidian allows the use of [aliases when creating callouts](https://help.obsidian.md/How+to/Use+callouts#Types), mkdocs-callouts converts these to the corresponding block type. Should you wish to disable this behaviour then you can do so by setting `aliases` to `false` in the plugin configuration:
```yaml
plugins:
  - search
  - callouts:
      aliases: false
```

### Breakless lists (New in 1.11.0)
Markdown specification requires a blank line between list items and other block elements, whereas Obsidian does not require this. This plugin will by default automatically add a blank line between list items and callout blocks (if none are present). Should you wish to disable this behaviour then you can do so by setting `breakless_lists` to `false` in the plugin configuration:
```yaml
plugins:
  - search
  - callouts:
      breakless_lists: false
```