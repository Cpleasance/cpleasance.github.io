/**
 * Blog Editor - Enhanced JavaScript
 */

// DOM Elements
const editor = document.getElementById('editor');
const preview = document.getElementById('preview');
const previewPane = document.getElementById('previewPane');
const titleInput = document.getElementById('title');
const titleGroup = document.getElementById('titleGroup');
const tagInput = document.getElementById('tagInput');
const tagsList = document.getElementById('tagsList');
const draftBtn = document.getElementById('draftBtn');
const publishBtn = document.getElementById('publishBtn');
const saveBtn = document.getElementById('saveBtn');
const togglePreview = document.getElementById('togglePreview');
const wordCountEl = document.getElementById('wordCount');
const charCountEl = document.getElementById('charCount');
const postsModal = document.getElementById('postsModal');
const uploadModal = document.getElementById('uploadModal');
const confirmModal = document.getElementById('confirmModal');
const notification = document.getElementById('notification');
const unsavedIndicator = document.getElementById('unsavedIndicator');
const autosaveIndicator = document.getElementById('autosaveIndicator');
const toolbar = document.getElementById('toolbar');
const toolbarExpand = document.getElementById('toolbarExpand');

// State
let tags = [];
let isDraft = true;
let previewVisible = true;
let previewTimeout = null;
let hasUnsavedChanges = false;
let lastSavedContent = '';
let lastSavedTitle = '';
let autoSaveTimeout = null;
let confirmCallback = null;

// Auto-save interval (30 seconds)
const AUTO_SAVE_DELAY = 30000;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initToolbar();
    initTags();
    initStatusToggle();
    initPreview();
    initModals();
    initImageUpload();
    initKeyboardShortcuts();
    initWordCount();
    initUnsavedWarning();
    initToolbarExpand();

    // Show preview by default
    previewPane.classList.add('visible');
    togglePreview.classList.add('active');

    // Store initial state
    lastSavedContent = editor.value;
    lastSavedTitle = titleInput.value;
});

// Unsaved Changes Warning
function initUnsavedWarning() {
    window.addEventListener('beforeunload', (e) => {
        if (hasUnsavedChanges) {
            e.preventDefault();
            e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
            return e.returnValue;
        }
    });

    // Track changes
    editor.addEventListener('input', markAsUnsaved);
    titleInput.addEventListener('input', markAsUnsaved);
}

function markAsUnsaved() {
    const currentContent = editor.value;
    const currentTitle = titleInput.value;

    if (currentContent !== lastSavedContent || currentTitle !== lastSavedTitle) {
        hasUnsavedChanges = true;
        unsavedIndicator.classList.add('visible');

        // Schedule auto-save for drafts
        if (isDraft && currentTitle.trim()) {
            scheduleAutoSave();
        }
    } else {
        hasUnsavedChanges = false;
        unsavedIndicator.classList.remove('visible');
    }
}

function markAsSaved() {
    hasUnsavedChanges = false;
    lastSavedContent = editor.value;
    lastSavedTitle = titleInput.value;
    unsavedIndicator.classList.remove('visible');
    clearTimeout(autoSaveTimeout);
}

// Auto-save
function scheduleAutoSave() {
    clearTimeout(autoSaveTimeout);
    autoSaveTimeout = setTimeout(async () => {
        if (hasUnsavedChanges && isDraft && titleInput.value.trim()) {
            await autoSave();
        }
    }, AUTO_SAVE_DELAY);
}

async function autoSave() {
    const autosaveText = autosaveIndicator.querySelector('.autosave-text');

    autosaveIndicator.classList.add('visible', 'saving');
    autosaveText.textContent = 'Saving...';

    try {
        const response = await fetch('/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: titleInput.value.trim(),
                content: editor.value.trim(),
                tags,
                is_draft: true
            })
        });

        const data = await response.json();

        if (!data.error) {
            markAsSaved();
            autosaveIndicator.classList.remove('saving');
            autosaveIndicator.classList.add('saved');
            autosaveText.textContent = 'Auto-saved';

            setTimeout(() => {
                autosaveIndicator.classList.remove('visible');
            }, 2000);
        }
    } catch (error) {
        autosaveIndicator.classList.remove('visible', 'saving');
    }
}

