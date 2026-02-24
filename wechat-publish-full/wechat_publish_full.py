#!/usr/bin/env python3
"""
微信公众号发布工具 v2.5
功能：
1. 根据主题生成文章 → 发布公众号
2. 已有文章（Markdown）→ 转换 HTML → 发布公众号

v2.5 更新：
- 封面生成失败时使用默认封面
- 优化编码处理
- 更详细的错误提示
"""

import argparse
import json
import requests
import subprocess
import sys
from pathlib import Path

WECHAT_API_BASE = "https://api.weixin.qq.com"

def create_draft(title: str, author: str, html_content: str, thumb_media_id: str, app_id: str, app_secret: str) -> bool:
    """创建草稿（优化编码版本）"""
    print(f"📝 创建草稿...")

    # 获取 access_token
    url = f"{WECHAT_API_BASE}/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
    resp = requests.get(url)
    result = resp.json()

    if "access_token" not in result:
        print(f"❌ 获取 access_token 失败: {result}")
        return False

    access_token = result["access_token"]

    # 构造数据
    data = {
        "articles": [{
            "title": title[:32],  # 标题限制 32 字符
            "author": author[:8],  # 作者限制 8 字符
            "content": html_content,
            "thumb_media_id": thumb_media_id,
            "digest": f"{author} - {title[:20]}...",
            "need_open_comment": 1
        }]
    }

    draft_url = f"{WECHAT_API_BASE}/cgi-bin/draft/add?access_token={access_token}"

    # 关键修复：手动编码 JSON，使用 ensure_ascii=False 保留中文
    json_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
    }

    resp = requests.post(draft_url, data=json_bytes, headers=headers)
    result = resp.json()

    if result.get("errcode") == 0:
        print(f"✅ 草稿创建成功！")
        return True
    else:
        print(f"❌ 草稿创建失败: {result}")
        return False


