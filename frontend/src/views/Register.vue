<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <el-button link @click="goToLogin" class="back-button">
            <el-icon><ArrowLeft /></el-icon>
          </el-button>
          <span>{{ $t('register.title') }}</span>
        </div>
      </template>
      <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" label-position="top">
        <el-form-item :label="$t('register.username')" prop="username">
          <el-input v-model="registerForm.username" :placeholder="$t('register.usernamePlaceholder')"></el-input>
        </el-form-item>
        <el-form-item :label="$t('register.email')" prop="email">
          <el-input v-model="registerForm.email" :placeholder="$t('register.emailPlaceholder')"></el-input>
        </el-form-item>
        <el-form-item :label="$t('register.phone')" prop="phone">
          <el-input v-model="registerForm.phone" :placeholder="$t('register.phonePlaceholder')"></el-input>
        </el-form-item>
        <el-form-item :label="$t('userProfile.department')" prop="department">
          <el-input v-model="registerForm.department" :placeholder="$t('userProfile.department')"></el-input>
        </el-form-item>
        <el-form-item :label="$t('userProfile.firstName')" prop="first_name">
          <el-input v-model="registerForm.first_name" :placeholder="$t('userProfile.firstName')"></el-input>
        </el-form-item>
        <el-form-item :label="$t('userProfile.surname')" prop="surname">
          <el-input v-model="registerForm.surname" :placeholder="$t('userProfile.surname')"></el-input>
        </el-form-item>
        <el-form-item :label="$t('register.password')" prop="password">
          <el-input type="password" v-model="registerForm.password" :placeholder="$t('register.passwordPlaceholder')" show-password></el-input>
        </el-form-item>
        <el-form-item :label="$t('register.confirmPassword')" prop="confirmPassword">
          <el-input type="password" v-model="registerForm.confirmPassword" :placeholder="$t('register.confirmPasswordPlaceholder')" show-password></el-input>
        </el-form-item>
        <el-form-item :label="$t('register.captcha')" prop="captcha">
          <el-input v-model="registerForm.captcha" :placeholder="$t('register.captchaPlaceholder')"></el-input>
          <img :src="captchaImageUrl" @click="refreshCaptcha" alt="Captcha Image" class="captcha-image">
        </el-form-item>
        <el-form-item>
           <el-button type="primary" @click="handleRegister" style="width: 100%;">{{ $t('register.registerButton') }}</el-button>
         </el-form-item>
         <el-form-item>
           <el-button link @click="goToLogin">{{ $t('register.loginLink') }}</el-button>
         </el-form-item>
       </el-form>
    </el-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'; // Import onMounted
import { useRouter } from 'vue-router';
import { ElForm, ElFormItem, ElInput, ElButton, ElCard, ElMessage, ElIcon } from 'element-plus'; // Add ElIcon
import type { FormInstance, FormRules } from 'element-plus';
import { useI18n } from 'vue-i18n';
import { register, verifyCaptcha } from '../services/authService'; // Import the register and verifyCaptcha services
import { ArrowLeft } from '@element-plus/icons-vue'; // Import ArrowLeft icon

