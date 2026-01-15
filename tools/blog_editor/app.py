"""
Blog Editor - A local Flask app for writing Jekyll blog posts
"""

import os
import re
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from slugify import slugify
from werkzeug.utils import secure_filename
import markdown

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Paths relative to the Jekyll site (tools/blog_editor -> site root)
SITE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POSTS_DIR = os.path.join(SITE_ROOT, '_posts')
DRAFTS_DIR = os.path.join(SITE_ROOT, '_drafts')
IMAGES_DIR = os.path.join(SITE_ROOT, 'assets', 'images', 'blog')

# Ensure directories exist
os.makedirs(POSTS_DIR, exist_ok=True)
os.makedirs(DRAFTS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def editor():
    """Main editor page"""
    return render_template('editor.html')


@app.route('/preview', methods=['POST'])
def preview():
    """Convert markdown to HTML for preview"""
    content = request.json.get('content', '')
    html = markdown.markdown(
        content,
        extensions=['fenced_code', 'tables', 'toc', 'nl2br']
    )
    return jsonify({'html': html})


@app.route('/save', methods=['POST'])
def save_post():
    """Save post as Jekyll markdown file"""
    data = request.json

    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    tags = data.get('tags', [])
    is_draft = data.get('is_draft', False)

    if not title:
        return jsonify({'error': 'Title is required'}), 400
    if not content:
        return jsonify({'error': 'Content is required'}), 400

    # Generate filename
    date_str = datetime.now().strftime('%Y-%m-%d')
    slug = slugify(title)
    filename = f"{date_str}-{slug}.md"

    # Choose directory based on draft status
    target_dir = DRAFTS_DIR if is_draft else POSTS_DIR
    filepath = os.path.join(target_dir, filename)

    # Build frontmatter
    frontmatter = [
        '---',
        f'title: "{title}"',
        f'date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
    ]

    if tags:
        tags_str = ', '.join(tags)
        frontmatter.append(f'tags: [{tags_str}]')

    frontmatter.append('---')
    frontmatter.append('')

    # Combine frontmatter and content
    full_content = '\n'.join(frontmatter) + content

    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_content)

    status = 'draft' if is_draft else 'published'
    return jsonify({
        'success': True,
        'message': f'Post saved as {status}',
        'filename': filename,
        'path': filepath
    })


@app.route('/upload', methods=['POST'])
def upload_image():
    """Handle image upload"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    # Secure the filename and add timestamp to avoid conflicts
    original_name = secure_filename(file.filename)
    name, ext = os.path.splitext(original_name)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{name}_{timestamp}{ext}"

    filepath = os.path.join(IMAGES_DIR, filename)
    file.save(filepath)

    # Return the markdown-ready path
    markdown_path = f"/assets/images/blog/{filename}"

    return jsonify({
        'success': True,
        'filename': filename,
        'markdown': f"![{name}]({markdown_path})",
        'path': markdown_path
    })


@app.route('/posts', methods=['GET'])
def list_posts():
    """List existing posts and drafts"""
    posts = []
    drafts = []

    # Get published posts
    if os.path.exists(POSTS_DIR):
        for filename in os.listdir(POSTS_DIR):
            if filename.endswith('.md'):
                posts.append({
                    'filename': filename,
                    'path': os.path.join(POSTS_DIR, filename),
                    'status': 'published'
                })

    # Get drafts
    if os.path.exists(DRAFTS_DIR):
        for filename in os.listdir(DRAFTS_DIR):
            if filename.endswith('.md'):
                drafts.append({
                    'filename': filename,
                    'path': os.path.join(DRAFTS_DIR, filename),
                    'status': 'draft'
                })

    return jsonify({'posts': posts, 'drafts': drafts})


@app.route('/load/<path:filename>', methods=['GET'])
def load_post(filename):
    """Load an existing post for editing"""
    # Check both directories
    for directory in [POSTS_DIR, DRAFTS_DIR]:
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse frontmatter
            match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
            if match:
                frontmatter_str = match.group(1)
                body = match.group(2)

                # Extract title
                title_match = re.search(r'title:\s*["\']?(.+?)["\']?\s*$', frontmatter_str, re.MULTILINE)
                title = title_match.group(1) if title_match else ''

                # Extract tags
                tags_match = re.search(r'tags:\s*\[(.+?)\]', frontmatter_str)
                tags = [t.strip() for t in tags_match.group(1).split(',')] if tags_match else []

                is_draft = directory == DRAFTS_DIR

                return jsonify({
                    'title': title,
                    'content': body.strip(),
                    'tags': tags,
                    'is_draft': is_draft
                })

    return jsonify({'error': 'Post not found'}), 404


if __name__ == '__main__':
    print("\n" + "="*50)
    print("Blog Editor Running!")
    print("="*50)
    print(f"\nOpen your browser to: http://localhost:5000")
    print(f"\nPosts will be saved to: {POSTS_DIR}")
    print(f"Drafts will be saved to: {DRAFTS_DIR}")
    print(f"Images will be saved to: {IMAGES_DIR}")
    print("\nPress Ctrl+C to stop the server")
    print("="*50 + "\n")

    app.run(debug=True, port=5000)
