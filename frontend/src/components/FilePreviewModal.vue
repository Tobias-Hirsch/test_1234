<!--
Developer: Jinglu Han
mailbox: admin@de-manufacturing.cn
-->

<template>
  <el-dialog
    :model-value="previewStore.isVisible"
    :title="previewStore.fileName"
    fullscreen
    @close="handleClose"
    class="file-preview-dialog"
  >
    <div v-loading="isLoading" v-if="previewStore.fileType !== 'error'" class="preview-content-wrapper">
      <!-- The content will be rendered here or show loading -->
    </div>

    <div v-else class="error-display">
      <h2>Preview Error</h2>
      <p>{{ previewStore.error }}</p>
    </div>

    <div class="preview-content">
      <!-- PDF Preview -->
      <div v-if="previewStore.fileType === 'pdf' && !isLoading" ref="pdfContainer" class="pdf-container">
        <vue-pdf-embed :source="previewStore.url" />
      </div>

      <!-- Image Preview -->
      <div v-else-if="['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'].includes(previewStore.fileType || '') && !isLoading" class="image-container">
        <img :src="previewStore.url" :alt="previewStore.fileName" />
      </div>

      <!-- DOCX Preview -->
      <div v-else-if="previewStore.fileType === 'docx' && !isLoading" ref="docxContainer" class="docx-container"></div>

      <!-- XLSX Preview -->
      <div v-else-if="previewStore.fileType === 'xlsx' && !isLoading" class="xlsx-container">
        <el-table :data="excelData.rows" stripe>
          <el-table-column v-for="header in excelData.headers" :key="header" :prop="header" :label="header"></el-table-column>
        </el-table>
      </div>

      <!-- Unsupported File Type -->
      <div v-else class="unsupported-container">
        <h2>Unsupported File Type</h2>
        <p>Cannot preview files of type: <strong>.{{ previewStore.fileType }}</strong></p>
        <p>You can still try to download it.</p>
        <el-button type="primary" @click="downloadFile">Download File</el-button>
      </div>
    </div>

    <template #footer>
      <el-button @click="handleClose">Close</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import { usePreviewStore } from '../stores/preview';
import { ElDialog, ElButton, ElTable, ElTableColumn, vLoading } from 'element-plus';
import VuePdfEmbed from 'vue-pdf-embed';
import { renderAsync } from 'docx-preview';
import * as XLSX from 'xlsx';

const previewStore = usePreviewStore();

const isLoading = ref(false);
const docxContainer = ref<HTMLDivElement | null>(null);
const pdfContainer = ref<HTMLDivElement | null>(null);
const excelData = ref<{ headers: string[], rows: any[] }>({ headers: [], rows: [] });

const handleClose = () => {
  previewStore.hide();
};

const downloadFile = () => {
  if (previewStore.url) {
    const a = document.createElement('a');
    a.href = previewStore.url;
    a.download = previewStore.fileName || 'download';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }
};

watch(() => previewStore.isVisible, async (visible) => {
  if (visible && previewStore.url) {
    isLoading.value = true;
    await nextTick(); // Wait for the dialog and containers to be rendered

    try {
      const response = await fetch(previewStore.url);
      const blob = await response.blob();

      if (previewStore.fileType === 'docx' && docxContainer.value) {
        await renderAsync(blob, docxContainer.value);
      } else if (previewStore.fileType === 'xlsx') {
        const arrayBuffer = await blob.arrayBuffer();
        const workbook = XLSX.read(arrayBuffer, { type: 'buffer' });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const json = XLSX.utils.sheet_to_json<any>(worksheet, { header: 1 });
        
        if (json.length > 0) {
          excelData.value.headers = json[0];
          excelData.value.rows = json.slice(1).map((row: any[]) => {
            const rowData: { [key: string]: any } = {};
            excelData.value.headers.forEach((header: string, index: number) => {
              rowData[header] = row[index];
            });
            return rowData;
          });
        }
      }
      // PDF and images are handled directly by their components via URL
    } catch (error) {
      console.error('Error rendering file preview:', error);
      previewStore.showError(`Failed to load file for preview. ${error instanceof Error ? error.message : ''}`);
    } finally {
      isLoading.value = false;
    }
  }
});
</script>

<style scoped>
.preview-content {
  height: 100%;
  overflow: auto;
  background-color: #f0f2f5;
}
.pdf-container, .docx-container, .xlsx-container, .image-container {
  height: 100%;
}
.image-container img {
  max-width: 100%;
  max-height: 100%;
  display: block;
  margin: auto;
}
.loading-spinner, .error-display, .unsupported-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  text-align: center;
}
.docx-container {
  padding: 20px;
  background-color: white;
}
</style>