export default defineComponent({
  name: 'Register',
  components: {
    ElForm,
    ElFormItem,
    ElInput,
    ElButton,
    ElCard,
    ElIcon, // Add ElIcon
    ArrowLeft, // Add ArrowLeft icon component
  },
  setup() {
    const router = useRouter();
    const { t } = useI18n();

    const registerFormRef = ref<FormInstance>();
    const registerForm = ref({
      username: '',
      email: '',
      phone: '',
      department: '', // Add department
      first_name: '', // Add first_name, initialize with empty string
      surname: '', // Add surname, initialize with empty string
      password: '',
      confirmPassword: '',
      captcha: '', // Add captcha field
    });

    const captchaImageUrl = ref<string | undefined>(undefined); // To display the captcha image
    const currentCaptchaId = ref<string | null>(null); // To store the current captcha ID
    const captchaEndpoint = '/api/captcha'; // Backend endpoint for captcha

    const refreshCaptcha = async () => {
      try {
        // Always fetch from the backend endpoint
        const response = await fetch(captchaEndpoint);
        if (!response.ok) {
          throw new Error(`Failed to fetch captcha: ${response.statusText}`);
        }
        // Get captcha ID from response header
        const captchaId = response.headers.get('captcha-id');
        if (!captchaId) {
          throw new Error('Captcha ID not found in response headers');
        }
        currentCaptchaId.value = captchaId;

        // Get image blob and create object URL
        const imageBlob = await response.blob();
        // Revoke previous object URL if it exists
        if (captchaImageUrl.value && captchaImageUrl.value.startsWith('blob:')) {
          URL.revokeObjectURL(captchaImageUrl.value);
        }
        captchaImageUrl.value = URL.createObjectURL(imageBlob); // Update captchaImageUrl to display the image

      } catch (error) {
        console.error('Error refreshing captcha:', error);
        ElMessage.error(t('register.captchaLoadFailed')); // Assuming a captchaLoadFailed translation key exists
        // Clear captcha image and ID on error
        if (captchaImageUrl.value && captchaImageUrl.value.startsWith('blob:')) {
           URL.revokeObjectURL(captchaImageUrl.value);
        }
        captchaImageUrl.value = undefined;
        currentCaptchaId.value = null;
      }
    };

    // Fetch captcha on component mount
    onMounted(() => {
      refreshCaptcha();
    });

    const validateConfirmPassword = (rule: any, value: string, callback: any) => {
      if (value === '') {
        callback(new Error(t('register.confirmPasswordRequired')));
      } else if (value !== registerForm.value.password) {
        callback(new Error(t('register.passwordMismatch')));
      } else {
        callback();
      }
    };

    const registerRules: FormRules = {
      username: [
        { required: true, message: t('register.usernameRequired'), trigger: 'blur' },
      ],
      email: [
        { required: true, message: t('register.emailRequired'), trigger: 'blur' },
        { type: 'email', message: t('register.emailInvalid'), trigger: ['blur', 'change'] },
      ],
      phone: [
        { required: true, message: t('register.phoneRequired'), trigger: 'blur' },
        // Add phone number format validation if needed
      ],
      department: [ // Add department validation
        { required: true, message: t('userProfile.departmentRequired'), trigger: 'blur' }, // Assuming a departmentRequired translation key exists
      ],
      password: [
        { required: true, message: t('register.passwordRequired'), trigger: 'blur' },
        { min: 6, message: t('register.passwordMinLength'), trigger: 'blur' },
      ],
      confirmPassword: [
        { required: true, validator: validateConfirmPassword, trigger: 'blur' },
      ],
      captcha: [ // Add captcha validation
        { required: true, message: t('register.captchaRequired'), trigger: 'blur' }, // Assuming a captchaRequired translation key exists
      ],
    };

    const handleRegister = async () => {
      const form = registerFormRef.value;
      if (!form) return;

      form.validate(async (valid) => {
        if (valid) {
          console.log('Register form submitted:', registerForm.value);
          try {
            // Verify captcha first
            if (!currentCaptchaId.value) {
              ElMessage.error(t('register.captchaRequired')); // Ensure captcha is loaded
              return;
            }
            await verifyCaptcha({
              captcha_id: currentCaptchaId.value, // Use the stored captcha ID
              captcha_input: registerForm.value.captcha,
            });
            // Clear captcha after successful verification to prevent reuse
            if (captchaImageUrl.value && captchaImageUrl.value.startsWith('blob:')) {
               URL.revokeObjectURL(captchaImageUrl.value);
            }
            captchaImageUrl.value = undefined;
            currentCaptchaId.value = null;

            // If captcha verification is successful, proceed with registration
            await register(registerForm.value);
            ElMessage.success(t('register.registrationSuccessActivation'));
            // Redirect to login page after successful registration
            router.push('/login');
          } catch (error: any) {
            console.error('Registration failed:', error);
            // Check if the error is from captcha verification
            if (error.message && error.message.includes('Incorrect captcha')) {
              ElMessage.error(t('register.captchaIncorrect')); // Assuming a captchaIncorrect translation key exists
              refreshCaptcha(); // Refresh captcha on failure
            } else {
              ElMessage.error(error.message || t('register.registerFailed'));
            }
          }
        } else {
          console.log('Register form validation failed');
        }
      });
    };

    const goToLogin = () => {
      router.push('/login');
    };

    return {
      registerFormRef,
      registerForm,
      registerRules,
      handleRegister,
      goToLogin,
      t, // Expose t for template usage
      captchaImageUrl, // Expose captchaImageUrl (now an object URL)
      refreshCaptcha, // Expose refreshCaptcha
      currentCaptchaId, // Expose currentCaptchaId (optional, for debugging)
    };
  },
  // Clean up the object URL when the component is unmounted
  beforeUnmount() {
    // Check if captchaImageUrl is a blob URL before revoking
    if (typeof this.captchaImageUrl === 'string' && this.captchaImageUrl.startsWith('blob:')) {
      URL.revokeObjectURL(this.captchaImageUrl);
    }
  }
});
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--el-bg-color-page); /* Use theme variable */
}

.register-card {
  width: 400px;
  max-width: 90%;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  background-color: var(--el-bg-color-overlay); /* Use theme variable */
  color: var(--el-text-color-primary); /* Use theme variable */
}

.card-header {
  display: flex; /* Use flexbox */
  align-items: center; /* Vertically align items */
  font-size: 1.2em;
  font-weight: bold;
  color: var(--el-text-color-primary); /* Use theme variable */
}

.card-header span {
  flex-grow: 1; /* Allow the title to take up available space */
  text-align: center; /* Center the title */
}

.back-button {
  margin-right: 10px; /* Add some space between the button and the title */
  font-size: 1.2em; /* Match font size of the header */
}

.captcha-image {
  cursor: pointer;
  vertical-align: middle;
  margin-left: 10px;
}
</style>