// Toolbar Expand (mobile)
function initToolbarExpand() {
    toolbarExpand.addEventListener('click', () => {
        toolbar.classList.toggle('expanded');
        toolbarExpand.textContent = toolbar.classList.contains('expanded') ? 'Less' : 'More';
    });
}

// Toolbar Actions
function initToolbar() {
    document.querySelectorAll('.tool-btn[data-action]').forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.action;
            handleToolbarAction(action);
        });
    });
}

function handleToolbarAction(action) {
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const text = editor.value;
    const selected = text.substring(start, end);

    let replacement = '';
    let cursorOffset = 0;

    switch (action) {
        case 'h1':
            replacement = `# ${selected || 'Heading 1'}`;
            cursorOffset = selected ? 0 : -9;
            break;
        case 'h2':
            replacement = `## ${selected || 'Heading 2'}`;
            cursorOffset = selected ? 0 : -9;
            break;
        case 'h3':
            replacement = `### ${selected || 'Heading 3'}`;
            cursorOffset = selected ? 0 : -9;
            break;
        case 'bold':
            replacement = `**${selected || 'bold text'}**`;
            cursorOffset = selected ? 0 : -11;
            break;
        case 'italic':
            replacement = `*${selected || 'italic text'}*`;
            cursorOffset = selected ? 0 : -12;
            break;
        case 'strikethrough':
            replacement = `~~${selected || 'strikethrough'}~~`;
            cursorOffset = selected ? 0 : -15;
            break;
        case 'link':
            if (selected) {
                replacement = `[${selected}](url)`;
                cursorOffset = -1;
            } else {
                replacement = '[link text](url)';
                cursorOffset = -1;
            }
            break;
        case 'image':
            replacement = `![${selected || 'alt text'}](image-url)`;
            cursorOffset = selected ? -1 : -10;
            break;
        case 'upload':
            openUploadModal();
            return;
        case 'code':
            replacement = `\`${selected || 'code'}\``;
            cursorOffset = selected ? 0 : -5;
            break;
        case 'codeblock':
            replacement = `\`\`\`\n${selected || 'code here'}\n\`\`\``;
            cursorOffset = selected ? 0 : -12;
            break;
        case 'quote':
            replacement = `> ${selected || 'quote'}`;
            cursorOffset = selected ? 0 : -5;
            break;
        case 'ul':
            if (selected) {
                replacement = selected.split('\n').map(line => `- ${line}`).join('\n');
            } else {
                replacement = '- list item';
                cursorOffset = -9;
            }
            break;
        case 'ol':
            if (selected) {
                replacement = selected.split('\n').map((line, i) => `${i + 1}. ${line}`).join('\n');
            } else {
                replacement = '1. list item';
                cursorOffset = -9;
            }
            break;
        case 'hr':
            replacement = '\n---\n';
            break;
        default:
            return;
    }

    editor.focus();
    editor.setRangeText(replacement, start, end, 'end');

    if (cursorOffset !== 0) {
        const newPos = editor.selectionEnd + cursorOffset;
        editor.setSelectionRange(newPos, newPos);
    }

    updatePreview();
    updateWordCount();
    markAsUnsaved();
}

// Tags
function initTags() {
    tagInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            const tag = tagInput.value.trim();
            if (tag && !tags.includes(tag)) {
                tags.push(tag);
                renderTags();
                showNotification('Tag added', `"${tag}" has been added`, 'success');
                markAsUnsaved();
            } else if (tags.includes(tag)) {
                showNotification('Duplicate tag', `"${tag}" already exists`, 'warning');
            }
            tagInput.value = '';
        }
    });
}

function renderTags() {
    tagsList.innerHTML = tags.map(tag => `
        <span class="tag" data-tag="${escapeHtml(tag)}">
            ${escapeHtml(tag)}
            <span class="tag-remove" data-tag="${escapeHtml(tag)}">&times;</span>
        </span>
    `).join('');

    // Add remove listeners
    tagsList.querySelectorAll('.tag-remove').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const tagToRemove = btn.dataset.tag;
            const tagEl = btn.closest('.tag');

            // Add removing animation
            tagEl.classList.add('removing');

            setTimeout(() => {
                tags = tags.filter(t => t !== tagToRemove);
                renderTags();
                markAsUnsaved();
            }, 200);
        });
    });
}

