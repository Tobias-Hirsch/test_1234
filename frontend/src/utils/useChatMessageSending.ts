import { ref, Ref } from 'vue';
import { ElMessage } from 'element-plus';
import { useI18n } from 'vue-i18n';
import { useChatStore, Message } from '@/stores/chat';
import { uploadFiles } from '@/services/apiService';
import { storeToRefs } from 'pinia';

// Define interface for Attachment based on backend schema
interface Attachment {
  _id?: string | null;
  filename: string;
  bucket_name: string;
  object_name: string;
  size: number;
  content_type: string;
  upload_timestamp: string;
  download_url?: string;
}

export function useChatMessageSending(userInput: Ref<string>, selectedFiles: Ref<File[]>) {
  const { t } = useI18n();
  const chatStore = useChatStore();
  const { currentConversation, messages, showThinkProcess } = storeToRefs(chatStore);

  const searchAIActive = ref(true);
  const searchRostiActive = ref(false);
  const searchOnlineActive = ref(false);

  const MAX_WORD_COUNT = 200000;

  const sendMessage = async () => {
    console.log('sendMessage called. userInput:', userInput.value, 'selectedFiles:', selectedFiles.value);
    if (!userInput.value.trim() && selectedFiles.value.length === 0) {
      console.log('No user input or selected files. Aborting sendMessage.');
      return;
    }

    // Calculate current conversation word count (excluding attachments)
    let currentWordCount = 0;
    if (chatStore.messages && Array.isArray(chatStore.messages)) {
        currentWordCount = chatStore.messages.reduce((count: number, message: Message) => {
            // Simple word count: split by whitespace and count non-empty tokens
            const words = message.content ? message.content.trim().split(/\s+/).filter((word: string) => word.length > 0) : [];
            return count + words.length;
        }, 0);
    }

    // Check if current conversation exceeds word limit
    if (chatStore.currentConversation && currentWordCount >= MAX_WORD_COUNT) {
        ElMessage.warning(t('rostiChat.conversationLimitReached'));
        chatStore.clearCurrentConversation();
    }

    let uploadedFilesInfo: Attachment[] = [];

    // Handle file upload if files are selected
    if (selectedFiles.value.length > 0) {
      const formData = new FormData();
      selectedFiles.value.forEach((file: File) => {
        formData.append('files', file);
      });

      try {
        const conversationId = chatStore.currentConversation?._id;
        const response = await uploadFiles(formData, conversationId);
        console.log("Upload response:", response);
        uploadedFilesInfo = response.uploaded_files as Attachment[];

      } catch (error: any) {
        console.error("Error uploading files:", error);
         chatStore.messages.push({
          content: `Error uploading file(s): ${error.message}`,
          sender: 'bot',
          time: new Date().toISOString()
        });
        selectedFiles.value = [];
        return;
      } finally {
         selectedFiles.value = [];
      }
    }

    // Handle sending text message (if any) and add message to conversation
    if (userInput.value.trim() || uploadedFilesInfo.length > 0) {
      const messageContent = userInput.value.trim();
      const attachments = uploadedFilesInfo;

      const newMessage: Message = {
          sender: 'user',
          content: messageContent,
          attachments: attachments,
          search_ai_active: searchAIActive.value,
          search_rosti_active: searchRostiActive.value,
          search_online_active: searchOnlineActive.value,
          show_think_process: showThinkProcess.value,
          // search_results will be populated by the backend
      };

      try {
          if (!chatStore.currentConversation) {
              // If no conversation is selected, create a new one and add the message
              await chatStore.createConversationAndAddMessage(messageContent, attachments, {
                  search_ai_active: searchAIActive.value,
                  search_rosti_active: searchRostiActive.value,
                  search_online_active: searchOnlineActive.value,
                  show_think_process: showThinkProcess.value
              });
          } else {
              // If a conversation is selected, just add the message to it
              await chatStore.addMessageToConversation(chatStore.currentConversation._id, newMessage);
          }

          userInput.value = '';
      } catch (error: any) {
          console.error("Error sending message:", error);
           chatStore.messages.push({
              content: `Error sending message: ${error.message}`,
              sender: 'bot',
              time: new Date().toISOString()
          });
      }
    }
  };

  return {
    searchAIActive,
    searchRostiActive,
    searchOnlineActive,
    MAX_WORD_COUNT, // Export MAX_WORD_COUNT
    sendMessage,
  };
}