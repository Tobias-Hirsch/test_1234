<template>
  <div class="reset-password-container">
    <el-card class="reset-password-card">
      <template #header>
        <div class="card-header">
          <span>{{ $t('resetPassword.title') }}</span>
        </div>
      </template>
      <el-form :model="resetPasswordForm" :rules="resetPasswordRules" ref="resetPasswordFormRef" label-position="top">
        <el-form-item :label="$t('resetPassword.token')" prop="token">
          <el-input v-model="resetPasswordForm.token" :placeholder="$t('resetPassword.tokenPlaceholder')"></el-input>
        </el-form-item>
        <el-form-item :label="$t('resetPassword.newPassword')" prop="new_password">
          <el-input type="password" v-model="resetPasswordForm.new_password" :placeholder="$t('resetPassword.newPasswordPlaceholder')" show-password></el-input>
        </el-form-item>
        <el-form-item :label="$t('resetPassword.confirmPassword')" prop="confirm_password">
          <el-input type="password" v-model="resetPasswordForm.confirm_password" :placeholder="$t('resetPassword.confirmPasswordPlaceholder')" show-password></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleResetPassword" style="width: 100%;">{{ $t('resetPassword.resetButton') }}</el-button>
        </el-form-item>
        <el-form-item>
          <el-button type="text" link @click="goToLogin">{{ $t('resetPassword.loginLink') }}</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElForm, ElFormItem, ElInput, ElButton, ElCard, ElMessage } from 'element-plus';
import type { FormInstance, FormRules } from 'element-plus';
import { useI18n } from 'vue-i18n';
import { resetPassword, ResetPasswordData } from '../services/authService'; // Import resetPassword service and interface

export default defineComponent({
  name: 'ResetPassword',
  components: {
    ElForm,
    ElFormItem,
    ElInput,
    ElButton,
    ElCard,
  },
  setup() {
    const router = useRouter();
    const route = useRoute();
    const { t } = useI18n();

    const resetPasswordFormRef = ref<FormInstance>();
    const resetPasswordForm = ref({
      token: route.query.token as string || '', // Get token from query parameter
      new_password: '',
      confirm_password: '',
    });

    const validateConfirmPassword = (rule: any, value: string, callback: any) => {
      if (value === '') {
        callback(new Error(t('resetPassword.confirmPasswordRequired')));
      } else if (value !== resetPasswordForm.value.new_password) {
        callback(new Error(t('resetPassword.passwordMismatch')));
      } else {
        callback();
      }
    };

    const resetPasswordRules: FormRules = {
      token: [
        { required: true, message: t('resetPassword.tokenRequired'), trigger: 'blur' },
      ],
      new_password: [
        { required: true, message: t('resetPassword.newPasswordRequired'), trigger: 'blur' },
        { min: 6, message: t('resetPassword.passwordMinLength'), trigger: 'blur' },
      ],
      confirm_password: [
        { required: true, validator: validateConfirmPassword, trigger: 'blur' },
      ],
    };

    const handleResetPassword = async () => {
      const form = resetPasswordFormRef.value;
      if (!form) return;

      form.validate(async (valid) => {
        if (valid) {
          console.log('Reset Password form submitted:', resetPasswordForm.value);
          try {
            // Call resetPassword service
            const resetData: ResetPasswordData = {
              token: resetPasswordForm.value.token,
              new_password: resetPasswordForm.value.new_password,
            };
            await resetPassword(resetData);
            ElMessage.success(t('resetPassword.resetSuccess'));
            router.push('/login'); // Redirect to login after successful reset
          } catch (error: any) {
            console.error('Password reset failed:', error);
            ElMessage.error(error.message || t('resetPassword.resetFailed'));
          }
        } else {
          console.log('Reset Password form validation failed');
        }
      });
    };

    const goToLogin = () => {
      router.push('/login');
    };

    return {
      resetPasswordFormRef,
      resetPasswordForm,
      resetPasswordRules,
      handleResetPassword,
      goToLogin,
      t, // Expose t for template usage
    };
  },
});
</script>

<style scoped>
.reset-password-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--el-bg-color-page); /* Use theme variable */
}

.reset-password-card {
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