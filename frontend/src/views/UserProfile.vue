<template>
  <div class="user-profile-container">
    <h1>{{ $t('userProfile.title') }}</h1>
    <el-form :model="userData" label-width="120px">
      <el-form-item :label="$t('userProfile.username')">
        <el-input v-model="userData.username"></el-input>
      </el-form-item>
      <el-form-item :label="$t('userProfile.email')">
        <el-input v-model="userData.email"></el-input>
      </el-form-item>
      <el-form-item :label="$t('userProfile.phone')">
        <el-input v-model="userData.phone"></el-input>
      </el-form-item>
      <el-form-item :label="$t('userProfile.department')">
        <el-input v-model="userData.department"></el-input>
      </el-form-item>
      <el-form-item :label="$t('userProfile.firstName')">
        <el-input v-model="userData.first_name"></el-input>
      </el-form-item>
      <el-form-item :label="$t('userProfile.surname')">
        <el-input v-model="userData.surname"></el-input>
      </el-form-item>
      <el-form-item :label="$t('userProfile.isActive')">
        <el-switch v-model="userData.is_active"></el-switch>
      </el-form-item>

      <el-form-item :label="$t('userProfile.avatar')">
        <div class="avatar-upload-container">
          <el-avatar v-if="userData.avatar" :src="userData.avatar" :size="100" shape="square"></el-avatar>
          <el-upload
            class="avatar-uploader"
            action="#"
            :show-file-list="false"
            :before-upload="beforeAvatarUpload"
            :http-request="uploadAvatar"
          >
            <el-button type="primary">{{ $t('userProfile.selectAvatar') }}</el-button>
          </el-upload>
        </div>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="saveUserData">{{ $t('userProfile.saveButton') }}</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElForm, ElFormItem, ElInput, ElButton, ElSwitch, ElMessage, ElUpload, ElAvatar } from 'element-plus'; // Import Element Plus components and ElMessage
import { fetchUserProfile, updateUserProfile, UserProfileData, uploadUserAvatar } from '../services/authService'; // Import API functions and UserProfileData interface

const { t } = useI18n();

const userData = ref<UserProfileData>({
  username: '',
  email: null, // Initialize with null to match UserProfileData type
  phone: null, // Initialize with null to match UserProfileData type
  department: '', // Initialize department
  first_name: null, // Initialize first_name
  surname: null, // Initialize surname
  is_active: true,
  avatar: null, // Initialize avatar field
});

const fetchUserData = async () => {
  try {
    const user = await fetchUserProfile();
    userData.value = user;
  } catch (error) {
    console.error('Error fetching user profile:', error);
    ElMessage.error(t('userProfile.fetchError')); // Assuming a fetchError translation key exists
  }
};

const saveUserData = async () => {
  try {
    await updateUserProfile(userData.value);
    ElMessage.success(t('userProfile.saveSuccess'));
  } catch (error) {
    console.error('Error saving user profile:', error);
    ElMessage.error(t('userProfile.saveError')); // Assuming a saveError translation key exists
  }
};

const beforeAvatarUpload = (rawFile: any) => {
  // Basic file type and size validation (adjust as needed)
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
  const isAllowedType = allowedTypes.includes(rawFile.type);
  const isLt2M = rawFile.size / 1024 / 1024 < 2; // Max 2MB

  if (!isAllowedType) {
    ElMessage.error(t('userProfile.avatarUpload.invalidType')); // Assuming translation key
    return false;
  }
  if (!isLt2M) {
    ElMessage.error(t('userProfile.avatarUpload.sizeExceeded')); // Assuming translation key
    return false;
  }
  return true;
};

const uploadAvatar = async (options: any) => {
  try {
    // Assuming uploadUserAvatar function handles the file upload API call
    const response = await uploadUserAvatar(options.file);
    // Assuming the backend returns the URL of the uploaded avatar
    userData.value.avatar = response.avatar_url; // Update avatar URL in userData
    ElMessage.success(t('userProfile.avatarUpload.success')); // Assuming translation key
  } catch (error) {
    console.error('Error uploading avatar:', error);
    ElMessage.error(t('userProfile.avatarUpload.failed') + (error as any).message); // Assuming translation key
  }
};


onMounted(() => {
  fetchUserData();
});

// Script setup for UserProfile view
</script>


<style scoped>
.user-profile-container {
  padding: 20px;
}

.user-profile-container h1 {
  color: var(--el-text-color-primary);
  margin-bottom: 20px;
}

.user-profile-container p {
  color: var(--el-text-color-regular);
}

.avatar-upload-container {
  display: flex;
  align-items: center;
  gap: 20px;
}
</style>