// Status Toggle with Confirmation
function initStatusToggle() {
    draftBtn.addEventListener('click', () => {
        if (!isDraft) {
            showConfirm(
                'Switch to Draft?',
                'This will move the post back to drafts when saved.',
                () => {
                    setStatus(true);
                    showNotification('Status changed', 'Post will be saved as draft', 'success');
                }
            );
        }
    });

    publishBtn.addEventListener('click', () => {
        if (isDraft) {
            showConfirm(
                'Publish Post?',
                'This will make the post visible on your blog when saved.',
                () => {
                    setStatus(false);
                    showNotification('Status changed', 'Post will be published when saved', 'success');
                }
            );
        }
    });
}

function setStatus(draft) {
    isDraft = draft;
    if (draft) {
        draftBtn.classList.add('active');
        publishBtn.classList.remove('active');
    } else {
        publishBtn.classList.add('active');
        draftBtn.classList.remove('active');
    }
    markAsUnsaved();
}

// Confirmation Modal
function showConfirm(title, message, onConfirm) {
    document.getElementById('confirmTitle').textContent = title;
    document.getElementById('confirmMessage').textContent = message;
    document.getElementById('confirmIcon').textContent = '?';
    confirmCallback = onConfirm;
    confirmModal.classList.add('visible');
}

function initConfirmModal() {
    document.getElementById('closeConfirmModal').addEventListener('click', closeConfirmModal);
    document.getElementById('confirmCancel').addEventListener('click', closeConfirmModal);
    document.getElementById('confirmOk').addEventListener('click', () => {
        if (confirmCallback) {
            confirmCallback();
        }
        closeConfirmModal();
    });

    confirmModal.addEventListener('click', (e) => {
        if (e.target === confirmModal) {
            closeConfirmModal();
        }
    });
}

function closeConfirmModal() {
    confirmModal.classList.remove('visible');
    confirmCallback = null;
}

// Preview
function initPreview() {
    togglePreview.addEventListener('click', () => {
        previewVisible = !previewVisible;
        previewPane.classList.toggle('visible', previewVisible);
        togglePreview.classList.toggle('active', previewVisible);

        if (previewVisible) {
            updatePreview();
        }
    });

    editor.addEventListener('input', () => {
        clearTimeout(previewTimeout);
        previewTimeout = setTimeout(updatePreview, 300);
        updateWordCount();
    });
}

async function updatePreview() {
    if (!previewVisible) return;

    try {
        const response = await fetch('/preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: editor.value })
        });

        const data = await response.json();
        preview.innerHTML = data.html || '<p class="empty">Start writing to see preview...</p>';
    } catch (error) {
        console.error('Preview error:', error);
    }
}

// Word Count
function initWordCount() {
    updateWordCount();
}

function updateWordCount() {
    const text = editor.value;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    const chars = text.length;

    wordCountEl.textContent = `${words} word${words !== 1 ? 's' : ''}`;
    charCountEl.textContent = `${chars} character${chars !== 1 ? 's' : ''}`;
}

// Modals
function initModals() {
    // Load Posts Modal
    document.getElementById('loadPostsBtn').addEventListener('click', openPostsModal);
    document.getElementById('closeModal').addEventListener('click', () => {
        postsModal.classList.remove('visible');
    });

    // New Post with unsaved check
    document.getElementById('newPostBtn').addEventListener('click', () => {
        if (hasUnsavedChanges) {
            showConfirm(
                'Discard changes?',
                'You have unsaved changes. Create a new post anyway?',
                clearEditor
            );
        } else {
            clearEditor();
        }
    });

    // Close modals on backdrop click
    [postsModal, uploadModal].forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('visible');
            }
        });
    });

    // Initialize confirm modal
    initConfirmModal();

    // Save
    saveBtn.addEventListener('click', savePost);
}

