"""
Jekyll Site Preview - Local development server for Jekyll sites
Properly renders the site with layout, CSS, and Liquid template processing
"""

import os
import re
import yaml
import markdown
import frontmatter
from flask import Flask, send_from_directory, Response, abort
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

# Site variables
SITE = {
    'title': config.get('title', 'My Site'),
    'description': config.get('description', ''),
    'url': 'http://localhost:5001',  # Local preview URL
    'baseurl': '',
    'logo': config.get('logo', ''),
    'author': config.get('author', ''),
    'lang': config.get('lang', 'en-US'),
    'github': {
        'is_user_page': True,
        'owner_url': 'https://github.com/' + config.get('author', '').replace(' ', ''),
        'repository_name': config.get('title', ''),
        'build_revision': 'preview'
    }
}


def load_layout(layout_name='default'):
    """Load a layout file from _layouts directory"""
    layout_path = LAYOUTS_DIR / f'{layout_name}.html'
    if layout_path.exists():
        with open(layout_path, 'r', encoding='utf-8') as f:
            return f.read()
    return '<html><body>{{ content }}</body></html>'


def load_include(include_name):
    """Load an include file from _includes directory"""
    include_path = INCLUDES_DIR / include_name
    if include_path.exists():
        with open(include_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''


def load_posts():
    """Load all posts from _posts directory"""
    posts = []

    if POSTS_DIR.exists():
        for post_file in sorted(POSTS_DIR.glob('*.md'), reverse=True):
            try:
                with open(post_file, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)

                # Parse date from filename (YYYY-MM-DD-title.md)
                filename = post_file.stem
                date_match = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)', filename)

                if date_match:
                    date_str = date_match.group(1)
                    slug = date_match.group(2)
                    post_date = datetime.strptime(date_str, '%Y-%m-%d')
                else:
                    post_date = datetime.now()
                    slug = filename

                # Get excerpt (first paragraph)
                content_lines = post.content.strip().split('\n\n')
                excerpt = content_lines[0] if content_lines else ''
                # Remove markdown headers from excerpt
                excerpt = re.sub(r'^#+\s*', '', excerpt)

                posts.append({
                    'title': post.metadata.get('title', slug.replace('-', ' ').title()),
                    'date': post.metadata.get('date', post_date),
                    'url': f'/blog/{date_str}-{slug}',
                    'excerpt': excerpt,
                    'tags': post.metadata.get('tags', []),
                    'content': post.content,
                    'file_path': post_file
                })
            except Exception as e:
                print(f"Error loading post {post_file}: {e}")

    return posts


