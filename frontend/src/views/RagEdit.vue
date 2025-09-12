<template>
  <div class="rag-edit-container">
    <h1>{{ isNew ? t('ragEdit.titleNew') : t('ragEdit.titleEdit') }}</h1>

    <!-- RagForm content -->
    <form @submit.prevent="saveRagData">
      <div class="form-group">
        <label for="name">{{ t('ragEdit.nameLabel') }}:</label>
        <input type="text" id="name" v-model="formData.name" required :disabled="isFormDisabled">
      </div>
      <div class="form-group">
        <label for="description">{{ t('ragEdit.descriptionLabel') }}:</label>
        <textarea id="description" v-model="formData.description" :disabled="isFormDisabled"></textarea>
      </div>
      <div class="form-group">
        <label for="is_active">{{ t('ragEdit.activeLabel') }}:</label>
        <input type="checkbox" id="is_active" v-model="isActiveCheckbox" :disabled="isFormDisabled">
      </div>
      <el-button type="primary" native-type="submit" :disabled="isFormDisabled">{{ isNew ? t('ragEdit.createButton') : t('ragEdit.saveButton') }}</el-button>
      <el-button type="info" @click="cancelEdit" :disabled="isFormDisabled">{{ t('ragEdit.cancelButton') }}</el-button>
    </form>

    <hr v-if="!isNew">

    <!-- RagEmbedding content -->
    <div v-if="!isNew" class="file-upload-section">
      <h2>{{ t('ragEdit.uploadFilesTitle') }}</h2>
      <input type="file" multiple @change="handleFileChange" ref="fileInputRef" style="display: none;" :disabled="!canEditFile">
      <el-button type="info" @click="triggerFileInput" :disabled="!canEditFile">{{ t('ragEdit.selectFileButton') }}</el-button>
      <el-button type="primary" @click="uploadSelectedFiles" :disabled="!selectedFiles.length || !canEditFile">{{ t('ragEdit.uploadFilesButton') }}</el-button>
      <el-button type="info" @click="handleEmbedSelected" :disabled="selectedFileIds.length === 0 || !canEditFile">{{ t('ragEdit.embedButton') }}</el-button>
      <el-button type="info" @click="handleReEmbedSelected" :disabled="selectedFileIds.length === 0 || !canEditFile">{{ t('ragEdit.reEmbedButton') }}</el-button>
      <el-button type="info" @click="handlePreviewSelected" :disabled="selectedFileIds.length === 0 || !canReadFile">{{ t('ragEdit.previewButton') }}</el-button>
      <el-button type="danger" @click="handleDeleteSelected" :disabled="selectedFileIds.length === 0 || !canDeleteFile">{{ t('ragEdit.deleteButton') }}</el-button>
      <div v-if="uploading">{{ t('ragEdit.uploadingMessage') }}</div>
      <div v-if="uploadError" class="error-message">{{ uploadError }}</div>
      <div v-if="uploadSuccess" class="success-message">{{ uploadSuccess }}</div>
    </div>

    <hr v-if="!isNew && (files.length > 0 || filesLoading || filesError)">

    <!-- RagFileList content -->
    <div v-if="!isNew && canReadFile" class="file-list-section">
      <h2>{{ t('ragEdit.associatedFilesTitle') }}</h2>
      <div v-if="filesLoading">{{ t('ragEdit.loadingFilesMessage') }}</div>
      <div v-if="filesError" class="error-message">{{ filesError }}</div>
      <div class="file-list-header" v-if="files.length > 0 && !filesLoading">
        <el-checkbox :model-value="allFilesSelected" @change="handleToggleSelectAll" :disabled="!canEditFile">{{ t('ragEdit.selectAllLabel') }}</el-checkbox>
      </div>
      <ul v-if="files.length > 0 && !filesLoading">
        <li v-for="file in files" :key="file.id" class="file-item">
           <el-checkbox :label="file.id.toString()" :model-value="selectedFileIds.includes(file.id)" @change="handleFileCheckboxChange(file.id, $event)"></el-checkbox>
           <a @click.prevent="handleFileCheckboxChange(file.id, !selectedFileIds.includes(file.id))" href="#" class="file-link">{{ file.filename }}</a>
         </li>
      </ul>
      <div v-if="files.length === 0 && !filesLoading && !filesError">{{ t('ragEdit.noFilesMessage') }}</div>
    </div>

    <div v-if="loading">{{ t('ragEdit.loadingRagDataMessage') }}</div>
    <div v-if="error" class="error-message">{{ error }}</div>

  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';
import { ElButton, ElCheckbox } from 'element-plus';
import { useRagEdit } from '../composables/useRagEdit';

const props = defineProps({
  id: {
    type: String,
    required: true
  },
});

const {
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
} = useRagEdit(props);
</script>

<style scoped>
.rag-edit-container {
  padding: 20px;
}

.error-message {
  color: red;
  margin-top: 10px;
}

.success-message {
  color: green;
  margin-top: 10px;
}

/* Styles from RagForm */
.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input[type="text"],
.form-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.form-group input:disabled,
.form-group textarea:disabled {
    background-color: #f5f5f5;
    cursor: not-allowed;
}

/* Styles from RagEmbedding */
.file-upload-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

/* Styles from RagFileList */
.file-list-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.file-list-header {
  margin-bottom: 10px;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.file-item .el-checkbox {
  margin-right: 10px;
}

.file-item span {
  flex-grow: 1;
  margin-right: 10px;
}

.file-link {
  color: #409EFF;
  text-decoration: none;
  cursor: pointer;
}

.file-link:hover {
  text-decoration: underline;
}
</style>