<!--
Developer: Jinglu Han
mailbox: admin@de-manufacturing.cn
-->

<template>
  <el-dialog
    v-model="dialogVisible"
    :title="t('knowledgeBase.title')"
    width="70%"
    @close="handleClose"
  >
    <div class="kb-manager-container">
      <div class="toolbar">
        <el-upload
          ref="uploadRef"
          class="upload-demo"
          action="#"
          :http-request="handleUpload"
          :show-file-list="false"
          multiple
        >
          <el-button type="primary">
            <el-icon><Upload /></el-icon> {{ t('knowledgeBase.uploadFiles') }}
          </el-button>
        </el-upload>
      </div>

      <el-table :data="documents" v-loading="loading" style="width: 100%">
        <el-table-column prop="original_filename" :label="t('knowledgeBase.filename')" />
        <el-table-column prop="created_at" :label="t('knowledgeBase.uploadDate')" width="200">
          <template #default="scope">
            <span>{{ new Date(scope.row.created_at).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="t('knowledgeBase.status')" width="120">
            <template #default="scope">
                <el-tag :type="getStatusTag(scope.row.status)">{{ scope.row.status || 'N/A' }}</el-tag>
            </template>
        </el-table-column>
        <el-table-column :label="t('knowledgeBase.actions')" width="120">
          <template #default="scope">
            <el-button
              link
              type="primary"
              size="small"
              @click.prevent="deleteDocument(scope.row.id)"
            >
              {{ t('knowledgeBase.delete') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">{{ t('knowledgeBase.close') }}</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, Ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElDialog, ElButton, ElTable, ElTableColumn, ElUpload, ElIcon, ElMessage, ElMessageBox, ElTag } from 'element-plus';
import { Upload } from '@element-plus/icons-vue';
import {
  FileGist,
  listKnowledgeBaseDocuments,
  uploadFilesToKnowledgeBase,
  triggerKnowledgeBaseEmbedding,
  deleteKnowledgeBaseDocument
} from '@/services/apiService';

const props = defineProps({
  visible: {
    type: Boolean,
    required: true,
  },
  ragId: {
    type: Number,
    required: true,
  },
});

const emit = defineEmits(['update:visible']);

const { t } = useI18n();
const dialogVisible = ref(props.visible);
const documents: Ref<FileGist[]> = ref([]);
const loading = ref(false);

watch(() => props.visible, (newValue) => {
  dialogVisible.value = newValue;
  if (newValue) {
    fetchDocuments();
  }
});

const handleClose = () => {
  emit('update:visible', false);
};

const fetchDocuments = async () => {
  if (!props.ragId) return;
  loading.value = true;
  try {
    documents.value = await listKnowledgeBaseDocuments(props.ragId);
  } catch (error: any) {
    ElMessage.error(`${t('knowledgeBase.errors.fetch')}: ${error.message}`);
  } finally {
    loading.value = false;
  }
};

const handleUpload = async (options: any) => {
  if (!props.ragId) {
    ElMessage.error(t('knowledgeBase.errors.noRagId'));
    return;
  }
  
  const file = options.file;
  ElMessage.info(`${t('knowledgeBase.uploading')} ${file.name}`);
  
  try {
    // Step 1: Upload file to get FileGist record
    const uploadedGists = await uploadFilesToKnowledgeBase(props.ragId, [file]);
    if (!uploadedGists || uploadedGists.length === 0) {
      throw new Error("File upload did not return a valid record.");
    }
    
    ElMessage.info(`${file.name} ${t('knowledgeBase.uploadSuccess')}. ${t('knowledgeBase.embeddingStart')}`);
    
    // Step 2: Trigger embedding process
    const fileIds = uploadedGists.map(gist => gist.id);
    await triggerKnowledgeBaseEmbedding(props.ragId, fileIds);
    
    ElMessage.success(`${file.name} ${t('knowledgeBase.embeddingSuccess')}`);
    
  } catch (error: any) {
    ElMessage.error(`${t('knowledgeBase.errors.uploadFail')}: ${error.message}`);
  } finally {
    fetchDocuments(); // Refresh the list regardless of outcome
  }
};

const deleteDocument = async (docId: number) => {
  if (!props.ragId) return;

  ElMessageBox.confirm(
    t('knowledgeBase.deleteConfirmText'),
    t('knowledgeBase.deleteConfirmTitle'),
    {
      confirmButtonText: t('knowledgeBase.delete'),
      cancelButtonText: t('knowledgeBase.cancel'),
      type: 'warning',
    }
  ).then(async () => {
    try {
      await deleteKnowledgeBaseDocument(props.ragId, docId);
      ElMessage.success(t('knowledgeBase.errors.deleteSuccess'));
      fetchDocuments(); // Refresh list
    } catch (error: any) {
      ElMessage.error(`${t('knowledgeBase.errors.deleteFail')}: ${error.message}`);
    }
  }).catch(() => {
    // Action cancelled
  });
};

const getStatusTag = (status: string) => {
    if (status === 'Completed') return 'success';
    if (status === 'Processing') return 'primary';
    if (status === 'Failed') return 'danger';
    return 'info';
};

</script>

<style scoped>
.kb-manager-container {
  padding: 20px;
}
.toolbar {
  margin-bottom: 20px;
}
</style>