def process_liquid(content, page=None):
    """Process Liquid template tags"""
    if page is None:
        page = {}

    # Load posts for loops
    posts = load_posts()

    # Process for loops: {% for post in site.posts %}...{% endfor %}
    def process_for_loop(match):
        loop_content = match.group(1)
        result = []

        for post in posts:
            item_html = loop_content

            # Format date
            if isinstance(post['date'], datetime):
                formatted_date = post['date'].strftime('%B %d, %Y')
            else:
                formatted_date = str(post['date'])

            # Replace post variables
            item_html = re.sub(r'\{\{\s*post\.title\s*\}\}', post['title'], item_html)
            item_html = re.sub(r'\{\{\s*post\.url\s*\}\}', post['url'], item_html)
            item_html = re.sub(r'\{\{\s*post\.date\s*\|\s*date:\s*"[^"]*"\s*\}\}', formatted_date, item_html)
            item_html = re.sub(r'\{\{\s*post\.date\s*\}\}', formatted_date, item_html)
            item_html = re.sub(r'\{\{\s*post\.excerpt\s*\}\}', post['excerpt'], item_html)

            result.append(item_html)

        return ''.join(result)

    content = re.sub(
        r'\{%\s*for\s+post\s+in\s+site\.posts\s*%\}(.*?)\{%\s*endfor\s*%\}',
        process_for_loop,
        content,
        flags=re.DOTALL
    )

    # Process if site.posts.size == 0
    if len(posts) == 0:
        content = re.sub(
            r'\{%\s*if\s+site\.posts\.size\s*==\s*0\s*%\}(.*?)\{%\s*endif\s*%\}',
            r'\1',
            content,
            flags=re.DOTALL
        )
    else:
        content = re.sub(
            r'\{%\s*if\s+site\.posts\.size\s*==\s*0\s*%\}.*?\{%\s*endif\s*%\}',
            '',
            content,
            flags=re.DOTALL
        )

    # Process includes: {% include filename %}
    def replace_include(match):
        include_name = match.group(1).strip()
        return load_include(include_name)
    content = re.sub(r'\{%\s*include\s+([^\s%]+)\s*%\}', replace_include, content)

    # Process seo tag - generate basic SEO
    seo_html = f'''<title>{page.get('title', SITE['title'])}</title>
    <meta name="description" content="{page.get('description', SITE['description'])}">
    <meta property="og:title" content="{page.get('title', SITE['title'])}">
    <meta property="og:description" content="{page.get('description', SITE['description'])}">'''
    content = re.sub(r'\{%\s*seo\s*%\}', seo_html, content)

    # Process feed_meta
    content = re.sub(r'\{%\s*feed_meta\s*%\}', '', content)

    # Process if/endif blocks for site.logo
    if SITE['logo']:
        # Keep content inside if site.logo block
        content = re.sub(
            r'\{%\s*if\s+site\.logo\s*%\}(.*?)\{%\s*endif\s*%\}',
            r'\1',
            content,
            flags=re.DOTALL
        )
    else:
        # Remove if site.logo block entirely
        content = re.sub(
            r'\{%\s*if\s+site\.logo\s*%\}.*?\{%\s*endif\s*%\}',
            '',
            content,
            flags=re.DOTALL
        )

    # Process if/endif for site.github.is_user_page
    content = re.sub(
        r'\{%\s*if\s+site\.github\.is_user_page\s*%\}(.*?)\{%\s*endif\s*%\}',
        r'\1',
        content,
        flags=re.DOTALL
    )

    # Remove any remaining if/endif blocks
    content = re.sub(r'\{%\s*if\s+.*?%\}', '', content)
    content = re.sub(r'\{%\s*endif\s*%\}', '', content)

    # Process variable outputs with filters

    # Handle CSS paths: {{ "/assets/css/style.css?v=" | append: site.github.build_revision | relative_url }}
    content = re.sub(
        r'\{\{\s*"/assets/css/style\.css\?v="[^}]*\}\}',
        '/assets/css/style.css',
        content
    )
    content = re.sub(
        r'\{\{\s*"/assets/css/custom\.css\?v="[^}]*\}\}',
        '/assets/css/custom.css',
        content
    )

    # Handle feed.xml path
    content = re.sub(
        r'\{\{\s*"/feed\.xml"\s*\|\s*relative_url\s*\}\}',
        '/feed.xml',
        content
    )

    # Handle root path
    content = re.sub(
        r'\{\{\s*"/"\s*\|\s*absolute_url\s*\}\}',
        '/',
        content
    )

    # Site variables
    content = re.sub(r'\{\{\s*site\.title\s*\}\}', SITE['title'], content)
    content = re.sub(r'\{\{\s*site\.description\s*\}\}', SITE['description'], content)
    content = re.sub(r'\{\{\s*site\.url\s*\}\}', SITE['url'], content)
    content = re.sub(r'\{\{\s*site\.baseurl\s*\}\}', SITE['baseurl'], content)
    content = re.sub(r'\{\{\s*site\.author\s*\}\}', SITE['author'], content)
    content = re.sub(r'\{\{\s*site\.lang\s*\}\}', SITE['lang'], content)

    # Site logo with relative_url filter
    content = re.sub(
        r'\{\{\s*site\.logo\s*\|\s*relative_url\s*\}\}',
        SITE['logo'],
        content
    )
    content = re.sub(r'\{\{\s*site\.logo\s*\}\}', SITE['logo'], content)

    # GitHub variables
    content = re.sub(r'\{\{\s*site\.github\.owner_url\s*\}\}', SITE['github']['owner_url'], content)
    content = re.sub(r'\{\{\s*site\.github\.repository_name\s*\}\}', SITE['github']['repository_name'], content)
    content = re.sub(r'\{\{\s*site\.github\.build_revision\s*\}\}', SITE['github']['build_revision'], content)

    # Fallback patterns with default
    content = re.sub(
        r'\{\{\s*site\.title\s*\|\s*default:\s*site\.github\.repository_name\s*\}\}',
        SITE['title'],
        content
    )
    content = re.sub(
        r'\{\{\s*site\.description\s*\|\s*default:\s*site\.github\.project_tagline\s*\}\}',
        SITE['description'],
        content
    )
    content = re.sub(
        r'\{\{\s*site\.lang\s*\|\s*default:\s*"en-US"\s*\}\}',
        SITE['lang'],
        content
    )

    # Page variables
    content = re.sub(r'\{\{\s*page\.title\s*\}\}', str(page.get('title', '')), content)
    content = re.sub(r'\{\{\s*page\.date\s*\}\}', str(page.get('date', '')), content)
    content = re.sub(r'\{\{\s*page\.description\s*\}\}', str(page.get('description', '')), content)

    # Content placeholder
    content = re.sub(r'\{\{\s*content\s*\}\}', page.get('content', ''), content)

    # Clean up any remaining unprocessed Liquid
    content = re.sub(r'\{%[^%]*%\}', '', content)
    content = re.sub(r'\{\{[^}]*\}\}', '', content)

    return content


