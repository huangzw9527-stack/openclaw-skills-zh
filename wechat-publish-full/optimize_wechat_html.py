#!/usr/bin/env python3
"""
公众号 HTML 样式优化器
参考成功案例，为 HTML 添加内联样式
"""

import re
import sys
from pathlib import Path


def optimize_wechat_html(html_content: str, title: str = "") -> str:
    """为公众号 HTML 添加内联样式"""

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

    # 11. 处理 code
    html_content = re.sub(
        r'<code[^>]*>(.*?)</code>',
        r'<code style="background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace;">\1</code>',
        html_content
    )

    # 12. 处理 pre 代码块
    html_content = re.sub(
        r'<pre[^>]*>',
        r'<pre style="background: #f5f5f5; padding: 12px; border-radius: 4px; overflow-x: auto; margin: 16px 0; font-size: 14px;">',
        html_content
    )

    # 13. 移除空的 <br>
    html_content = re.sub(r'<br>\s*<br>', '<br><br>', html_content)

    # 14. 清理多余的空行
    html_content = re.sub(r'\n{3,}', '\n\n', html_content)

    return html_content


def main():
    if len(sys.argv) < 2:
        print("用法: python optimize_wechat_html.py <html文件>")
        sys.exit(1)

    html_file = Path(sys.argv[1])

    if not html_file.exists():
        print(f"❌ 文件不存在: {html_file}")
        sys.exit(1)

    html_content = html_file.read_text(encoding='utf-8')
    optimized = optimize_wechat_html(html_content)

    # 保存优化后的文件
    output_file = html_file.parent / f"{html_file.stem}_styled{html_file.suffix}"
    output_file.write_text(optimized, encoding='utf-8')

    print(f"✅ 样式优化完成: {output_file}")
    print(f"📝 原始大小: {len(html_content)} 字符")
    print(f"📝 优化后: {len(optimized)} 字符")


if __name__ == "__main__":
    main()
