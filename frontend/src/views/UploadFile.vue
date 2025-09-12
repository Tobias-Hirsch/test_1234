<template>
  <div class="upload-file-container">
    <el-card class="upload-file-card">
      <template #header>
        <div class="card-header">
          <span>{{ $t('uploadFile.title') }}</span>
        </div>
      </template>
      <el-upload
        class="upload-demo"
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        :file-list="fileList"
        action=""
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          {{ $t('uploadFile.dragDrop') }} <em>{{ $t('uploadFile.clickToUpload') }}</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            {{ $t('uploadFile.fileTypeTip') }}
          </div>
        </template>
      </el-upload>
      <div class="upload-button-container">
        <el-button type="primary" @click="submitUpload" :disabled="fileList.length === 0">{{ $t('uploadFile.uploadButton') }}</el-button>
      </div>
    </el-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { ElCard, ElUpload, ElButton, ElMessage } from 'element-plus';
import { UploadFilled } from '@element-plus/icons-vue';
import type { UploadFile, UploadFiles } from 'element-plus';
import { useI18n } from 'vue-i18n';
import { uploadFile } from '../services/apiService'; // Import the uploadFile service

export default defineComponent({
  name: 'UploadFile',
  components: {
    ElCard,
    ElUpload,
    ElButton,
    UploadFilled,
  },
  setup() {
    const { t } = useI18n();
    const fileList = ref<UploadFile[]>([]);

    const handleFileChange = (file: UploadFile, files: UploadFiles) => {
      // Keep only the last selected file
      fileList.value = [file];
    };

    const handleFileRemove = (file: UploadFile, files: UploadFiles) => {
      fileList.value = [];
    };

    const submitUpload = async () => {
      if (fileList.value.length === 0 || !fileList.value[0].raw) {
        ElMessage.warning(t('uploadFile.noFileSelected'));
        return;
      }

      const fileToUpload = fileList.value[0].raw;

      try {
        await uploadFile(fileToUpload);
        ElMessage.success(t('uploadFile.uploadSuccess'));
        fileList.value = []; // Clear the file list after successful upload
      } catch (error: any) {
        console.error('File upload failed:', error);
        ElMessage.error(error.message || t('uploadFile.uploadFailed'));
      }
    };

    return {
      fileList,
      handleFileChange,
      handleFileRemove,
      submitUpload,
      t, // Expose t for template usage
    };
  },
});
</script>

<style scoped>
.upload-file-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--el-bg-color-page);
}

.upload-file-card {
  width: 600px;
  max-width: 90%;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  background-color: var(--el-bg-color-overlay);
  color: var(--el-text-color-primary);
}

.dark-mode .upload-file-container {
  background-color: var(--el-bg-color-page); /* Ensure dark mode background */
}

.dark-mode .upload-file-card {
  background-color: var(--el-bg-color-overlay); /* Ensure dark mode card background */
  color: var(--el-text-color-primary); /* Ensure dark mode text color */
}

.dark-mode .card-header {
  color: var(--el-text-color-primary); /* Ensure dark mode header text color */
}

.dark-mode .el-upload__text {
  color: var(--el-text-color-regular); /* Ensure dark mode upload text color */
}

.dark-mode .el-upload__tip {
  color: var(--el-text-color-secondary); /* Ensure dark mode tip text color */
}

.card-header {
  font-size: 1.2em;
  font-weight: bold;
  text-align: center;
  color: var(--el-text-color-primary);
}

.upload-demo {
  margin-bottom: 20px;
}

.upload-button-container {
  text-align: center;
}
</style>