<template>
  <div v-if="showPreviewDrawer" class="preview-drawer-overlay" @click="closeDrawer">
    <div class="preview-drawer" @click.stop>
      <div class="drawer-header">
        <h3>{{ t('ragEdit.filePreviewTitle') }}</h3>
        <el-button type="info" size="small" @click="closeDrawer">{{ t('ragEdit.closeButton') }}</el-button>
      </div>
      <div class="drawer-content">
        <!-- Render content based on file type -->
        <div v-if="previewFileType === 'text'">
          <pre>{{ previewContent as string }}</pre>
        </div>
        <div v-else-if="previewFileType === 'image'">
          <img v-if="previewUrl" :src="previewUrl" alt="File Preview" style="max-width: 100%; height: auto;">
        </div>
        <div v-else-if="previewFileType === 'pdf'">
           <iframe v-if="previewUrl" :src="previewUrl" width="100%" height="500px"></iframe>
        </div>
        <div v-else>
          <p>{{ t('ragEdit.cannotPreviewMessage') }}</p>
          <!-- Display content if it's a string, otherwise indicate type -->
          <p>{{ t('ragEdit.contentIfAvailableLabel') }}: {{ typeof previewContent === 'string' ? previewContent : `[${previewFileType} content]` }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, watch, ref, onUnmounted, type PropType } from 'vue'; // Import PropType
import { useI18n } from 'vue-i18n'; // Import useI18n
import { ElButton } from 'element-plus';

// Define a type for the preview content prop
type PreviewContent = string | ArrayBuffer | null | undefined;

export default defineComponent({
  name: 'FilePreviewDrawer',
  components: {
    ElButton,
  },
  props: {
    showPreviewDrawer: {
      type: Boolean,
      required: true,
    },
    previewContent: {
      type: [String, Object, null] as PropType<PreviewContent>, // Use PropType for correct typing
      default: null,
    },
    previewFileType: {
      type: String,
      default: null,
    },
    accessLevel: { // Add accessLevel prop
      type: String,
      default: undefined,
    },
  },
  emits: ['close'],
  setup(props, { emit }) {
    const { t } = useI18n(); // Use useI18n directly

    const closeDrawer = () => {
      emit('close');
    };

    const previewUrl = ref<string | undefined>(undefined);

    // Watch for changes in previewContent and previewFileType to create a Blob URL if necessary
    watch([() => props.previewContent, () => props.previewFileType], ([newContent, newType]) => {
      // Revoke previous Blob URL if it exists
      if (previewUrl.value && previewUrl.value.startsWith('blob:')) {
        URL.revokeObjectURL(previewUrl.value);
        previewUrl.value = undefined;
      }

      if (newContent instanceof ArrayBuffer && (newType === 'image' || newType === 'pdf')) {
        // Create a Blob from ArrayBuffer and generate a Blob URL
        const blob = new Blob([newContent], { type: newType === 'image' ? 'image/*' : 'application/pdf' });
        previewUrl.value = URL.createObjectURL(blob);
      } else if (typeof newContent === 'string' && (newType === 'image' || newType === 'pdf' || newType === 'link')) {
         // If content is a string and type is image, pdf, or link, assume it's a URL
         previewUrl.value = newContent;
      } else {
        previewUrl.value = undefined; // Clear URL for other types or null content
      }
    }, { immediate: true }); // Run immediately on component mount

    // Clean up Blob URL on component unmount
    onUnmounted(() => {
      if (previewUrl.value && previewUrl.value.startsWith('blob:')) {
        URL.revokeObjectURL(previewUrl.value);
      }
    });


    return {
      t,
      closeDrawer,
      previewUrl, // Expose previewUrl to the template
    };
  },
});
</script>

<style scoped>
/* Styles for the drawer */
.preview-drawer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: flex-end; /* Align drawer to the right */
  z-index: 1000; /* Ensure it's above other content */
}

.preview-drawer {
  width: 400px; /* Adjust width as needed */
  background-color: white;
  box-shadow: -2px 0 5px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
}

.drawer-header {
  padding: 15px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.drawer-header h3 {
  margin: 0;
}

.drawer-content {
  padding: 15px;
  overflow-y: auto; /* Enable scrolling for content */
  flex-grow: 1;
}

.drawer-content pre {
    white-space: pre-wrap; /* Wrap long text */
    word-wrap: break-word;
}
/* End Styles for the drawer */
</style>