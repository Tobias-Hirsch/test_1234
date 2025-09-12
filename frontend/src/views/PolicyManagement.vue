<template>
  <div class="policy-management-container">
    <h2>ABAC 策略管理</h2>

    <!-- 策略列表 -->
    <el-table :data="policies" style="width: 100%" border>
      <el-table-column prop="id" label="ID" width="80"></el-table-column>
      <el-table-column prop="name" label="策略名称"></el-table-column>
      <el-table-column prop="description" label="描述"></el-table-column>
      <el-table-column label="是否启用" width="100">
        <template #default="scope">
          <el-switch
            v-model="scope.row.is_active"
            @change="togglePolicyStatus(scope.row)"
          ></el-switch>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280">
        <template #default="scope">
          <el-button size="small" @click="editPolicy(scope.row)">编辑</el-button>
          <el-button size="small" type="primary" plain @click="clonePolicy(scope.row)">复制</el-button>
          <el-button size="small" type="danger" @click="deletePolicy(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑策略对话框 -->
    <!-- 创建/编辑策略对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="80%"
      top="5vh"
      destroy-on-close
      @close="handleDialogClose"
    >
      <PolicyBuilder
        v-if="dialogVisible"
        :policy-id="editingPolicyId"
        :initial-data="clonedPolicyData"
        @save="handleSavePolicy"
        @cancel="dialogVisible = false"
      />
    </el-dialog>

    <el-button type="primary" @click="createNewPolicy">创建新策略</el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { get, post, put, del } from '@/services/apiService';
import PolicyBuilder from './PolicyManagement/PolicyBuilder.vue';

interface Policy {
  id?: number;
  name: string;
  description: string;
  effect: 'allow' | 'deny';
  actions: string[];
  subjects: any[];
  resources: any[];
  conditions?: any[];
  is_active: boolean;
}

const policies = ref<Policy[]>([]);
const dialogVisible = ref(false);
const isEditMode = ref(false);
const editingPolicyId = ref<number | null>(null);
const clonedPolicyData = ref<Policy | null>(null);

const fetchPolicies = async () => {
  try {
    const data = await get('/policies/'); // 直接获取数据
    // 检查 data 是否存在且为数组
    if (Array.isArray(data)) {
      // 转换 is_active 字段为布尔值
      policies.value = data.map((policy: Policy) => ({
        ...policy,
        is_active: !!policy.is_active // 将 1 转换为 true，0 转换为 false
      }));
    } else {
      console.error('API 返回的数据无效或不是数组:', data);
      policies.value = []; // 清空策略列表
      ElMessage.error('获取策略失败: API 返回数据格式不正确或为空');
    }
  } catch (error: any) {
    console.error('获取策略时发生错误:', error);
    ElMessage.error(`获取策略失败: ${error.message || '未知错误'}`);
  }
};

const createNewPolicy = () => {
  isEditMode.value = false;
  editingPolicyId.value = null;
  clonedPolicyData.value = null;
  dialogVisible.value = true;
};

const editPolicy = (policy: Policy) => {
  isEditMode.value = true;
  editingPolicyId.value = policy.id!;
  clonedPolicyData.value = null;
  dialogVisible.value = true;
};

const clonePolicy = async (policy: Policy) => {
  try {
    const policyToClone = await get(`/policies/${policy.id}`);
    isEditMode.value = false;
    editingPolicyId.value = null;
    clonedPolicyData.value = {
      ...policyToClone,
      id: undefined,
      name: `${policyToClone.name} - copy`,
      is_active: false,
    };
    dialogVisible.value = true;
  } catch (error: any) {
    ElMessage.error(`复制策略失败: ${error.message}`);
  }
};

const handleSavePolicy = async (policyToSave: Omit<Policy, 'id'>) => {
  try {
    // Create a payload with the correct data type for is_active
    const payload = {
      ...policyToSave,
      is_active: policyToSave.is_active ? 1 : 0,
    };

    // Log the final payload before sending to the backend
    console.log('Final payload being sent to API:', JSON.stringify(payload, null, 2));

    if (isEditMode.value && editingPolicyId.value) {
      await put(`/policies/${editingPolicyId.value}`, payload);
      ElMessage.success('策略更新成功');
    } else {
      await post('/policies/', payload);
      ElMessage.success('策略创建成功');
    }
    dialogVisible.value = false;
    fetchPolicies(); // 刷新列表
  } catch (error: any) {
    ElMessage.error(`保存策略失败: ${error.message}`);
  }
};

const handleDialogClose = () => {
  clonedPolicyData.value = null;
};

const dialogTitle = computed(() => {
  if (isEditMode.value) {
    return '编辑策略';
  }
  if (clonedPolicyData.value) {
    return '从现有策略创建 (复制)';
  }
  return '创建新策略';
});

const deletePolicy = async (id: number) => {
  ElMessageBox.confirm('确定要删除此策略吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      try {
        await del(`/policies/${id}`);
        ElMessage.success('策略删除成功');
        fetchPolicies(); // 刷新列表
      } catch (error: any) {
        ElMessage.error(`删除策略失败: ${error.message}`);
      }
    })
    .catch(() => {
      ElMessage.info('已取消删除');
    });
};

const togglePolicyStatus = async (policy: Policy) => {
  try {
    // 仅更新 is_active 状态
    await put(`/policies/${policy.id}`, { is_active: policy.is_active });
    ElMessage.success('策略状态更新成功');
  } catch (error: any) {
    ElMessage.error(`更新策略状态失败: ${error.message}`);
    policy.is_active = !policy.is_active; // 恢复原状态
  }
};

// These functions are no longer needed as we have separate fields
// const formatJson = ...
// const validateJson = ...

onMounted(() => {
  fetchPolicies();
});
</script>