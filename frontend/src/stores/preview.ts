import { defineStore } from 'pinia';
import { ref } from 'vue';

export const usePreviewStore = defineStore('preview', () => {
  const isVisible = ref(false);
  const url = ref<string | null>(null);
  const fileType = ref<string | null>(null);
  const fileName = ref<string | null>('File Preview');
  const error = ref<string | null>(null);

  function show(newUrl: string, newFileType: string, newFileName?: string) {
    isVisible.value = true;
    url.value = newUrl;
    fileType.value = newFileType.toLowerCase();
    fileName.value = newFileName || 'File Preview';
    error.value = null;
  }

  function showError(message: string) {
    isVisible.value = true;
    url.value = null;
    fileType.value = 'error';
    fileName.value = 'Error';
    error.value = message;
  }

  function hide() {
    isVisible.value = false;
    // Revoke the object URL to free up memory
    if (url.value && url.value.startsWith('blob:')) {
      window.URL.revokeObjectURL(url.value);
    }
    url.value = null;
    fileType.value = null;
    fileName.value = null;
    error.value = null;
  }

  return { 
    // State
    isVisible, 
    url, 
    fileType, 
    fileName, 
    error, 
    // Actions
    show, 
    showError, 
    hide 
  };
});