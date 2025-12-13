// @ts-check

let zoomInstance = null;

/**
 * Initialize medium-zoom for image messages only
 */
export function initImageZoom() {
  if (zoomInstance) {
    return zoomInstance;
  }

  // medium-zoom is loaded as a global UMD module
  // @ts-ignore
  if (typeof window.mediumZoom === "undefined") {
    console.warn("medium-zoom library not loaded");
    return null;
  }

  // Initialize with no selector - we'll attach manually
  // @ts-ignore
  zoomInstance = window.mediumZoom({
    margin: 24,
    background: "rgba(0, 0, 0, 0.9)",
    scrollOffset: 0,
  });

  return zoomInstance;
}

/**
 * Attach zoom to a specific image message element
 * @param {HTMLImageElement} img - The image element to make zoomable
 */
export function attachZoomToImage(img) {
  if (!zoomInstance) {
    initImageZoom();
  }

  if (!zoomInstance) return;

  // Only attach if it's an image inside a message-bubble with message-image class
  const bubble = img.closest(".message-bubble.message-image");
  if (bubble && img.parentElement === bubble) {
    zoomInstance.attach(img);
  }
}

/**
 * Attach zoom to all image messages in a container
 * @param {HTMLElement} container - The container with message elements
 */
export function attachZoomToContainer(container) {
  if (!zoomInstance) {
    initImageZoom();
  }

  if (!zoomInstance) return;

  // Select only images that are direct children of .message-bubble.message-image
  const imageMessages = container.querySelectorAll(".message-bubble.message-image > img");
  if (imageMessages.length > 0) {
    zoomInstance.attach(imageMessages);
  }
}
