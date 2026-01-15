# Site Maintenance Guide

Quick reference for maintaining your GitHub Pages site.

## File Structure

```
├── index.md              # Homepage
├── cv/index.md          # CV page
├── blog/index.md        # Blog index
├── 404.md               # Error page
├── _config.yml          # Site configuration
├── _layouts/            # HTML templates
│   └── default.html     # Main layout
├── _includes/           # Reusable components
│   └── analytics.html   # Google Analytics
└── assets/
    ├── css/
    │   └── custom.css   # Your custom styles
    └── images/
        └── avatar.png   # Profile image

```

## Making Changes

### Adding a Blog Post

1. Create a new file in `blog/` folder
2. Name it with date: `2026-01-15-post-title.md`
3. Add front matter:
```yaml
---
title: "Your Post Title"
date: 2026-01-15
---
```

### Updating CV

Edit `cv/index.md` directly. The PDF version is separate - update both when needed.

### Changing Colors

Edit `assets/css/custom.css` and modify the `:root` variables:
- `--primary-color`: Main blue color
- `--primary-hover`: Hover state
- `--primary-light`: Light backgrounds
- `--primary-dark`: Dark text

### Adding Google Analytics

Add to `_config.yml`:
```yaml
google_analytics: UA-XXXXXXXXX-X
```

## Testing Locally

```bash
# Install dependencies (first time only)
bundle install

# Run local server
bundle exec jekyll serve

# View at http://localhost:4000
```

## Common Issues

### Changes not showing up?
- Clear browser cache (Ctrl+Shift+R)
- Wait 1-2 minutes for GitHub Pages to rebuild
- Check GitHub Actions tab for build errors

### Layout looks broken?
- Ensure `custom.css` is loading (check browser console)
- Verify no syntax errors in CSS
- Check responsive design at different screen sizes

### Images not loading?
- Use relative paths: `/assets/images/file.png`
- Check file names are exact (case-sensitive)
- Ensure images are committed to repo

## CSS Organization

The custom.css file is organized in sections:
1. Theme Variables - Colors and spacing
2. Layout Structure - Grid system
3. Header/Sidebar - Left column styling
4. Main Content - Right column styling
5. Typography - Headings and text
6. Components - Links, lists, code blocks
7. Responsive Design - Mobile breakpoints

## Best Practices

- Keep consistent spacing using `var(--spacing-unit)`
- Test on mobile devices (use browser dev tools)
- Add titles to all pages in front matter
- Use semantic HTML in markdown
- Optimize images before uploading (< 500KB)
- Keep navigation consistent across pages

## Resources

- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [GitHub Pages Guide](https://docs.github.com/en/pages)
- [Markdown Cheatsheet](https://www.markdownguide.org/cheat-sheet/)
