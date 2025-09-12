<template>
  <div class="activate-account-container">
    <el-card class="activate-card">
      <template #header>
        <div class="card-header">
          <span>{{ $t('activateAccount.title') }}</span>
        </div>
      </template>
      <div v-if="loading">
        <p>{{ $t('activateAccount.activating') }}</p>
      </div>
      <div v-else>
        <p v-if="successMessage">{{ successMessage }}</p>
        <p v-if="errorMessage">{{ errorMessage }}</p>
        <el-button type="primary" @click="goToLogin">{{ $t('activateAccount.goToLogin') }}</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { ElCard, ElButton, ElMessage } from 'element-plus'; // Import Element Plus components and ElMessage
import { activateUser } from '../services/authService'; // Need to add activateUser to authService

const route = useRoute();
const router = useRouter();
const { t } = useI18n();

const loading = ref(true);
const successMessage = ref('');
const errorMessage = ref('');

const activateAccount = async () => {
  const token = route.query.token as string;
  if (!token) {
    errorMessage.value = t('activateAccount.noToken');
    loading.value = false;
    return;
  }

  try {
    // Call the backend activation endpoint
    const response = await activateUser(token); // Need to implement activateUser in authService
    successMessage.value = response.message || t('activateAccount.activationSuccess');
  } catch (error: any) {
    console.error('Account activation failed:', error);
    errorMessage.value = error.message || t('activateAccount.activationFailed');
  } finally {
    loading.value = false;
  }
};

const goToLogin = () => {
  router.push('/login');
};

onMounted(() => {
  activateAccount();
});
</script>

<style scoped>
.activate-account-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--el-bg-color-page);
}

.activate-card {
  width: 400px;
  max-width: 90%;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  background-color: var(--el-bg-color-overlay);
  color: var(--el-text-color-primary);
  text-align: center;
  padding: 20px;
}

.card-header {
  font-size: 1.2em;
  font-weight: bold;
  margin-bottom: 20px;
  color: var(--el-text-color-primary);
}
</style>