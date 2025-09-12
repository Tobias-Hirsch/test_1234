<template>
  <div class="user-management-container">
    <h1>{{ $t('userManagement.userManagementTitle') }}</h1>

    <!-- Entire el-table section commented out for diagnosis -->
    
    <el-table :data="users" v-loading="loading" style="width: 100%">
      <el-table-column prop="id" :label="$t('userManagement.table.idHeader')" width="80"></el-table-column>
      <el-table-column prop="username" :label="$t('userManagement.table.usernameHeader')"></el-table-column>
      <el-table-column prop="email" :label="$t('userManagement.table.emailHeader')"></el-table-column>
      <el-table-column prop="phone" :label="$t('userManagement.table.phoneHeader')"></el-table-column>
      <el-table-column prop="department" :label="$t('userManagement.table.departmentHeader')"></el-table-column>
      <el-table-column prop="is_active" :label="$t('userManagement.table.activeHeader')" width="100">
        <template #default="scope">
          {{ scope.row.is_active === 1 ? $t('userManagement.table.activeYes') : $t('userManagement.table.activeNo') }}
        </template>
      </el-table-column>
      <el-table-column :label="$t('userManagement.table.actionsHeader')" width="350">
        <template #default="scope">
          <el-button size="small" @click="handleEdit(scope.row)">{{ $t('userManagement.actions.editButton') }}</el-button>
          <el-button size="small" @click="handleManageRoles(scope.row)">{{ $t('userManagement.actions.manageRolesButton') }}</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.row)">{{ $t('userManagement.actions.deleteButton') }}</el-button>
        </template>
      </el-table-column>
    </el-table>
    

    <!-- Role Management Dialog commented out for diagnosis -->
    
    <el-dialog
      v-model="roleDialogVisible"
      :title="$t('userManagement.roleDialog.title')"
      width="500px"
      @close="clearRoleMessage"
    >
      <p>{{ $t('userManagement.roleDialog.managingUser') }} <strong>{{ selectedUser?.username }}</strong></p>

      <el-select
        v-model="selectedRoleToAssign"
        :placeholder="$t('userManagement.roleDialog.selectRolePlaceholder')"
        style="width: 100%; margin-bottom: 20px;"
      >
        <el-option
          v-for="role in availableRoles"
          :key="role.id"
          :label="role.name"
          :value="role.id"
        ></el-option>
      </el-select>
      <el-button type="primary" @click="assignRole" :disabled="!selectedRoleToAssign">{{ $t('userManagement.roleDialog.assignButton') }}</el-button>

      <div style="margin-top: 20px;">
        <p>{{ $t('userManagement.roleDialog.assignedRoles') }}</p>
        <el-tag
          v-for="role in userRoles"
          :key="role.id"
          closable
          @close="removeRole(role)"
          style="margin-right: 5px;"
        >
          {{ role.name }}
        </el-tag>
      </div>

      <div v-if="roleMessage.text" :class="['role-message', roleMessage.type]">
        {{ roleMessage.text }}
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="roleDialogVisible = false">{{ $t('userManagement.roleDialog.cancelButton') }}</el-button>
        </span>
      </template>
    </el-dialog>
    

    <!-- Edit User Dialog commented out for diagnosis -->
    
    <el-dialog v-model="editDialogVisible" :title="$t('userManagement.editDialog.title')" width="500px">
      <el-form v-if="editingUser" :model="editingUser" label-width="120px">
        <el-form-item :label="$t('userManagement.table.usernameHeader')">
          <el-input v-model="editingUser.username"></el-input>
        </el-form-item>
        <el-form-item :label="$t('userManagement.table.emailHeader')">
          <el-input v-model="editingUser.email"></el-input>
        </el-form-item>
        <el-form-item :label="$t('userManagement.table.phoneHeader')">
          <el-input v-model="editingUser.phone"></el-input>
        </el-form-item>
        <el-form-item :label="$t('userManagement.table.departmentHeader')">
          <el-input v-model="editingUser.department"></el-input>
        </el-form-item>
        <el-form-item :label="$t('userManagement.table.activeHeader')">
           <el-select v-model="editingUser.is_active" :placeholder="$t('userManagement.editDialog.selectStatusPlaceholder')">
            <el-option :label="$t('userManagement.table.activeYes')" :value="1"></el-option>
            <el-option :label="$t('userManagement.table.activeNo')" :value="0"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">{{ $t('userManagement.editDialog.cancelButton') }}</el-button>
          <el-button type="primary" @click="saveUser">{{ $t('userManagement.editDialog.saveButton') }}</el-button>
        </span>
      </template>
    </el-dialog>
    
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { ElTable, ElTableColumn, ElButton, ElMessage, ElDialog, ElSelect, ElOption, ElTag, ElMessageBox, ElForm, ElFormItem, ElInput } from 'element-plus'; // Import Element Plus components
import { getUsers, getRoles, getUserRoles, assignRoleToUser, removeRoleFromUser, deleteUser, updateUser, User, Role } from '@/services/apiService'; // Import API service and interfaces
import { useI18n } from 'vue-i18n'; // Import useI18n