def generate_cover_image(title: str, summary: str, output_path: str):
    """生成封面图（优化版本）"""
    print(f"🖼️ 生成封面图...")

    # 默认封面图提示词
    default_prompt = "Minimalist tech cover, blue gradient background, abstract AI neural network patterns, clean white text space, professional business style --ar 2.35:1 --v 6.1"

    ZIMAGE_API = "https://api-inference.modelscope.cn/v1/images/generations"
    ZIMAGE_KEY = "ms-9d9aef10-3ad7-477d-8f52-f687c7ba3cef"

    data = {
        "model": "Tongyi-MAI/Z-Image",
        "prompt": default_prompt,
        "size": "900x383"
    }

    headers = {
        "Authorization": f"Bearer {ZIMAGE_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # 创建异步任务
        resp = requests.post(ZIMAGE_API, headers=headers, json=data, timeout=30)
        if resp.status_code != 200:
            print(f"⚠️ 封面生成失败，使用备用方案")
            return None

        task_id = resp.json().get("task_id")
        print(f"📋 封面任务ID: {task_id}")

        # 轮询结果
        for i in range(60):
            import time
            time.sleep(5)

            status_resp = requests.get(
                f"https://api-inference.modelscope.cn/v1/tasks/{task_id}",
                headers={"Authorization": f"Bearer {ZIMAGE_KEY}", "X-ModelScope-Task-Type": "image_generation"}
            )
            status_data = status_resp.json()

            if status_data.get("task_status") == "SUCCEED":
                img_url = status_data["output_images"][0]
                img_data = requests.get(img_url).content

                with open(output_path, 'wb') as f:
                    f.write(img_data)
                print(f"✅ 封面图已保存: {output_path}")
                return output_path
            elif status_data.get("task_status") == "FAILED":
                print(f"⚠️ 封面生成失败")
                return None

        print(f"⚠️ 封面生成超时")
        return None

    except Exception as e:
        print(f"⚠️ 封面生成异常: {e}")
        return None


def upload_image(image_path: str, app_id: str, app_secret: str) -> str:
    """上传图片到公众号素材库"""
    print(f"📤 上传封面图...")

    url = f"{WECHAT_API_BASE}/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
    resp = requests.get(url)
    result = resp.json()

    if "access_token" not in result:
        print(f"❌ 获取 access_token 失败")
        return None

    access_token = result["access_token"]
    upload_url = f"{WECHAT_API_BASE}/cgi-bin/material/add_material?access_token={access_token}&type=image"

    try:
        with open(image_path, 'rb') as f:
            files = {'media': (image_path, f, 'image/jpeg')}
            resp = requests.post(upload_url, files=files, timeout=30)

        result = resp.json()
        if result.get("media_id"):
            print(f"✅ 封面上传成功")
            return result['media_id']
        else:
            print(f"❌ 封面上传失败: {result}")
            return None
    except Exception as e:
        print(f"❌ 封面上传异常: {e}")
        return None


def md_to_html(content: str, title: str = "Article", author: str = "", theme: str = "default") -> str:
    """使用 markdown-to-html 技能将 Markdown 转换为 HTML"""
    print("📄 转换 Markdown → HTML...")

    try:
        sys.path.insert(0, '/root/.openclaw/workspace')
        from tools.markdown_to_html import convert_markdown_to_html

        html, meta = convert_markdown_to_html(
            content,
            theme=theme,
            title=title,
            author=author,
            keep_title=True
        )

        if html.startswith("<!DOCTYPE html>") or html.startswith("<html"):
            print("✅ HTML 转换成功")
            return html

    except Exception as e:
        print(f"⚠️ markdown-to-html 调用失败: {e}")

    # 备用：使用 basic 转换
    print("🔄 使用基础转换...")
    import markdown
    html = markdown.markdown(content, extensions=['tables', 'fenced_code', 'nl2br'])
    return html


def optimize_wechat_html(html_content: str) -> str:
    """为公众号 HTML 添加内联样式（参考成功案例）"""
    import re

    # 1. 处理 h1 标题
    html_content = re.sub(
        r'<h1[^>]*>(.*?)</h1>',
        r'<h1 style="font-size: 24px; font-weight: 600; margin: 24px 0 16px; color: #1a1a1a; text-align: center; border-bottom: 2px solid #007aff; padding-bottom: 12px;">\1</h1>',
        html_content
    )

    # 2. 处理 h2 标题（紫色渐变背景）
    html_content = re.sub(
        r'<h2[^>]*>(.*?)</h2>',
        r'<h2 style="font-size: 20px; font-weight: 600; margin: 24px 0 12px; color: #ffffff; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 8px 16px; border-radius: 4px;">\1</h2>',
        html_content
    )

    # 3. 处理 h3 标题
    html_content = re.sub(
        r'<h3[^>]*>(.*?)</h3>',
        r'<h3 style="font-size: 18px; font-weight: 600; margin: 20px 0 10px; color: #333333;">\1</h3>',
        html_content
    )

    # 4. 处理普通段落
    html_content = re.sub(
        r'<p>(.*?)</p>',
        r'<p style="margin: 16px 0; line-height: 1.8; color: #333333;">\1</p>',
        html_content
    )

    # 5. 处理列表 ul
    html_content = re.sub(
        r'<ul[^>]*>',
        r'<ul style="padding-left: 24px; margin: 16px 0;">',
        html_content
    )

    # 6. 处理列表项 li
    html_content = re.sub(
        r'<li[^>]*>(.*?)</li>',
        r'<li style="margin: 8px 0; line-height: 1.7; color: #333333;">\1</li>',
        html_content
    )

    # 7. 处理表格
    html_content = re.sub(
        r'<table[^>]*>',
        r'<table style="width: 100%; border-collapse: collapse; margin: 16px 0;">',
        html_content
    )
    html_content = re.sub(
        r'<thead[^>]*>',
        r'<thead style="background: #f5f5f5;">',
        html_content
    )
    html_content = re.sub(
        r'<th([^>]*)>',
        r'<th\1 style="padding: 10px; border: 1px solid #ddd; text-align: left; font-weight: 600;">',
        html_content
    )
    html_content = re.sub(
        r'<td([^>]*)>',
        r'<td\1 style="padding: 10px; border: 1px solid #ddd;">',
        html_content
    )

    # 8. 处理引用 blockquote
    html_content = re.sub(
        r'<blockquote[^>]*>',
        r'<blockquote style="border-left: 4px solid #667eea; padding-left: 16px; margin: 16px 0; color: #666666; background: #f9f9f9; padding: 12px 16px;">',
        html_content
    )

    # 9. 处理 hr 分割线
    html_content = re.sub(
        r'<hr\s*/?>',
        r'<hr style="border: none; border-top: 1px solid #eeeeee; margin: 24px 0;" />',
        html_content
    )

    # 10. 处理 strong/bold
    html_content = re.sub(
        r'<strong>(.*?)</strong>',
        r'<strong style="font-weight: 600; color: #1a1a1a;">\1</strong>',
        html_content
    )

    print("✅ 样式优化完成（内联样式）")
    return html_content


def fix_html_for_wechat(html: str) -> str:
    """修复 HTML 以适配微信编辑器（兼容旧版本）"""
    import re

    # 移除可能导致问题的样式
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)

    # 修复图片样式
    html = re.sub(r'<img([^>]*)>', r'<img\1 style="max-width:100%;height:auto;" />', html)

    # 修复代码块样式
    html = re.sub(r'<pre>', r'<pre style="background:#f5f5f5;padding:12px;border-radius:4px;overflow-x:auto;">', html)

    # 在段落间添加换行
    html = re.sub(r'(</p>)\s*(<p)', r'\1<br><br>\2', html)

    # 移除多余的空行
    html = re.sub(r'\n{3,}', '\n\n', html)

    print("✅ HTML 修复完成")
    return html


