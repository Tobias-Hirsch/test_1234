<template>
  <div class="rag-list-container">
    <h1>{{ t('ragList.title') }}</h1>

    <el-button v-if="canCreate" type="primary" @click="createNewRag" class="create-button">{{ t('ragList.createNewButton') }}</el-button>

    <table v-if="ragDataList.length">
      <thead>
        <tr>
          <th>{{ t('ragList.table.idHeader') }}</th>
          <th>{{ t('ragList.table.nameHeader') }}</th>
          <th>{{ t('ragList.table.descriptionHeader') }}</th>
          <th>{{ t('ragList.table.activeHeader') }}</th>
          <th>{{ t('ragList.table.createdAtHeader') }}</th>
          <th>{{ t('ragList.table.updatedAtHeader') }}</th>
          <th>{{ t('ragList.table.actionsHeader') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="ragData in ragDataList" :key="ragData.id">
          <td>{{ ragData.id }}</td>
          <td>{{ ragData.name }}</td>
          <td>{{ ragData.description }}</td>
          <td>{{ ragData.is_active === 1 ? t('ragList.table.activeYes') : t('ragList.table.activeNo') }}</td>
          <td>{{ formatDate(ragData.created_at) }}</td>
          <td>{{ ragData.updated_at ? formatDate(ragData.updated_at) : '-' }}</td>
          <td>
            <!-- Edit button: enabled based on UI permission -->
            <el-button
              size="small"
              @click="editRagData(ragData.id)"
              :disabled="!canEdit"
            >
              {{ t('ragList.actions.editButton') }}
            </el-button>
            <!-- Delete button: enabled based on UI permission -->
            <el-button
              size="small"
              type="danger"
              @click="deleteRagDataEntry(ragData.id)"
              :disabled="!canDelete"
            >
              {{ t('ragList.actions.deleteButton') }}
            </el-button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else>{{ t('ragList.noDataMessage') }}</p>

    <div v-if="loading">{{ t('ragList.loadingMessage') }}</div>
    <div v-if="error">{{ error }}</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { getRagDataList, deleteRagData, listRagFiles, type RagData } from '../services/apiService'; // Import RagData type
import { format } from 'date-fns'; // Import date-fns for formatting
import { useAuthStore } from '../stores/auth'; // Import auth store
import { useI18n } from 'vue-i18n'; // Import useI18n
import { useToast } from 'vue-toastification'; // Import useToast
import { ElButton } from 'element-plus'; // Import ElButton
import { ElMessageBox } from 'element-plus'; // Import ElMessageBox for confirmation

export default defineComponent({
  name: 'RagList',
  components: {
    ElButton, // Register ElButton
  },
  setup() { // Removed props
    const router = useRouter();
    const { t } = useI18n(); // Use useI18n directly
    const toast = useToast(); // Use useToast directly
    const authStore = useAuthStore(); // Use auth store
    const ragDataList = ref<RagData[]>([]);
    const loading = ref(false);
    const error = ref<string | null>(null);
    const canCreate = ref(false);
    const canEdit = ref(false);
    const canDelete = ref(false);

    watch(() => t, () => { // Watch t for locale changes
      console.log('RagList.vue: Locale changed');
    });

    onMounted(async () => {
      if (authStore.isAuthenticated) {
        // Fetch permissions using the new ABAC service
        canCreate.value = await authStore.can('create', 'rag_data');
        canEdit.value = await authStore.can('update', 'rag_data');
        canDelete.value = await authStore.can('delete', 'rag_data');
        
        // Now fetch the data
        fetchRagData();
      } else {
        router.push('/login'); // Redirect to login if not authenticated
      }
    });

    const fetchRagData = async () => {
      loading.value = true;
      error.value = null;
      try {
        const response = await getRagDataList();
        ragDataList.value = response.rag_data;
      } catch (err: any) {
        if (err.message === 'Permission Denied') {
          toast.error(t('ragEdit.savePermissionDenied', { error: err.message }));
          router.push('/login'); // Redirect to login if permission denied
        } else {
          error.value = `${t('ragList.fetchErrorPrefix')}: ${err.message}`;
          console.error(err);
        }
      } finally {
        loading.value = false;
      }
    };

    const createNewRag = () => {
      // Navigate to the edit page with no ID to indicate creation
      router.push({ name: 'RagEdit', params: { id: 'new' } });
    };

    const editRagData = (id: number) => {
      router.push({ name: 'RagEdit', params: { id: id.toString() } });
    };

    const deleteRagDataEntry = async (id: number) => {
      // Permission is now checked by the disabled state of the button.
      // An additional check could be done here, but it's not strictly necessary
      // as the button shouldn't be clickable if the user lacks permission.
      try {
        const associatedFiles = await listRagFiles(id);
        let confirmed = false;

        if (associatedFiles.length > 0) {
          const confirmationText = t('ragList.deleteConfirmationWithFiles', { count: associatedFiles.length });
          // Use ElMessageBox for a better UI confirmation
          try {
            await ElMessageBox.confirm(
              confirmationText,
              t('ragList.deleteConfirmationTitle'),
              {
                confirmButtonText: t('ragList.confirmButton'),
                cancelButtonText: t('ragList.cancelButton'),
                type: 'warning',
              }
            );
            confirmed = true;
          } catch {
            // User cancelled the dialog
            alert(t('ragList.deleteCancelledMessage'));
            confirmed = false;
          }
        } else {
          // Use ElMessageBox for a better UI confirmation
           try {
            await ElMessageBox.confirm(
              t('ragList.deleteConfirmation'),
              t('ragList.deleteConfirmationTitle'),
              {
                confirmButtonText: t('ragList.confirmButton'),
                cancelButtonText: t('ragList.cancelButton'),
                type: 'warning',
              }
            );
            confirmed = true;
          } catch {
            // User cancelled the dialog
            alert(t('ragList.deleteCancelledMessage'));
            confirmed = false;
          }
        }

        if (confirmed) {
          await deleteRagData(id);
          // Remove the deleted item from the list
          ragDataList.value = ragDataList.value.filter(item => item.id !== id);
        }
      } catch (err: any) {
        error.value = `${t('ragList.deleteErrorPrefix')}: ${err.message}`;
        console.error(err);
      }
    };

    const formatDate = (dateString: string) => {
      if (!dateString) return '-';
      try {
        // Assuming the backend returns ISO 8601 strings
        return format(new Date(dateString), 'yyyy-MM-dd HH:mm');
      } catch (e) {
        console.error("Error formatting date:", e);
        return dateString; // Return original string if formatting fails
      }
    };

    return {
      t,
      ragDataList,
      loading,
      error,
      createNewRag,
      editRagData,
      deleteRagDataEntry,
      formatDate,
      authStore, // Expose authStore to the template
      canCreate,
      canEdit,
      canDelete,
    };
  },
});
</script>

<style scoped>
.rag-list-container {
  padding: 20px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th, td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

th {
  background-color: #f2f2f2;
}

tr:nth-child(even) {
  background-color: #f9f9f9;
}

/* Remove or adjust native button styles */
/*
.create-button {
  margin-bottom: 20px;
  padding: 10px 15px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.create-button:hover {
  background-color: #45a049;
}

button {
  margin-right: 5px;
  padding: 5px 10px;
  cursor: pointer;
}
*/
</style>