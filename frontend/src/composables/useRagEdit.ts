import { ref, computed, watch, watchEffect } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getRagDataById, createRagData, updateRagData, uploadRagFile, listRagFiles, deleteRagFile, previewFile as previewFileApi, embedRagFiles, type RagData, type RagDataCreate, type RagDataUpdate, type FileGist } from '../services/apiService';
import { useAuthStore } from '../stores/auth';
import { useI18n } from 'vue-i18n';
import { useToast } from 'vue-toastification';
import { usePreviewStore } from '../stores/preview';
import type { CheckboxValueType } from 'element-plus';

export function useRagEdit(props: { id: string }) {
  const route = useRoute();
  const router = useRouter();
  const { t } = useI18n();
  const toast = useToast();
  const authStore = useAuthStore();
  const previewStore = usePreviewStore();

  const isNew = computed(() => props.id === 'new');

  const ragData = ref<Partial<RagData>>({
    name: '',
    description: '',
    is_active: 1,
  });

  const loading = ref(false);
  const error = ref<string | null>(null);

  // Form related state
  const formData = ref<Partial<RagData>>({ ...ragData.value });
  watch(() => ragData.value, (newVal) => {
    formData.value = { ...newVal };
  }, { deep: true });

  const isActiveCheckbox = computed({
    get: () => formData.value.is_active === 1,
    set: (value: boolean) => {
      formData.value.is_active = value ? 1 : 0;
    }
  });

  const isFormDisabled = ref(true); // Default to disabled while checking permission

  watchEffect(async () => {
    const action = isNew.value ? 'create' : 'update';
    isFormDisabled.value = !(await authStore.can(action, 'rag_data'));
  });

  // Embedding related state
  const selectedFiles = ref<File[]>([]);
  const uploading = ref(false);
  const uploadError = ref<string | undefined>(undefined);
  const uploadSuccess = ref<string | undefined>(undefined);
  const fileInputRef = ref<HTMLInputElement | null>(null);

  // File list related state
  const files = ref<FileGist[]>([]);
  const filesLoading = ref(false);
  const filesError = ref<string | undefined>(undefined);
  const selectedFileIds = ref<number[]>([]);

  const canEditFile = computed(() => authStore.can('update', 'file'));
  const canDeleteFile = computed(() => authStore.can('delete', 'file'));
  const canReadFile = computed(() => authStore.can('read', 'file'));

  const allFilesSelected = computed(() => files.value.length > 0 && selectedFileIds.value.length === files.value.length);

  // Methods
  const fetchRagData = async (id: number) => {
    loading.value = true;
    error.value = null;
    try {
      const data = await getRagDataById(id);
      ragData.value = data;
    } catch (err: any) {
      if (err.message === 'Permission Denied') {
        toast.error(t('ragEdit.savePermissionDenied', { error: err.message }));
        router.push('/login');
      } else {
        error.value = `${t('ragEdit.fetchRagDataErrorPrefix')}: ${err.message}`;
        console.error(err);
      }
    } finally {
      loading.value = false;
    }
  };

  const fetchRagFiles = async (id: number) => {
    filesLoading.value = true;
    filesError.value = undefined;
    try {
      files.value = await listRagFiles(id);
    } catch (err: any) {
      filesError.value = `${t('ragEdit.fetchFilesErrorPrefix')}: ${err.message}`;
      console.error(err);
    } finally {
      filesLoading.value = false;
    }
  };

  const saveRagData = async () => {
    loading.value = true;
    error.value = null;
    try {
      if (isNew.value) {
        if (!formData.value.name) {
          throw new Error(t('ragEdit.nameRequiredError'));
        }
        const newRagEntry = await createRagData({
          name: formData.value.name,
          description: formData.value.description,
        } as RagDataCreate);
        ragData.value = newRagEntry;
        router.push({ name: 'RagEdit', params: { id: newRagEntry.id.toString() } });
      } else {
        if (formData.value.id === undefined) {
          throw new Error(t('ragEdit.idMissingForUpdateError'));
        }
        const updatedFields: RagDataUpdate = {
          name: formData.value.name,
          description: formData.value.description,
          is_active: formData.value.is_active,
        };
        await updateRagData(formData.value.id, updatedFields);
        await fetchRagData(formData.value.id);
      }
    } catch (err: any) {
      if (err.message === 'Permission Denied') {
        toast.error(t('ragEdit.savePermissionDenied', { error: err.message }));
        router.push('/login');
      } else {
        error.value = err.message;
        console.error(err);
      }
    } finally {
      loading.value = false;
    }
  };

  const cancelEdit = () => {
    router.push({ name: 'RagList' });
  };

  const handleFileChange = (event: Event) => {
    const target = event.target as HTMLInputElement;
    if (target.files) {
      selectedFiles.value = Array.from(target.files);
    } else {
      selectedFiles.value = [];
    }
  };

  const triggerFileInput = () => {
    fileInputRef.value?.click();
  };

  const uploadSelectedFiles = async () => {
    if (!selectedFiles.value.length || isNew.value) return;

    uploading.value = true;
    uploadError.value = undefined;
    uploadSuccess.value = undefined;

    const currentRagId = parseInt(props.id as string);

    for (const file of selectedFiles.value) {
      try {
        await uploadRagFile(currentRagId, file);
        uploadSuccess.value = t('ragEdit.fileUploadSuccess', { fileName: file.name });
        setTimeout(() => { uploadSuccess.value = undefined; }, 5000);
      } catch (err: any) {
        uploadError.value = `${t('ragEdit.fileUploadErrorPrefix', { fileName: file.name })}: ${err.message}`;
        console.error(err);
        break;
      }
    }

    uploading.value = false;
    selectedFiles.value = [];
    if (fileInputRef.value) {
      fileInputRef.value.value = '';
    }
    if (!uploadError.value && !isNew.value) {
      fetchRagFiles(parseInt(props.id as string));
    }
  };

  const handleEmbedSelected = async () => {
    if (selectedFileIds.value.length === 0 || isNew.value || ragData.value.id === undefined) {
      toast.info(t('ragEdit.selectFilesToEmbed'));
      return;
    }
    try {
      await embedRagFiles(ragData.value.id, selectedFileIds.value);
      toast.success(t('ragEdit.embeddingStarted'));
    } catch (err: any) {
      toast.error(`${t('ragEdit.embeddingErrorPrefix')}: ${err.message}`);
    } finally {
      selectedFileIds.value = [];
    }
  };

  const handleReEmbedSelected = async () => {
    if (selectedFileIds.value.length === 0 || isNew.value || ragData.value.id === undefined) {
      toast.info(t('ragEdit.selectFilesToReEmbed'));
      return;
    }
    try {
      await embedRagFiles(ragData.value.id, selectedFileIds.value);
      toast.success(t('ragEdit.reEmbeddingStarted'));
    } catch (err: any) {
      toast.error(`${t('ragEdit.reEmbeddingErrorPrefix')}: ${err.message}`);
    } finally {
      selectedFileIds.value = [];
    }
  };

  const previewFile = async (fileId: number) => {
    const fileInfo = files.value.find(f => f.id === fileId);
    if (!fileInfo) {
      toast.error('File information not found.');
      return;
    }
    filesLoading.value = true;
    filesError.value = undefined;
    try {
      const blob = await previewFileApi(fileId);
      const url = window.URL.createObjectURL(blob);
      const fileType = fileInfo.filename.split('.').pop() || 'unknown';
      previewStore.show(url, fileType, fileInfo.filename);
    } catch (err: any) {
      filesError.value = `${t('ragEdit.previewFileErrorPrefix')}: ${err.message}`;
      previewStore.showError(`${t('ragEdit.previewFileErrorPrefix')}: ${err.message}`);
    } finally {
      filesLoading.value = false;
    }
  };
  
  const handlePreviewSelected = async () => {
      if (selectedFileIds.value.length > 0) {
        await previewFile(selectedFileIds.value[0]);
      }
  };

  const handleDeleteSelected = async () => {
    if (confirm(t('ragEdit.deleteFileConfirmation'))) {
      filesLoading.value = true;
      filesError.value = undefined;
      try {
        for (const fileId of selectedFileIds.value) {
          await deleteRagFile(fileId);
          files.value = files.value.filter(file => file.id !== fileId);
          toast.success(t('ragEdit.fileDeletedSuccess', { fileId: fileId }));
        }
        selectedFileIds.value = [];
      } catch (err: any) {
        filesError.value = `${t('ragEdit.deleteFileErrorPrefix')}: ${err.message}`;
      } finally {
        filesLoading.value = false;
      }
    }
  };

  const handleToggleSelectAll = (val: CheckboxValueType) => {
    if (canEditFile.value) {
      const checked = val === true;
      selectedFileIds.value = checked ? files.value.map(file => file.id) : [];
    }
  };

  const handleFileCheckboxChange = (fileId: number, checked: boolean | CheckboxValueType) => {
    if (canEditFile.value) {
      const isChecked = checked === true;
      const index = selectedFileIds.value.indexOf(fileId);
      if (isChecked && index === -1) {
        selectedFileIds.value.push(fileId);
      } else if (!isChecked && index !== -1) {
        selectedFileIds.value.splice(index, 1);
      }
    }
  };

  watch(() => props.id, (newId) => {
    if (newId !== 'new') {
      const currentRagId = parseInt(newId as string);
      fetchRagData(currentRagId);
      fetchRagFiles(currentRagId);
    } else {
      ragData.value = { name: '', description: '', is_active: 1 };
      files.value = [];
      filesError.value = undefined;
      selectedFileIds.value = [];
    }
  }, { immediate: true });

  return {
    t,
    isNew,
    ragData,
    loading,
    error,
    formData,
    isActiveCheckbox,
    isFormDisabled,
    selectedFiles,
    uploading,
    uploadError,
    uploadSuccess,
    fileInputRef,
    files,
    filesLoading,
    filesError,
    selectedFileIds,
    canEditFile,
    canDeleteFile,
    canReadFile,
    allFilesSelected,
    saveRagData,
    cancelEdit,
    handleFileChange,
    triggerFileInput,
    uploadSelectedFiles,
    handleEmbedSelected,
    handleReEmbedSelected,
    handlePreviewSelected,
    handleDeleteSelected,
    handleToggleSelectAll,
    handleFileCheckboxChange,
  };
}