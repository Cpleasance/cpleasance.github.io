"""
Jekyll Site Preview - Local development server for Jekyll sites
Renders Markdown with frontmatter without requiring Ruby/Jekyll
"""

import os
import re
import yaml
import markdown
import frontmatter
from flask import Flask, send_from_directory, render_template_string, abort
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

# Site root (tools/website_tester -> site root)
SITE_ROOT = Path(__file__).parent.parent.parent
LAYOUTS_DIR = SITE_ROOT / '_layouts'
INCLUDES_DIR = SITE_ROOT / '_includes'
ASSETS_DIR = SITE_ROOT / 'assets'
POSTS_DIR = SITE_ROOT / '_posts'
DRAFTS_DIR = SITE_ROOT / '_drafts'

# Load Jekyll config
config = {}
config_path = SITE_ROOT / '_config.yml'
if config_path.exists():
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f) or {}

SITE_TITLE = config.get('title', 'My Site')
SITE_DESCRIPTION = config.get('description', '')
SITE_URL = config.get('url', 'http://localhost:5001')


def load_layout(layout_name='default'):
    """Load a layout file from _layouts directory"""
    layout_path = LAYOUTS_DIR / f'{layout_name}.html'
    if layout_path.exists():
        with open(layout_path, 'r', encoding='utf-8') as f:
            return f.read()
    return '{{ content }}'


def load_include(include_name):
    """Load an include file from _includes directory"""
    include_path = INCLUDES_DIR / include_name
    if include_path.exists():
        with open(include_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''


def process_includes(content):
    """Process Jekyll include tags"""
    include_pattern = r'\{%\s*include\s+(\S+)\s*%\}'

    def replace_include(match):
        include_name = match.group(1)
        return load_include(include_name)

    return re.sub(include_pattern, replace_include, content)


def process_liquid_tags(content, page_data, site_data):
    """Process basic Liquid template tags"""
    # Process includes first
    content = process_includes(content)

    # Replace site variables
    content = re.sub(r'\{\{\s*site\.title\s*\}\}', site_data.get('title', ''), content)
    content = re.sub(r'\{\{\s*site\.description\s*\}\}', site_data.get('description', ''), content)
    content = re.sub(r'\{\{\s*site\.url\s*\}\}', site_data.get('url', ''), content)

    # Replace page variables
    content = re.sub(r'\{\{\s*page\.title\s*\}\}', str(page_data.get('title', '')), content)
    content = re.sub(r'\{\{\s*page\.date\s*\}\}', str(page_data.get('date', '')), content)
    content = re.sub(r'\{\{\s*page\.description\s*\}\}', str(page_data.get('description', '')), content)

    # Replace content placeholder
    content = re.sub(r'\{\{\s*content\s*\}\}', page_data.get('content', ''), content)

    # Handle basic if/endif for seo_tag and feed_meta (just remove them for preview)
    content = re.sub(r'\{%\s*seo\s*%\}', f'<title>{page_data.get("title", SITE_TITLE)}</title>', content)
    content = re.sub(r'\{%\s*feed_meta\s*%\}', '', content)

    # Remove other unprocessed Liquid tags to avoid display issues
    content = re.sub(r'\{%.*?%\}', '', content)
    content = re.sub(r'\{\{.*?\}\}', '', content)

    return content


def render_markdown(md_content):
    """Convert Markdown to HTML"""
    return markdown.markdown(
        md_content,
        extensions=['fenced_code', 'tables', 'toc', 'nl2br', 'attr_list']
    )


def process_markdown_file(file_path):
    """Process a markdown file with frontmatter"""
    with open(file_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)

    # Get frontmatter data
    page_data = dict(post.metadata)
    page_data['content'] = render_markdown(post.content)

    # Get layout
    layout_name = page_data.get('layout', 'default')
    layout = load_layout(layout_name)

    # Site data
    site_data = {
        'title': SITE_TITLE,
        'description': SITE_DESCRIPTION,
        'url': SITE_URL
    }

    # Process the layout with page data
    html = process_liquid_tags(layout, page_data, site_data)

    return html


def process_html_file(file_path):
    """Process an HTML file (may have frontmatter)"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if it has frontmatter
    if content.startswith('---'):
        post = frontmatter.loads(content)
        page_data = dict(post.metadata)
        page_data['content'] = post.content

        layout_name = page_data.get('layout', 'default')
        layout = load_layout(layout_name)

        site_data = {
            'title': SITE_TITLE,
            'description': SITE_DESCRIPTION,
            'url': SITE_URL
        }

        return process_liquid_tags(layout, page_data, site_data)

    return content


@app.route('/')
def index():
    """Serve the homepage"""
    # Try index.md first, then index.html
    index_md = SITE_ROOT / 'index.md'
    index_html = SITE_ROOT / 'index.html'

    if index_md.exists():
        return process_markdown_file(index_md)
    elif index_html.exists():
        return process_html_file(index_html)
    else:
        return '<h1>No index file found</h1>'


@app.route('/<path:path>')
def serve_page(path):
    """Serve any page or asset"""

    # Remove trailing slash
    path = path.rstrip('/')

    # Check for assets (CSS, JS, images)
    if path.startswith('assets/'):
        asset_path = SITE_ROOT / path
        if asset_path.exists() and asset_path.is_file():
            directory = asset_path.parent
            filename = asset_path.name
            return send_from_directory(directory, filename)
        abort(404)

    # Check for direct file paths (like favicon, robots.txt)
    direct_file = SITE_ROOT / path
    if direct_file.exists() and direct_file.is_file():
        if direct_file.suffix in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp']:
            return send_from_directory(direct_file.parent, direct_file.name)
        elif direct_file.suffix == '.xml':
            return send_from_directory(direct_file.parent, direct_file.name, mimetype='application/xml')
        elif direct_file.suffix == '.txt':
            return send_from_directory(direct_file.parent, direct_file.name, mimetype='text/plain')

    # Try different file patterns
    possible_paths = [
        SITE_ROOT / path / 'index.md',
        SITE_ROOT / path / 'index.html',
        SITE_ROOT / f'{path}.md',
        SITE_ROOT / f'{path}.html',
    ]

    for file_path in possible_paths:
        if file_path.exists():
            if file_path.suffix == '.md':
                return process_markdown_file(file_path)
            else:
                return process_html_file(file_path)

    # 404 page
    four_oh_four = SITE_ROOT / '404.md'
    if four_oh_four.exists():
        return process_markdown_file(four_oh_four), 404

    abort(404)


@app.route('/blog/')
def blog_index():
    """Serve the blog index"""
    blog_index_md = SITE_ROOT / 'blog' / 'index.md'
    if blog_index_md.exists():
        return process_markdown_file(blog_index_md)
    abort(404)


@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    four_oh_four = SITE_ROOT / '404.md'
    if four_oh_four.exists():
        return process_markdown_file(four_oh_four), 404
    return '<h1>404 - Page Not Found</h1>', 404


if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("Site Preview Server")
    print("=" * 50)
    print(f"\nSite: {SITE_TITLE}")
    print(f"Root: {SITE_ROOT}")
    print(f"\nOpen your browser to: http://localhost:5001")
    print("\nPress Ctrl+C to stop")
    print("=" * 50 + "\n")

    app.run(debug=True, port=5001, use_reloader=True)
