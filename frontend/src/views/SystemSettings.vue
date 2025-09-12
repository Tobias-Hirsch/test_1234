<template>
  <div class="system-settings-container">
    <h1>{{ $t('systemSettings.title') }}</h1>

    <el-form v-if="settings" :model="settings" label-width="200px">
      <el-form-item v-for="(value, key) in settings" :key="key" :label="key">
        <el-switch v-if="typeof value === 'boolean'" v-model="settings[key]"></el-switch>
        <el-input v-else v-model="settings[key]"></el-input>
      </el-form-item>
    </el-form>

    <el-button type="primary" @click="saveSettings">{{ $t('systemSettings.saveButton') }}</el-button>
    <el-button @click="fetchSettings">{{ $t('systemSettings.cancelButton') }}</el-button>

    <p v-if="loading">{{ $t('systemSettings.loading') }}</p>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { ElForm, ElFormItem, ElInput, ElButton, ElMessage, ElSwitch } from 'element-plus';
import { useI18n } from 'vue-i18n';
import { get, post } from '@/services/apiService'; // Import named exports get and post

export default defineComponent({
  name: 'SystemSettings',
  components: {
    ElForm,
    ElFormItem,
    ElInput,
    ElButton,
    ElSwitch,
  },
  setup() {
    const { t } = useI18n();
    const settings = ref<Record<string, any> | null>(null);
    const loading = ref(false);

    const fetchSettings = async () => {
      loading.value = true;
      try {
        const response = await get('/settings/'); // Use the named export get
        settings.value = response; // Assuming the response is the data directly
      } catch (error: any) {
        ElMessage.error(t('systemSettings.messages.fetchFailed') + error.message);
      } finally {
        loading.value = false;
      }
    };

    const saveSettings = async () => {
      if (!settings.value) return;
      loading.value = true;
      try {
        await post('/settings/', settings.value); // Use the named export post
        ElMessage.success(t('systemSettings.messages.saveSuccess'));
      } catch (error: any) {
        ElMessage.error(t('systemSettings.messages.saveFailed') + error.message);
      } finally {
        loading.value = false;
      }
    };

    onMounted(() => {
      fetchSettings();
    });

    return {
      settings,
      loading,
      fetchSettings,
      saveSettings,
      t,
    };
  },
});
</script>

<style scoped>
.system-settings-container {
  padding: 20px;
}
</style>