def render_markdown(md_content):
    """Convert Markdown to HTML with Jekyll-style attribute lists"""
    # Process Jekyll-style attribute lists like {: .btn-primary}
    # Convert {: .class} to {.class} for Python markdown
    md_content = re.sub(r'\{:\s*\.([^}]+)\}', r'{.\1}', md_content)

    return markdown.markdown(
        md_content,
        extensions=['fenced_code', 'tables', 'toc', 'nl2br', 'attr_list']
    )


def process_page(file_path):
    """Process a markdown or HTML file with frontmatter"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for frontmatter
    if content.startswith('---'):
        post = frontmatter.loads(content)
        page_data = dict(post.metadata)

        # Render markdown content
        if file_path.suffix == '.md':
            page_data['content'] = render_markdown(post.content)
        else:
            page_data['content'] = post.content
    else:
        page_data = {'content': content if file_path.suffix == '.html' else render_markdown(content)}

    # Get layout (default to 'default')
    layout_name = page_data.get('layout', 'default')

    # Handle layout: none
    if layout_name is None or layout_name == 'none':
        return page_data['content']

    # Load and process layout
    layout = load_layout(layout_name)
    html = process_liquid(layout, page_data)

    return html


@app.route('/')
def index():
    """Serve the homepage"""
    index_md = SITE_ROOT / 'index.md'
    index_html = SITE_ROOT / 'index.html'

    if index_md.exists():
        return process_page(index_md)
    elif index_html.exists():
        return process_page(index_html)
    return '<h1>No index file found</h1>', 404


@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve static assets"""
    return send_from_directory(ASSETS_DIR, filename)


@app.route('/feed.xml')
def serve_feed():
    """Serve RSS feed"""
    feed_path = SITE_ROOT / 'feed.xml'
    if feed_path.exists():
        with open(feed_path, 'r', encoding='utf-8') as f:
            return Response(f.read(), mimetype='application/xml')
    abort(404)


@app.route('/blog/<path:post_slug>')
def serve_post(post_slug):
    """Serve individual blog post"""
    # Try to find matching post file
    posts = load_posts()

    for post in posts:
        # Check if URL matches
        if post['url'] == f'/blog/{post_slug}':
            # Process the post
            page_data = {
                'title': post['title'],
                'date': post['date'],
                'content': render_markdown(post['content']),
                'layout': 'default'
            }

            layout = load_layout('default')
            html = process_liquid(layout, page_data)
            return html

    # Also check _posts directory directly
    for post_file in POSTS_DIR.glob('*.md'):
        if post_slug in post_file.stem:
            return process_page(post_file)

    abort(404)


@app.route('/<path:path>')
def serve_page(path):
    """Serve any page"""
    # Remove trailing slash
    path = path.rstrip('/')

    # Direct file requests (images, etc.)
    direct_path = SITE_ROOT / path
    if direct_path.exists() and direct_path.is_file():
        ext = direct_path.suffix.lower()
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp']:
            return send_from_directory(direct_path.parent, direct_path.name)
        elif ext == '.xml':
            with open(direct_path, 'r', encoding='utf-8') as f:
                return Response(f.read(), mimetype='application/xml')
        elif ext == '.txt':
            return send_from_directory(direct_path.parent, direct_path.name, mimetype='text/plain')
        elif ext == '.pdf':
            return send_from_directory(direct_path.parent, direct_path.name, mimetype='application/pdf')

    # Try different file patterns for pages
    possible_paths = [
        SITE_ROOT / path / 'index.md',
        SITE_ROOT / path / 'index.html',
        SITE_ROOT / f'{path}.md',
        SITE_ROOT / f'{path}.html',
    ]

    for file_path in possible_paths:
        if file_path.exists():
            return process_page(file_path)

    # 404
    four_oh_four = SITE_ROOT / '404.md'
    if four_oh_four.exists():
        return process_page(four_oh_four), 404

    return '<h1>404 - Page Not Found</h1>', 404


@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    four_oh_four = SITE_ROOT / '404.md'
    if four_oh_four.exists():
        return process_page(four_oh_four), 404
    return '<h1>404 - Page Not Found</h1>', 404


if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("Website Tester - Local Preview Server")
    print("=" * 50)
    print(f"\nSite: {SITE['title']}")
    print(f"Root: {SITE_ROOT}")
    print(f"\nOpen your browser to: http://localhost:5001")
    print("\nPress Ctrl+C to stop")
    print("=" * 50 + "\n")

    app.run(debug=True, port=5001, use_reloader=True)
