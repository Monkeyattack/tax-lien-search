import { toast } from 'react-toastify';

// Store recent toast messages to prevent duplicates
const recentToasts = new Map();
const TOAST_DEBOUNCE_MS = 1000; // 1 second

export const showToast = {
  success: (message) => {
    if (!shouldShowToast(message, 'success')) return;
    return toast.success(message);
  },
  
  error: (message) => {
    if (!shouldShowToast(message, 'error')) return;
    return toast.error(message);
  },
  
  info: (message) => {
    if (!shouldShowToast(message, 'info')) return;
    return toast.info(message);
  },
  
  warning: (message) => {
    if (!shouldShowToast(message, 'warning')) return;
    return toast.warning(message);
  }
};

function shouldShowToast(message, type) {
  const key = `${type}:${message}`;
  const lastShown = recentToasts.get(key);
  const now = Date.now();
  
  if (lastShown && now - lastShown < TOAST_DEBOUNCE_MS) {
    return false;
  }
  
  recentToasts.set(key, now);
  
  // Clean up old entries
  setTimeout(() => {
    recentToasts.delete(key);
  }, TOAST_DEBOUNCE_MS);
  
  return true;
}