export default defineComponent({
  name: 'UserManagement',
  components: {
    ElTable,
    ElTableColumn,
    ElButton,
    ElDialog,
    ElSelect,
    ElOption,
    ElTag,
    ElForm, // Added ElForm
    ElFormItem, // Added ElFormItem
    ElInput, // Added ElInput
  },
  setup() {
    const { t } = useI18n(); // Get the translation function

    const users = ref<User[]>([]);
    const loading = ref(true);

    const roleDialogVisible = ref(false);
    const selectedUser = ref<User | null>(null);
    const availableRoles = ref<Role[]>([]);
    const userRoles = ref<Role[]>([]);
    const selectedRoleToAssign = ref<any | null>(null); // Changed type to any | null

    const roleMessage = ref<{ type: 'success' | 'error' | null; text: string | null }>({ type: null, text: null }); // Reactive property for role management messages

    const editDialogVisible = ref(false); // Added state for edit dialog
    const editingUser = ref<User | null>(null); // Added state for user being edited


    const fetchUsers = async () => {
      loading.value = true;
      try {
        users.value = await getUsers();
      } catch (error: any) {
        ElMessage.error(t('userManagement.messages.fetchUsersFailed') + error.message);
      } finally {
        loading.value = false;
      }
    };

    const fetchRoles = async () => {
      try {
        availableRoles.value = await getRoles();
      } catch (error: any) {
        ElMessage.error(t('userManagement.messages.fetchRolesFailed') + error.message);
      }
    };

    const fetchUserRoles = async (userId: number) => {
       try {
        userRoles.value = await getUserRoles(userId);
      } catch (error: any) {
        ElMessage.error(t('userManagement.messages.fetchUserRolesFailed') + error.message);
        userRoles.value = []; // Clear roles on error
      }
    };


    const handleEdit = (user: User) => {
      editingUser.value = { ...user }; // Create a copy to avoid modifying the table data directly
      editDialogVisible.value = true;
    };

    const saveUser = async () => {
      if (!editingUser.value) return;
      try {
        await updateUser(editingUser.value.id, editingUser.value);
        ElMessage.success(t('userManagement.messages.updateUserSuccess'));
        editDialogVisible.value = false;
        fetchUsers(); // Refresh the user list
      } catch (error: any) {
        ElMessage.error(t('userManagement.messages.updateUserFailed') + error.message);
      }
    };

    const handleDelete = async (user: User) => {
      try {
        await ElMessageBox.confirm(
          t('userManagement.messages.deleteConfirmation', { username: user.username }),
          t('userManagement.messages.deleteWarningTitle'),
          {
            confirmButtonText: t('userManagement.actions.deleteButton'),
            cancelButtonText: t('userManagement.roleDialog.cancelButton'),
            type: 'warning',
          }
        );
        await deleteUser(user.id);
        ElMessage.success(t('userManagement.messages.deleteSuccess'));
        fetchUsers(); // Refresh the user list
      } catch (error: any) {
        if (error !== 'cancel') { // Check if the error is not due to user cancelling
          ElMessage.error(t('userManagement.messages.deleteFailed') + error.message);
        }
      }
    };

    const handleManageRoles = async (user: User) => {
      selectedUser.value = user;
      roleDialogVisible.value = true;
      await fetchRoles(); // Fetch all available roles
      await fetchUserRoles(user.id); // Fetch roles assigned to the user
    };

    const assignRole = async () => {
      if (!selectedUser.value || selectedRoleToAssign.value === null) { // Check for null explicitly
        ElMessage.warning(t('userManagement.messages.selectUserAndRoleWarning'));
        return;
      }
      try {
        // Ensure selectedRoleToAssign is treated as a number for the API call
        await assignRoleToUser({ user_id: selectedUser.value.id, role_id: selectedRoleToAssign.value as number });
        roleMessage.value = { type: 'success', text: t('userManagement.messages.assignRoleSuccess') }; // Display success message in dialog
        selectedRoleToAssign.value = null; // Clear selection
        await fetchUserRoles(selectedUser.value.id); // Refresh user roles
      } catch (error: any) {
        roleMessage.value = { type: 'error', text: t('userManagement.messages.assignRoleFailed') + error.message }; // Display error message in dialog
      }
    };

    const removeRole = async (role: Role) => {
      if (!selectedUser.value) return;
      try {
        await removeRoleFromUser({ user_id: selectedUser.value.id, role_id: role.id });
        roleMessage.value = { type: 'success', text: t('userManagement.messages.removeRoleSuccess') }; // Display success message in dialog
        await fetchUserRoles(selectedUser.value.id); // Refresh user roles
      } catch (error: any) {
        roleMessage.value = { type: 'error', text: t('userManagement.messages.removeRoleFailed') + error.message }; // Display error message in dialog
      }
    };

    const clearRoleMessage = () => {
      roleMessage.value = { type: null, text: null };
    };


    onMounted(() => {
      fetchUsers();
    });

    return {
      users,
      loading,
      roleDialogVisible,
      selectedUser,
      availableRoles,
      userRoles,
      selectedRoleToAssign,
      roleMessage, // Expose roleMessage to template
      editDialogVisible, // Expose edit dialog state
      editingUser, // Expose editing user state
      handleEdit,
      saveUser, // Expose save user function
      handleDelete,
      handleManageRoles,
      assignRole,
      removeRole,
      clearRoleMessage, // Expose clearRoleMessage to template
      t, // Expose t for template usage
    };
  },
});
</script>

<style scoped>
.user-management-container {
  padding: 20px;
}

.role-message {
  margin-top: 15px;
  padding: 10px;
  border-radius: 4px;
}

.role-message.success {
  color: #67c23a; /* El-message success color */
  background-color: #f0f9eb; /* El-message success background */
  border: 1px solid #e1f3d8;
}

.role-message.error {
  color: #f56c6c; /* El-message error color */
  background-color: #fef0f0; /* El-message error background */
  border: 1px solid #fde2e2;
}
</style>