async function openPostsModal() {
    try {
        const response = await fetch('/posts');
        const data = await response.json();

        const draftsList = document.getElementById('draftsList');
        const publishedList = document.getElementById('publishedList');

        if (data.drafts.length === 0) {
            draftsList.innerHTML = '<li class="empty">No drafts</li>';
        } else {
            draftsList.innerHTML = data.drafts.map(post =>
                `<li data-filename="${post.filename}">${post.filename}</li>`
            ).join('');
        }

        if (data.posts.length === 0) {
            publishedList.innerHTML = '<li class="empty">No published posts</li>';
        } else {
            publishedList.innerHTML = data.posts.map(post =>
                `<li data-filename="${post.filename}">${post.filename}</li>`
            ).join('');
        }

        // Add click handlers
        document.querySelectorAll('.posts-list li[data-filename]').forEach(li => {
            li.addEventListener('click', () => {
                if (hasUnsavedChanges) {
                    showConfirm(
                        'Discard changes?',
                        'You have unsaved changes. Load another post anyway?',
                        () => loadPost(li.dataset.filename)
                    );
                } else {
                    loadPost(li.dataset.filename);
                }
            });
        });

        postsModal.classList.add('visible');
    } catch (error) {
        showNotification('Error', 'Failed to load posts', 'error');
    }
}

async function loadPost(filename) {
    try {
        const response = await fetch(`/load/${filename}`);
        const data = await response.json();

        if (data.error) {
            showNotification('Error', data.error, 'error');
            return;
        }

        titleInput.value = data.title;
        editor.value = data.content;
        tags = data.tags || [];
        isDraft = data.is_draft;

        renderTags();
        setStatus(isDraft);

        // Clear validation errors
        titleGroup.classList.remove('error');

        updatePreview();
        updateWordCount();
        postsModal.classList.remove('visible');

        // Update saved state
        markAsSaved();

        showNotification('Post loaded', `"${data.title}" is ready to edit`, 'success');
    } catch (error) {
        showNotification('Error', 'Failed to load post', 'error');
    }
}

// Form Validation
function validateForm() {
    let isValid = true;

    // Title validation
    if (!titleInput.value.trim()) {
        titleGroup.classList.add('error');
        titleInput.focus();
        isValid = false;
    } else {
        titleGroup.classList.remove('error');
    }

    return isValid;
}

// Clear validation on input
titleInput.addEventListener('input', () => {
    if (titleInput.value.trim()) {
        titleGroup.classList.remove('error');
    }
});

async function savePost() {
    // Validate
    if (!validateForm()) {
        showNotification('Validation Error', 'Please fill in all required fields', 'error');
        return;
    }

    const content = editor.value.trim();
    if (!content) {
        showNotification('Validation Error', 'Please enter some content', 'error');
        editor.focus();
        return;
    }

    // Show saving state
    saveBtn.classList.add('saving');
    saveBtn.disabled = true;

    try {
        const response = await fetch('/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: titleInput.value.trim(),
                content,
                tags,
                is_draft: isDraft
            })
        });

        const data = await response.json();

        if (data.error) {
            showNotification('Error', data.error, 'error');
            return;
        }

        markAsSaved();

        const status = isDraft ? 'draft' : 'published';
        showNotification(
            'Post Saved!',
            `Your post has been saved as ${status}`,
            'success'
        );
    } catch (error) {
        showNotification('Error', 'Failed to save post', 'error');
    } finally {
        saveBtn.classList.remove('saving');
        saveBtn.disabled = false;
    }
}

function clearEditor() {
    titleInput.value = '';
    editor.value = '';
    tags = [];
    isDraft = true;

    renderTags();
    setStatus(true);
    titleGroup.classList.remove('error');
    updatePreview();
    updateWordCount();
    markAsSaved();

    showNotification('New Post', 'Editor cleared for a new post', 'success');
}

