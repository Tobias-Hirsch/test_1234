import { ref, inject } from 'vue';
import { ElMessage } from 'element-plus';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/stores/auth';
import { updateUser, updateBotAvatar, uploadAvatar } from '@/services/apiService';

export function useAvatarManagement() {
  const { t } = useI18n();
  const authStore = useAuthStore();
  const { user } = authStore;

  const showAvatarDialog = ref(false);
  const selectedUserAvatar = ref('https://avatars.githubusercontent.com/u/76239030?v=4'); // Default user avatar
  const selectedBotAvatar = ref('https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'); // Default bot avatar
  const avatarFileInputRef = ref<HTMLInputElement | null>(null); // Ref for the hidden avatar file input
  const avatarFile = ref<File | null>(null); // To store the selected avatar file

  // Predefined Element Plus avatar options (example URLs)
  const avatarOptions = ref([
    'https://avatars.githubusercontent.com/u/76239030?v=4', // Current user avatar
    'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png', // Bot avatar (as an option)
    'https://fuss10.elemecdn.com/e/5d/4a731a90594a4af544c0c25941171jpeg.jpeg',
    'https://fuss10.elemecdn.com/8/27/f01c15bb73e1ef3793e64e6b7bbccjpeg.jpeg',
    'https://fuss10.elemecdn.com/1/82/36771ab7fd56290798f9d6777012dc5jpeg.jpeg',
  ]);

  let avatarToChange: 'user' | 'bot' = 'user'; // To track which avatar is being changed

  const openAvatarDialog = (sender: 'user' | 'bot') => {
    console.log(`Opening avatar dialog for ${sender}`);
    avatarToChange = sender;
    showAvatarDialog.value = true;
  };

  const selectAvatar = async (url: string) => {
    if (avatarToChange === 'user') {
      selectedUserAvatar.value = url;
      if (user.value && user.value.id) {
        try {
          await updateUser(user.value.id, { avatar: url });
          ElMessage.success(t('rostiChat.avatarUpdateSuccess'));
          authStore.setUser({ ...user.value, avatar: url });
        } catch (error: any) {
          console.error("Error updating user avatar:", error);
          ElMessage.error(`${t('rostiChat.avatarUpdateFailed')}: ${error.message}`);
        }
      }
    } else {
      selectedBotAvatar.value = url;
      try {
        await updateBotAvatar(url);
        ElMessage.success(t('rostiChat.botAvatarUpdateSuccess'));
      } catch (error: any) {
        console.error("Error updating bot avatar:", error);
        ElMessage.error(`${t('rostiChat.botAvatarUpdateFailed')}: ${error.message}`);
      }
    }
    showAvatarDialog.value = false;
  };

  const handleAvatarFileChange = async (event: Event) => {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
      const file = target.files[0];
      const allowedImageTypes = ['image/jpeg', 'image/png', 'image/gif'];
      if (!allowedImageTypes.includes(file.type)) {
        ElMessage.error(t('rostiChat.invalidAvatarFileType'));
        return;
      }
      if (file.size > 2 * 1024 * 1024) { // 2MB limit
        ElMessage.error(t('rostiChat.avatarFileSizeExceeded'));
        return;
      }

      avatarFile.value = file;
      let uploadedUrl: string | undefined;

      try {
        const response = await uploadAvatar(file);
        uploadedUrl = response.avatar_url;

        if (avatarToChange === 'user') {
          selectedUserAvatar.value = uploadedUrl;
          if (user.value && user.value.id) {
            await updateUser(user.value.id, { avatar: uploadedUrl });
            ElMessage.success(t('rostiChat.avatarUploadSuccess'));
            authStore.setUser({ ...user.value, avatar: uploadedUrl });
          }
        } else {
          selectedBotAvatar.value = uploadedUrl;
          console.log("Attempting to update bot avatar with URL:", uploadedUrl);
          await updateBotAvatar(uploadedUrl);
          ElMessage.success(t('rostiChat.botAvatarUploadSuccess'));
        }

        if (uploadedUrl && !avatarOptions.value.includes(uploadedUrl)) {
          avatarOptions.value.push(uploadedUrl);
        }

      } catch (error: any) {
        console.error("Error uploading avatar:", error);
        ElMessage.error(`${t('rostiChat.avatarUploadFailed')}: ${error.message}`);
      } finally {
        if (avatarFileInputRef.value) {
          avatarFileInputRef.value.value = '';
        }
        avatarFile.value = null;
        showAvatarDialog.value = false;
      }
    }
  };

  return {
    showAvatarDialog,
    selectedUserAvatar,
    selectedBotAvatar,
    avatarFileInputRef,
    avatarFile,
    avatarOptions,
    openAvatarDialog,
    selectAvatar,
    handleAvatarFileChange,
  };
}