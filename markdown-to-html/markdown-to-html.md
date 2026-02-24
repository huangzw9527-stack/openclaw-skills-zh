{
  "name": "markdown-to-html",
  "description": "将 Markdown 格式转换为微信公众号优化的 HTML 格式。支持多种主题（default/simple/grace）、frontmatter、脚注、警告框、代码高亮。",
  "version": "2.0.0",
  "author": "OpenClaw (based on baoyu-markdown-to-html)",
  "triggerKeywords": [
    "markdown 转 html",
    "markdown 转html",
    "md 转 html",
    "md转html",
    "markdown2html",
    "生成 html",
    "生成html",
    "md2html"
  ],
  "skills": {
    "run": {
      "command": "python3 ${workspace}/tools/markdown_to_html.py \"${content_or_path}\" ${--output| --theme| --title| --author| --keep-title| --json| --stdin|}",
      "parser": {
        "stdout": {
          "type": "text",
          "pattern": "^<"
        }
      }
    }
  },
  "parameters": {
    "content_or_path": {
      "type": "string",
      "description": "Markdown 内容或 Markdown 文件路径",
      "required": true,
      "examples": [
        "# 标题\n\n这是内容",
        "/root/.openclaw/workspace/article.md"
      ]
    },
    "output": {
      "type": "string",
      "description": "输出 HTML 文件路径（可选）",
      "required": false,
      "examples": [
        "/root/.openclaw/workspace/output.html"
      ]
    },
    "theme": {
      "type": "string",
      "description": "主题风格",
      "required": false,
      "default": "default",
      "choices": ["default", "simple", "grace"],
      "examples": ["default", "simple", "grace"]
    },
    "title": {
      "type": "string",
      "description": "文章标题（用于 HTML title 标签）",
      "required": false,
      "default": ""
    },
    "author": {
      "type": "string",
      "description": "作者名称（显示在文章末尾）",
      "required": false,
      "default": ""
    },
    "keep-title": {
      "type": "boolean",
      "description": "保留文章中的第一个标题",
      "required": false,
      "default": false
    },
    "json": {
      "type": "boolean",
      "description": "输出 JSON 格式结果",
      "required": false,
      "default": false
    },
    "stdin": {
      "type": "boolean",
      "description": "从标准输入读取 Markdown 内容",
      "required": false,
      "default": false
    }
  },
  "outputs": {
    "html_content": {
      "type": "string",
      "description": "转换后的 HTML 内容"
    },
    "output_file": {
      "type": "string",
      "description": "输出文件路径（如果指定了 -o 参数）"
    },
    "json_result": {
      "type": "object",
      "description": "JSON 格式结果（如果指定了 --json 参数）"
    }
  },
  "requirements": {
    "python": ["markdown"]
  },
  "notes": "功能特点（基于 baoyu-markdown-to-html 设计）：\\n1. **3 种主题风格**：\\n   - default（经典）：标题居中彩底，二级标题渐变色\\n   - simple（简洁）：现代极简风，深色代码块\\n   - grace（优雅）：圆角卡片，文字阴影\\n\\n2. **支持 Markdown 特性**：\\n   - 标题、段落、列表\\n   - 代码块（语法高亮）\\n   - 表格、脚注\\n   - 警告框（NOTE/WARNING/TIP/IMPORTANT）\\n   - 图片、链接、引用\\n\\n3. **Frontmatter 支持**：\\n   ```yaml\\n   ---\\n   title: 文章标题\\n   author: 作者名\\n   description: 描述\\n   ---\\n   ```\\n\\n4. **ASCII 架构图支持**：横向滚动不换行\\n5. **移动端适配**：viewport meta + 触摸滚动\\n\\n使用示例：\\n- `markdown 转 html \"# 标题\\n\\n内容\"`\\n- `markdown 转 html article.md --theme simple`\\n- `markdown 转 html article.md -o output.html --keep-title`\\n- `cat article.md | markdown 转 html --stdin --json`"
}