// Image Upload
function initImageUpload() {
    const uploadZone = document.getElementById('uploadZone');
    const imageInput = document.getElementById('imageInput');
    const uploadStatus = document.getElementById('uploadStatus');

    document.getElementById('closeUploadModal').addEventListener('click', () => {
        uploadModal.classList.remove('visible');
        uploadStatus.className = 'upload-status';
        uploadStatus.textContent = '';
        uploadZone.classList.remove('uploading');
    });

    // Drag and drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');

        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            uploadImage(file);
        } else {
            showNotification('Invalid File', 'Please drop an image file', 'error');
        }
    });

    // File input
    imageInput.addEventListener('change', () => {
        const file = imageInput.files[0];
        if (file) {
            uploadImage(file);
        }
    });
}

function openUploadModal() {
    uploadModal.classList.add('visible');
    document.getElementById('uploadStatus').className = 'upload-status';
    document.getElementById('uploadStatus').textContent = '';
    document.getElementById('imageInput').value = '';
    document.getElementById('uploadZone').classList.remove('uploading');
}

async function uploadImage(file) {
    const uploadZone = document.getElementById('uploadZone');
    const uploadStatus = document.getElementById('uploadStatus');

    // Show loading state
    uploadZone.classList.add('uploading');

    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        uploadZone.classList.remove('uploading');

        if (data.error) {
            uploadStatus.textContent = data.error;
            uploadStatus.className = 'upload-status error';
            return;
        }

        // Insert markdown at cursor
        const start = editor.selectionStart;
        editor.setRangeText(data.markdown + '\n', start, start, 'end');

        uploadStatus.textContent = `Uploaded: ${data.filename}`;
        uploadStatus.className = 'upload-status success';

        updatePreview();
        markAsUnsaved();

        // Close modal after short delay
        setTimeout(() => {
            uploadModal.classList.remove('visible');
        }, 1000);
    } catch (error) {
        uploadZone.classList.remove('uploading');
        uploadStatus.textContent = 'Upload failed';
        uploadStatus.className = 'upload-status error';
    }
}

// Keyboard Shortcuts
function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Only handle shortcuts when not in a modal
        const inModal = postsModal.classList.contains('visible') ||
                       uploadModal.classList.contains('visible') ||
                       confirmModal.classList.contains('visible');

        // Ctrl/Cmd + S = Save (global)
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            savePost();
            return;
        }

        // Ctrl/Cmd + P = Toggle Preview (global)
        if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
            e.preventDefault();
            togglePreview.click();
            return;
        }

        // Rest only when focused on editor
        if (document.activeElement !== editor) return;

        // Ctrl/Cmd + B = Bold
        if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
            e.preventDefault();
            handleToolbarAction('bold');
        }

        // Ctrl/Cmd + I = Italic
        if ((e.ctrlKey || e.metaKey) && e.key === 'i') {
            e.preventDefault();
            handleToolbarAction('italic');
        }

        // Ctrl/Cmd + K = Link
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            handleToolbarAction('link');
        }

        // Ctrl/Cmd + Shift + S = Strikethrough
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'S') {
            e.preventDefault();
            handleToolbarAction('strikethrough');
        }

        // Ctrl/Cmd + ` = Inline code
        if ((e.ctrlKey || e.metaKey) && e.key === '`') {
            e.preventDefault();
            if (e.shiftKey) {
                handleToolbarAction('codeblock');
            } else {
                handleToolbarAction('code');
            }
        }

        // Ctrl/Cmd + Shift + Q = Quote
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'Q') {
            e.preventDefault();
            handleToolbarAction('quote');
        }

        // Tab = Insert spaces
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = editor.selectionStart;
            editor.setRangeText('    ', start, start, 'end');
            markAsUnsaved();
        }
    });
}

// Enhanced Notification
function showNotification(title, message, type = 'success') {
    const iconEl = notification.querySelector('.notification-icon');
    const titleEl = notification.querySelector('.notification-title');
    const messageEl = notification.querySelector('.notification-message');

    // Set icon based on type
    const icons = {
        success: '✓',
        error: '✕',
        warning: '!'
    };

    iconEl.textContent = icons[type] || '';
    titleEl.textContent = title;
    messageEl.textContent = message;

    notification.className = `notification ${type} visible`;

    setTimeout(() => {
        notification.classList.remove('visible');
    }, 4000);
}

// Utility
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
