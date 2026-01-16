// Simple Text Annotation System for CloudBase
(function() {
  'use strict';

  // ============================================
  // CONFIGURATION - CloudBase Environment ID
  // ============================================
  const ENV_ID = 'test-3gop834c099077bf';

  // ============================================
  // State
  // ============================================
  let db = null;
  let annotations = [];
  let currentPopup = null;
  let currentTooltip = null;
  let addButton = null;

  // ============================================
  // CloudBase Initialization
  // ============================================
  function initCloudBase() {
    if (typeof cloudbase === 'undefined') {
      console.error('CloudBase SDK not loaded. Make sure cloudbase.full.js is included.');
      showNotification('Annotation system failed to load', true);
      return Promise.reject(new Error('CloudBase SDK not loaded'));
    }

    console.log('Initializing CloudBase with ENV_ID:', ENV_ID);
    const app = cloudbase.init({ env: ENV_ID });

    // Enable anonymous login for public commenting
    const auth = app.auth();
    return auth.signInAnonymously().then(() => {
      console.log('Anonymous login successful');
      db = app.database();
      console.log('CloudBase connected, loading annotations...');
      return loadAnnotations();
    }).catch(err => {
      console.error('Anonymous login failed:', err);
      showNotification('Failed to connect to comment system', true);
      throw err;
    });
  }

  // ============================================
  // Database Operations
  // ============================================
  function loadAnnotations() {
    return db.collection('annotations')
      .where({ uri: window.location.pathname })
      .orderBy('createdAt', 'desc')
      .limit(100)
      .get()
      .then(result => {
        annotations = result.data || [];
        console.log('Loaded', annotations.length, 'annotations');
        renderAnnotations();
      })
      .catch(err => {
        console.error('Failed to load annotations:', err);
        annotations = [];
      });
  }

  function saveAnnotation(quote, comment, rangeData) {
    console.log('Saving annotation for quote:', quote.substring(0, 50) + '...');

    const newAnnotation = {
      quote: quote,
      comment: comment,
      uri: window.location.pathname,
      rangeData: rangeData,
      createdAt: new Date()
    };

    return db.collection('annotations').add(newAnnotation)
      .then(result => {
        console.log('Database save successful, ID:', result.id);
        // Add to local cache with the returned ID
        annotations.unshift({
          _id: result.id,
          ...newAnnotation
        });
        console.log('Total annotations now:', annotations.length);
        renderAnnotations();
        console.log('Render complete');

        // Show success notification
        showNotification('Comment saved successfully!');
      })
      .catch(err => {
        console.error('Failed to save annotation:', err);
        showNotification('Failed to save comment: ' + err.message, true);
      });
  }

  // ============================================
  // Rendering
  // ============================================
  function renderAnnotations() {
    console.log('Rendering', annotations.length, 'annotations');
    // Remove existing highlights first
    removeAllHighlights();

    // Apply highlights for each annotation
    annotations.forEach((ann, index) => {
      try {
        const success = highlightText(ann.quote, ann._id, ann.comment);
        console.log('Highlight #' + index + ':', success ? 'SUCCESS' : 'NOT FOUND', '-', ann.quote.substring(0, 30) + '...');
      } catch (e) {
        console.warn('Could not highlight text:', ann.quote.substring(0, 30) + '...', e.message);
      }
    });
  }

  function removeAllHighlights() {
    document.querySelectorAll('.annotation-highlight').forEach(el => {
      const parent = el.parentNode;
      if (parent) {
        // Move all children out of the highlight span
        while (el.firstChild) {
          parent.insertBefore(el.firstChild, el);
        }
        parent.removeChild(el);
        // Normalize to merge adjacent text nodes
        parent.normalize();
      }
    });
  }

  function highlightText(searchText, annotationId, comment) {
    // Normalize search text (collapse whitespace)
    const normalizedSearch = searchText.replace(/\s+/g, ' ').trim();

    // Find the main content container
    const container = document.querySelector('.container') ||
                      document.querySelector('main') ||
                      document.querySelector('article') ||
                      document.body;

    // Build a list of all text nodes with their positions
    const textNodes = [];
    let combinedText = '';

    const walker = document.createTreeWalker(
      container,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode: function(node) {
          const parent = node.parentElement;
          if (!parent) return NodeFilter.FILTER_REJECT;

          const tagName = parent.tagName.toLowerCase();
          if (tagName === 'script' || tagName === 'style' || tagName === 'noscript') {
            return NodeFilter.FILTER_REJECT;
          }
          if (parent.classList.contains('annotation-highlight') ||
              parent.classList.contains('annotation-popup') ||
              parent.classList.contains('annotation-tooltip')) {
            return NodeFilter.FILTER_REJECT;
          }

          return NodeFilter.FILTER_ACCEPT;
        }
      }
    );

    let node;
    while (node = walker.nextNode()) {
      textNodes.push({
        node: node,
        start: combinedText.length,
        end: combinedText.length + node.textContent.length
      });
      combinedText += node.textContent;
    }

    // Search in combined text (try exact first, then normalized)
    let matchStart = combinedText.indexOf(searchText);
    let matchEnd = matchStart + searchText.length;

    // If exact match fails, try normalized
    if (matchStart === -1) {
      const normalizedCombined = combinedText.replace(/\s+/g, ' ');
      const normalizedMatchStart = normalizedCombined.indexOf(normalizedSearch);

      if (normalizedMatchStart !== -1) {
        // Map normalized position back to original
        let origPos = 0;
        let normPos = 0;
        while (normPos < normalizedMatchStart && origPos < combinedText.length) {
          if (/\s/.test(combinedText[origPos])) {
            while (origPos < combinedText.length && /\s/.test(combinedText[origPos])) origPos++;
            normPos++;
          } else {
            origPos++;
            normPos++;
          }
        }
        matchStart = origPos;

        // Find end position
        let endOrigPos = origPos;
        let endNormPos = 0;
        while (endNormPos < normalizedSearch.length && endOrigPos < combinedText.length) {
          if (/\s/.test(combinedText[endOrigPos])) {
            while (endOrigPos < combinedText.length && /\s/.test(combinedText[endOrigPos])) endOrigPos++;
            endNormPos++;
          } else {
            endOrigPos++;
            endNormPos++;
          }
        }
        matchEnd = endOrigPos;
      }
    }

    if (matchStart === -1) {
      return false;
    }

    // Find which text nodes are involved
    const affectedNodes = textNodes.filter(tn =>
      tn.start < matchEnd && tn.end > matchStart
    );

    if (affectedNodes.length === 0) {
      return false;
    }

    // For single node, use simple approach
    if (affectedNodes.length === 1) {
      const tn = affectedNodes[0];
      const localStart = matchStart - tn.start;
      const localEnd = matchEnd - tn.start;

      try {
        const range = document.createRange();
        range.setStart(tn.node, localStart);
        range.setEnd(tn.node, Math.min(localEnd, tn.node.textContent.length));

        const highlight = document.createElement('span');
        highlight.className = 'annotation-highlight';
        highlight.dataset.annotationId = annotationId;
        highlight.dataset.comment = comment;

        range.surroundContents(highlight);
        return true;
      } catch (e) {
        console.warn('Single node highlight failed:', e.message);
      }
    }

    // For multiple nodes, wrap each part separately
    try {
      // Process in reverse order to avoid position shifts
      for (let i = affectedNodes.length - 1; i >= 0; i--) {
        const tn = affectedNodes[i];
        const localStart = Math.max(0, matchStart - tn.start);
        const localEnd = Math.min(tn.node.textContent.length, matchEnd - tn.start);

        if (localEnd <= localStart) continue;

        const range = document.createRange();
        range.setStart(tn.node, localStart);
        range.setEnd(tn.node, localEnd);

        const highlight = document.createElement('span');
        highlight.className = 'annotation-highlight';
        highlight.dataset.annotationId = annotationId;
        highlight.dataset.comment = comment;

        try {
          range.surroundContents(highlight);
        } catch (e) {
          // If surroundContents fails, try extracting and wrapping
          const fragment = range.extractContents();
          highlight.appendChild(fragment);
          range.insertNode(highlight);
        }
      }
      return true;
    } catch (e) {
      console.warn('Multi-node highlight failed:', e.message);
      return false;
    }
  }

  // ============================================
  // UI Components
  // ============================================
  function showAddButton(x, y, selectedText) {
    hideAddButton();

    addButton = document.createElement('button');
    addButton.className = 'annotation-add-btn';
    addButton.textContent = '+ Add Comment';
    addButton.style.left = x + 'px';
    addButton.style.top = y + 'px';

    addButton.onclick = function(e) {
      e.preventDefault();
      e.stopPropagation();

      const selection = window.getSelection();
      showAddPopup(x, y + 25, selectedText);
      selection.removeAllRanges();
    };

    document.body.appendChild(addButton);
  }

  function hideAddButton() {
    if (addButton) {
      addButton.remove();
      addButton = null;
    }
  }

  function showAddPopup(x, y, selectedText) {
    hidePopup();

    const popup = document.createElement('div');
    popup.className = 'annotation-popup';

    // Truncate displayed text
    const displayText = selectedText.length > 50
      ? selectedText.substring(0, 50) + '...'
      : selectedText;

    popup.innerHTML = `
      <div style="font-size: 12px; color: #666; margin-bottom: 8px; font-style: italic;">
        "${displayText}"
      </div>
      <textarea placeholder="Add your comment..."></textarea>
      <div class="annotation-popup-buttons">
        <button class="cancel-btn">Cancel</button>
        <button class="save-btn">Save</button>
      </div>
    `;

    // Position popup, but keep it within viewport
    const viewportWidth = window.innerWidth;
    const popupWidth = 300;

    let posX = x;
    if (posX + popupWidth > viewportWidth - 20) {
      posX = viewportWidth - popupWidth - 20;
    }
    if (posX < 20) posX = 20;

    popup.style.left = posX + 'px';
    popup.style.top = y + 'px';

    document.body.appendChild(popup);
    currentPopup = popup;

    const textarea = popup.querySelector('textarea');
    textarea.focus({ preventScroll: true });

    // Handle Enter key to save
    textarea.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        saveAndClose();
      }
      if (e.key === 'Escape') {
        hidePopup();
      }
    });

    function saveAndClose() {
      const comment = textarea.value.trim();
      if (comment) {
        saveAnnotation(selectedText, comment, {});
      }
      hidePopup();
    }

    popup.querySelector('.save-btn').onclick = saveAndClose;
    popup.querySelector('.cancel-btn').onclick = hidePopup;
  }

  function hidePopup() {
    if (currentPopup) {
      currentPopup.remove();
      currentPopup = null;
    }
    hideAddButton();
  }

  function showTooltip(element, x, y) {
    hideTooltip();

    const comment = element.dataset.comment;
    if (!comment) return;

    const tooltip = document.createElement('div');
    tooltip.className = 'annotation-tooltip';
    tooltip.textContent = comment;

    // Position tooltip below the highlight
    let posX = x;
    let posY = y + 10;

    // Keep within viewport
    const viewportWidth = window.innerWidth;
    const tooltipWidth = 250;

    if (posX + tooltipWidth > viewportWidth - 20) {
      posX = viewportWidth - tooltipWidth - 20;
    }
    if (posX < 20) posX = 20;

    tooltip.style.left = posX + 'px';
    tooltip.style.top = posY + 'px';

    document.body.appendChild(tooltip);
    currentTooltip = tooltip;
  }

  function hideTooltip() {
    if (currentTooltip) {
      currentTooltip.remove();
      currentTooltip = null;
    }
  }

  function showNotification(message, isError = false) {
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: ${isError ? '#ef4444' : '#10b981'};
      color: white;
      padding: 12px 20px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.2);
      z-index: 10002;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 14px;
      animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
      notification.style.opacity = '0';
      notification.style.transition = 'opacity 0.3s';
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }

  // ============================================
  // Event Handlers
  // ============================================
  function handleSelection(e) {
    const selection = window.getSelection();
    const selectedText = selection.toString().trim();

    // Only show button for reasonable text selections
    if (selectedText.length > 3 && selectedText.length < 500) {
      try {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();

        showAddButton(
          rect.left + window.scrollX,
          rect.bottom + window.scrollY + 5,
          selectedText
        );
      } catch (e) {
        console.warn('Could not get selection range:', e);
      }
    }
  }

  function handleDocumentClick(e) {
    // Hide add button when clicking elsewhere
    if (addButton && !addButton.contains(e.target)) {
      hideAddButton();
    }

    // Hide popup when clicking outside
    if (currentPopup && !currentPopup.contains(e.target)) {
      hidePopup();
    }
  }

  function handleHighlightHover(e) {
    if (e.target.classList.contains('annotation-highlight')) {
      const rect = e.target.getBoundingClientRect();
      showTooltip(
        e.target,
        rect.left + window.scrollX,
        rect.bottom + window.scrollY
      );
    }
  }

  function handleHighlightLeave(e) {
    if (e.target.classList.contains('annotation-highlight')) {
      hideTooltip();
    }
  }

  // ============================================
  // Initialization
  // ============================================
  function init() {
    // Check if ENV_ID is configured
    if (ENV_ID === 'YOUR_ENV_ID') {
      console.warn('Annotation system: Please configure ENV_ID in lib/annotation.js');
      return;
    }

    initCloudBase()
      .then(() => {
        console.log('Annotation system initialized successfully');
      })
      .catch(err => {
        console.error('Failed to initialize annotation system:', err);
      });

    // Text selection handler
    document.addEventListener('mouseup', function(e) {
      // Small delay to allow selection to complete
      setTimeout(() => handleSelection(e), 10);
    });

    // Click handler for dismissing UI
    document.addEventListener('mousedown', handleDocumentClick);

    // Hover handlers for tooltips
    document.addEventListener('mouseover', handleHighlightHover);
    document.addEventListener('mouseout', handleHighlightLeave);
  }

  // Start when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
