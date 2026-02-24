{
  "name": "wechat-publish-full",
  "description": "公众号发布完整流程 v2.3：**修复编码问题** - 使用 UTF-8 编码手动构建 JSON 请求，解决 \\uXXXX 乱码问题。支持两种模式：1) 根据主题生成文章 2) 已有 Markdown 文章转换后发布。支持 3 种主题风格（default/simple/grace）。",
  "version": "2.3.0",
  "author": "OpenClaw",
  "triggerKeywords": [
    "发布公众号",
    "发布到公众号",
    "公众号发布",
    "公众号完整流程",
    "上传公众号草稿",
    "公众号生成",
    "生成文章并发布"
  ],
  "skills": {
    "run": {
      "command": "python3 ${workspace}/tools/wechat_publish_full.py ${--topic| -T|} \"${topic_or_content}\" ${--title| -t|} \"${title}\" --author \"${author:-agent}\" --app-id \"${app_id}\" --app-secret \"${app_secret}\" ${--preview| -p|} ${--cover-only|} ${--theme|}",
      "parser": {
        "stdout": {
          "type": "text",
          "pattern": "^(published:.*|✅|❌|📝|🖼️|📤|📄|🚀|📋).*$",
          "flags": "m"
        }
      }
    }
  },
  "parameters": {
    "topic_or_content": {
      "type": "string",
      "description": "二选一：文章主题（AI 生成文章）或 Markdown 内容（已有文章）",
      "required": true,
      "examples": [
        "AI Agent 架构设计",
        "# 文章标题\\n\\n这是文章内容..."
      ]
    },
    "topic": {
      "type": "string",
      "description": "明确指定为主题模式（AI 生成文章）",
      "required": false
    },
    "content": {
      "type": "string",
      "description": "明确指定为内容模式（已有 Markdown 文章）",
      "required": false
    },
    "title": {
      "type": "string",
      "description": "文章标题（可选，自动从内容提取）",
      "required": false
    },
    "author": {
      "type": "string",
      "description": "作者名称",
      "required": false,
      "default": "agent"
    },
    "app_id": {
      "type": "string",
      "description": "微信公众号 AppID",
      "required": true
    },
    "app_secret": {
      "type": "string",
      "description": "微信公众号 AppSecret",
      "required": true
    },
    "preview": {
      "type": "boolean",
      "description": "仅预览 HTML，不生成封面和上传",
      "required": false,
      "default": false
    },
    "cover_only": {
      "type": "boolean",
      "description": "只生成封面图，不上传公众号",
      "required": false,
      "default": false
    },
    "theme": {
      "type": "string",
      "description": "HTML 主题风格",
      "required": false,
      "default": "default",
      "choices": ["default", "simple", "grace"]
    }
  },
  "outputs": {
    "status": {
      "type": "string",
      "description": "状态：success / preview"
    },
    "mode": {
      "type": "string",
      "description": "执行模式：generate（AI生成）或 convert（直接转换）"
    },
    "html_path": {
      "type": "string",
      "description": "HTML 文件路径"
    },
    "cover_path": {
      "type": "string",
      "description": "封面图路径"
    },
    "original_md_path": {
      "type": "string",
      "description": "原始 Markdown 文件路径"
    }
  },
  "requirements": {
    "python": ["requests", "markdown"]
  },
  "notes": "功能更新 v2.1：\\n\\n**支持两种发布模式**：\\n1. **AI 生成模式**：传入主题，自动生成文章再发布\\n   - `发布公众号 \"AI Agent 架构设计\"`\\n\\n2. **直接转换模式**：传入已有 Markdown 内容\\n   - `发布公众号 \"# 我的文章\\n\\n内容...\"`\\n   - `发布公众号 --content \"Markdown 内容\"`\\n\\n**主题风格**：\\n- default：经典主题（标题彩底、二级标题渐变）\\n- simple：简洁主题（现代极简风）\\n- grace：优雅主题（圆角卡片）\\n\\n**流程**：\\n1. 判断模式（生成/转换）\\n2. Markdown → HTML（使用 markdown-to-html 技能）\\n3. 生成封面图\\n4. 上传公众号草稿箱\\n\\n**使用示例**：\\n- `发布公众号 \"AI 产品经理入门指南\"`\\n- `发布公众号 \"# 已有文章\\n\\n内容\" --title \"自定义标题\"`\\n- `发布公众号 \"主题\" --theme simple --preview`\\n- `发布公众号 --topic \"主题\" --content \"Markdown\"`（互斥，二选一）"
}
