<template>
  <div class="role-management-container">
    <h1>Role Management</h1>

    <el-button type="primary" @click="openCreateRoleDialog">Create Role</el-button>

    <el-table :data="roles" v-loading="loading" style="width: 100%; margin-top: 20px;">
      <el-table-column prop="id" label="ID" width="80"></el-table-column>
      <el-table-column prop="name" label="Name"></el-table-column>
      <el-table-column prop="description" label="Description"></el-table-column>
      <el-table-column label="Actions" width="250">
        <template #default="scope">
          <el-button size="small" @click="handleEdit(scope.row)">Edit</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.row)">Delete</el-button>
        </template>
      </el-table-column>
    </el-table>


    <!-- Create/Edit Role Dialog -->
    <el-dialog v-model="roleDialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="currentRole" label-width="100px">
        <el-form-item label="Name">
          <el-input v-model="currentRole.name"></el-input>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="currentRole.description" type="textarea"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="roleDialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="saveRole">Save</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue';
import { ElTable, ElTableColumn, ElButton, ElMessage, ElDialog, ElForm, ElFormItem, ElInput } from 'element-plus'; // Import Element Plus components
import { getRoles, createRole, Role } from '@/services/apiService'; // Import API service and interfaces

export default defineComponent({
  name: 'RoleManagement',
  components: {
    ElTable,
    ElTableColumn,
    ElButton,
    ElDialog,
    ElForm,
    ElFormItem,
    ElInput,
  },
  setup() {
    const roles = ref<Role[]>([]);
    const loading = ref(true);
    const roleDialogVisible = ref(false);
    const isEditing = ref(false);
    const currentRole = ref<Partial<Role>>({ name: '', description: '' });


    const dialogTitle = computed(() => isEditing.value ? 'Edit Role' : 'Create Role');

    const fetchRoles = async () => {
      loading.value = true;
      try {
        roles.value = await getRoles();
      } catch (error: any) {
        ElMessage.error('Failed to fetch roles: ' + error.message);
      } finally {
        loading.value = false;
      }
    };


    const openCreateRoleDialog = () => {
      isEditing.value = false;
      currentRole.value = { name: '', description: '' };
      roleDialogVisible.value = true;
    };

    const handleEdit = (role: Role) => {
      isEditing.value = true;
      currentRole.value = { ...role }; // Copy role data for editing
      roleDialogVisible.value = true;
    };

    const handleDelete = (role: Role) => {
      console.log('Delete role:', role);
      // TODO: Implement delete functionality (e.g., show a confirmation dialog and call API)
    };

    const saveRole = async () => {
      if (!currentRole.value.name) {
        ElMessage.warning('Role name is required.');
        return;
      }

      try {
        if (isEditing.value && currentRole.value.id) {
          // TODO: Implement update role API call
          ElMessage.info('Update functionality not yet implemented.');
        } else {
          await createRole(currentRole.value as { name: string; description?: string });
          ElMessage.success('Role created successfully.');
        }
        roleDialogVisible.value = false;
        fetchRoles(); // Refresh roles list
      } catch (error: any) {
        ElMessage.error('Failed to save role: ' + error.message);
      }
    };



    onMounted(() => {
      fetchRoles();
    });

    return {
      roles,
      loading,
      roleDialogVisible,
      isEditing,
      currentRole,
      dialogTitle,
      fetchRoles,
      openCreateRoleDialog,
      handleEdit,
      handleDelete,
      saveRole,
    };
  },
});
</script>

<style scoped>
.role-management-container {
  padding: 20px;
}
</style>