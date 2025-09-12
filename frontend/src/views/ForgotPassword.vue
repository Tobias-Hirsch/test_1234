<template>
  <div class="forgot-password-container">
    <el-card class="forgot-password-card">
      <template #header>
        <div class="card-header">
          <span>{{ $t('forgotPassword.title') }}</span>
        </div>
      </template>
      <el-form :model="forgotPasswordForm" :rules="forgotPasswordRules" ref="forgotPasswordFormRef" label-position="top">
        <el-form-item :label="$t('forgotPassword.emailOrPhone')" prop="email_or_phone">
          <el-input v-model="forgotPasswordForm.email_or_phone" :placeholder="$t('forgotPassword.emailOrPhonePlaceholder')"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleForgotPassword" style="width: 100%;">{{ $t('forgotPassword.resetButton') }}</el-button>
        </el-form-item>
        <el-form-item>
          <el-button link @click="goToLogin">{{ $t('forgotPassword.loginLink') }}</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElForm, ElFormItem, ElInput, ElButton, ElCard, ElMessage } from 'element-plus';
import type { FormInstance, FormRules } from 'element-plus';
import { useI18n } from 'vue-i18n';
import { forgotPassword } from '../services/authService'; // Import the forgotPassword service

export default defineComponent({
  name: 'ForgotPassword',
  components: {
    ElForm,
    ElFormItem,
    ElInput,
    ElButton,
    ElCard,
  },
  setup() {
    const router = useRouter();
    const { t } = useI18n();

    const forgotPasswordFormRef = ref<FormInstance>();
    const forgotPasswordForm = ref({
      email_or_phone: '', // Corrected field name
    });

    const forgotPasswordRules: FormRules = {
      email_or_phone: [ // Corrected field name
        { required: true, message: t('forgotPassword.emailOrPhoneRequired'), trigger: 'blur' },
        // Add email or phone format validation if needed
      ],
    };

    const handleForgotPassword = async () => {
      const form = forgotPasswordFormRef.value;
      if (!form) return;

      form.validate(async (valid) => {
        if (valid) {
          console.log('Forgot Password form submitted:', forgotPasswordForm.value);
          try {
            // Call the forgotPassword service
            await forgotPassword(forgotPasswordForm.value);
            ElMessage.success(t('forgotPassword.requestSuccess')); // Assuming a success message key
            // Optionally redirect to login page or show a message
            // router.push('/login');
          } catch (error: any) {
            console.error('Forgot password request failed:', error);
            ElMessage.error(error.message || t('forgotPassword.requestFailed')); // Assuming a failure message key
          }
        } else {
          console.log('Forgot Password form validation failed');
        }
      });
    };

    const goToLogin = () => {
      router.push('/login');
    };

    return {
      forgotPasswordFormRef,
      forgotPasswordForm,
      forgotPasswordRules,
      handleForgotPassword,
      goToLogin,
      t, // Expose t for template usage
    };
  },
});
</script>

<style scoped>
.forgot-password-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--el-bg-color-page); /* Use theme variable */
}

.forgot-password-card {
  width: 400px;
  max-width: 90%;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  background-color: var(--el-bg-color-overlay); /* Use theme variable */
  color: var(--el-text-color-primary); /* Use theme variable */
}

.card-header {
  font-size: 1.2em;
  font-weight: bold;
  text-align: center;
  color: var(--el-text-color-primary); /* Use theme variable */
}
</style>