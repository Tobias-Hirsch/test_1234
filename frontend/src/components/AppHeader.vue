<!--
Developer: Jinglu Han
mailbox: admin@de-manufacturing.cn
-->

<template>
    <el-header v-if="isAuthenticated" class="app-header">
      <div class="header-content">
        <el-button
          class="aside-toggle-btn"
          icon="Menu"
          link
          @click="toggleAside"
          style="margin-right: 10px;"
        />
        <!-- 其它 header 内容可在此添加 -->
      </div>
      <div class="header-actions">
        <el-avatar v-if="authStore.user?.avatar" :src="authStore.user.avatar" :size="30" class="user-avatar"></el-avatar>
        <el-button link @click="goToProfile">
          {{ authStore.user?.username || $t('header.user') }}
        </el-button>
        <el-button link @click="handleLogout">{{ $t('header.logout') }}</el-button>
        
        <el-switch
          v-if="showThemeSwitcher"
          v-model="isDarkMode"
          inline-prompt
          :active-icon="Moon"
          :inactive-icon="Sunny"
          @change="toggleTheme"
        />
        
      </div>
    </el-header>
  </template>
  
  <script setup lang="ts">
  import { inject, computed } from 'vue'; // Import watch, onMounted, onUnmounted, computed
  import { Sunny, Moon, Menu } from '@element-plus/icons-vue';
  import { useI18n } from 'vue-i18n';
  import { useRouter } from 'vue-router';
  import { useAuthStore } from '@/stores/auth';
  import { ElAvatar } from 'element-plus'; // Import ElAvatar
  
  const { t } = useI18n();
  const router = useRouter();
  const authStore = useAuthStore();
  const isAuthenticated = computed(() => authStore.isAuthenticated); // Make isAuthenticated a computed property
  const isDarkMode = inject('isDarkMode');
  const toggleTheme = inject('toggleTheme');
  const toggleAside = inject('toggleAside');
  
  // Control theme switcher visibility based on environment variable
  const showThemeSwitcher = computed(() => {
    const multiThemeEnv = import.meta.env.VITE_MULTI_THEME;
    return multiThemeEnv === 'true' || multiThemeEnv === true;
  });

  // Add logs for debugging
  const handleLogout = () => {
    authStore.logout();
  };
  const goToProfile = () => {
    router.push('/profile');
  };
  </script>
  
  <style scoped>
  .app-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    height: 80px;
    min-height: 80px;
    background: #fff;
    }
  .dark-mode .app-header {
    background: #1a1a1a;
  }
  .header-content {
    display: flex;
    align-items: center;
    height: 100%;
  }
  .header-actions {
    display: flex;
    align-items: center;
    gap: 10px;
    height: 100%;
  }
  .aside-toggle-btn {
    font-size: 20px;
  }
  .user-avatar {
    margin-right: 5px; /* Add some spacing between avatar and username */
  }
  </style>