def generate_article(topic: str) -> str:
    """根据主题生成 Markdown 文章"""
    print(f"📝 根据主题生成文章: {topic}")

    prompt = f"""请为微信公众号写一篇深度文章：

主题：{topic}

要求：
1. 2000-3000 字
2. Markdown 格式
3. 包含标题、章节、小标题
4. 使用列表呈现要点
5. 语言专业但不晦涩"""

    try:
        resp = requests.post(
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            headers={
                "Authorization": "Bearer 6056b7a100ea46c4b8772d4afee17131.DdXrHmnjSLlmCjjP",
                "Content-Type": "application/json"
            },
            json={
                "model": "glm-4.7",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 4000
            },
            timeout=180
        )
        result = resp.json()

        if "choices" in result:
            article = result["choices"][0]["message"]["content"]
            article = article.strip()
            if article.startswith("```markdown"):
                article = article[12:]
            if article.startswith("```"):
                article = article[3:]
            if article.endswith("```"):
                article = article[:-3]
            print("✅ 文章生成成功")
            return article.strip()
        else:
            raise Exception("AI 生成失败")
    except Exception as e:
        print(f"❌ 文章生成失败: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='公众号发布工具 v2.5')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--topic', '-T', help='文章主题（AI 生成文章）')
    group.add_argument('--content', '-c', help='文章内容（Markdown 格式，已有文章）')

    parser.add_argument('--title', '-t', help='文章标题（可选，自动从内容提取或生成）')
    parser.add_argument('--author', '-a', default='AI观察', help='作者名称（默认: AI观察）')
    parser.add_argument('--app-id', required=True, help='微信公众号 AppID')
    parser.add_argument('--app-secret', required=True, help='微信公众号 AppSecret')
    parser.add_argument('--preview', '-p', action='store_true', help='仅预览 HTML')
    parser.add_argument('--cover-only', action='store_true', help='只生成封面图')
    parser.add_argument('--theme', default='default', choices=['default', 'simple', 'grace'],
                        help='HTML 主题风格')

    args = parser.parse_args()

    print("=" * 60)
    print("🚀 公众号发布流程 v2.5（优化版）")
    print("=" * 60)

    # Step 1: 获取内容
    content = args.content.replace('\\n', '\n') if args.content else ""

    if args.topic:
        print(f"\n📋 模式 1：根据主题生成文章")
        print(f"主题：{args.topic}")
        article = generate_article(args.topic)
        if not article:
            sys.exit(1)
        content = article
        title = args.title or args.topic
    else:
        print(f"\n📋 模式 2：直接转换已有文章")
        title = args.title
        if not title:
            lines = content.strip().split('\n')
            for line in lines[:5]:
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
            title = title or "未命名文章"
        print(f"标题：{title}")

    # 保存原始 Markdown
    output_dir = Path("/root/.openclaw/workspace/wechat_output")
    output_dir.mkdir(exist_ok=True)
    safe_title = "".join(c for c in title if c.isalnum() or c in ' -_')[:30]
    md_path = output_dir / f"{safe_title}_original.md"
    md_path.write_text(content, encoding='utf-8')
    print(f"✅ 原文已保存: {md_path}")

    # Step 2: 转换为 HTML
    print(f"\n📄 Step 2: Markdown → HTML ({args.theme} 主题)")
    html = md_to_html(content, title, args.author, args.theme)

    if args.preview:
        print("\n--- HTML 预览 ---\n")
        print(html[:2000] + "..." if len(html) > 2000 else html)
        return

    # 保存 HTML
    html_path = output_dir / f"{safe_title}_content.html"
    html_path.write_text(html, encoding='utf-8')
    print(f"✅ HTML 已保存: {html_path}")

    # Step 3: 生成封面图
    print(f"\n🖼️ Step 3: 生成封面图")
    cover_path = output_dir / f"{safe_title}_cover.jpg"
    generate_cover_image(title, content[:300], str(cover_path))

    # 如果封面生成失败，使用备用封面
    if not Path(cover_path).exists():
        print("⚠️ 使用备用封面图...")
        backup_cover = "/root/.openclaw/workspace/wechat_output/cover_article.png"
        if Path(backup_cover).exists():
            import shutil
            shutil.copy(backup_cover, cover_path)
            print(f"✅ 已使用备用封面")
        else:
            print("❌ 无备用封面，将跳过封面设置")

    if args.cover_only:
        return

    # Step 4: 上传封面图
    print("\n📤 Step 4: 上传封面图")
    if Path(cover_path).exists():
        media_id = upload_image(str(cover_path), args.app_id, args.app_secret)
        if not media_id:
            print("⚠️ 封面上传失败，将不带封面上传")
            media_id = ""
    else:
        print("⚠️ 封面图不存在，跳过封面上传")
        media_id = ""

    # Step 5: 样式优化（内联样式 + 微信适配）
    print("\n🔧 Step 5: 优化 HTML 样式")
    html_fixed = optimize_wechat_html(html)
    html_fixed = fix_html_for_wechat(html_fixed)

    # 保存修复后的 HTML
    html_fixed_path = output_dir / f"{safe_title}_fixed.html"
    html_fixed_path.write_text(html_fixed, encoding='utf-8')
    print(f"✅ 修复后 HTML 已保存")

    # Step 6: 创建草稿
    print("\n📝 Step 6: 创建草稿")
    success = create_draft(title, args.author, html_fixed, media_id, args.app_id, args.app_secret)

    if success:
        print("\n" + "=" * 60)
        print("✅ 发布成功！")
        print(f"📝 标题：{title}")
        print(f"👤 作者：{args.author}")
        print("=" * 60)
    else:
        print("\n❌ 发布失败")


if __name__ == "__main__":
    main()
