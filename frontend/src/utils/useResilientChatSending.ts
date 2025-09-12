import { ref, Ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { useI18n } from 'vue-i18n';
import { useChatStore, Message } from '@/stores/chat';
import { uploadFiles } from '@/services/apiService';
import { storeToRefs } from 'pinia';

// 重连状态接口
interface RetryState {
  isRetrying: boolean
  retryCount: number
  error: string | null
  progress: string
  partialResponse: string
  lastHeartbeat: number
}

// 定义附件接口
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

export function useResilientChatSending(userInput: Ref<string>, selectedFiles: Ref<File[]>) {
  const { t } = useI18n();
  const chatStore = useChatStore();
  const { currentConversation, messages, showThinkProcess } = storeToRefs(chatStore);

  const searchAIActive = ref(true);
  const searchRostiActive = ref(false);
  const searchOnlineActive = ref(false);
  const MAX_WORD_COUNT = 200000;

  // 弹性重连状态
  const retryState = ref<RetryState>({
    isRetrying: false,
    retryCount: 0,
    error: null,
    progress: '',
    partialResponse: '',
    lastHeartbeat: Date.now()
  });

  // 保存最后一次发送的消息数据用于重试
  const lastMessageData = ref<any>(null);
  const lastBotMessageId = ref<string | null>(null);

  // 重试配置
  const retryConfig = {
    maxRetries: 3,
    retryDelay: 2000,
    timeoutMs: 900000, // 15分钟
    backoffMultiplier: 1.5,
    heartbeatTimeout: 30000 // 30秒心跳超时
  };

  // 计算属性
  const canRetry = computed(() => 
    !chatStore.isSending && 
    retryState.value.error && 
    retryState.value.retryCount < retryConfig.maxRetries
  );

  const isSending = computed(() => chatStore.isSending || retryState.value.isRetrying);

  // 重置重连状态
  const resetRetryState = () => {
    retryState.value = {
      isRetrying: false,
      retryCount: 0,
      error: null,
      progress: '',
      partialResponse: '',
      lastHeartbeat: Date.now()
    };
  };

  // 检查是否为网络错误
  const isNetworkError = (error: any): boolean => {
    if (!error) return false;
    
    const errorString = error.toString().toLowerCase();
    const networkErrors = [
      'network error',
      'err_incomplete_chunked_encoding',
      'err_connection_reset',
      'err_connection_aborted',
      'fetch_error',
      'abort',
      'timeout',
      'streaming error'
    ];
    
    return networkErrors.some(errorType => errorString.includes(errorType));
  };

  // 延迟函数
  const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));



  // 增强的消息发送函数
  const sendMessage = async (isRetry: boolean = false) => {
    console.log('resilient sendMessage called. userInput:', userInput.value, 'selectedFiles:', selectedFiles.value, 'isRetry:', isRetry);
    
    if (!isRetry && !userInput.value.trim() && selectedFiles.value.length === 0) {
      console.log('No user input or selected files. Aborting sendMessage.');
      return;
    }

    // 设置发送状态
    chatStore.isSending = true;

    // 如果不是重试，重置重连状态
    if (!isRetry) {
      resetRetryState();
    }

    // 检查会话字数限制
    let currentWordCount = 0;
    if (chatStore.messages && Array.isArray(chatStore.messages)) {
      currentWordCount = chatStore.messages.reduce((count: number, message: Message) => {
        const words = message.content ? message.content.trim().split(/\s+/).filter((word: string) => word.length > 0) : [];
        return count + words.length;
      }, 0);
    }

    if (chatStore.currentConversation && currentWordCount >= MAX_WORD_COUNT) {
      ElMessage.warning(t('rostiChat.conversationLimitReached'));
      chatStore.clearCurrentConversation();
    }

    let uploadedFilesInfo: Attachment[] = [];
    let messageContent = '';

    try {
      // 处理文件上传或使用之前的数据
      if (!isRetry) {
        // 首次发送，处理文件上传
        if (selectedFiles.value.length > 0) {
          const formData = new FormData();
          selectedFiles.value.forEach((file: File) => {
            formData.append('files', file);
          });

          // 如果有当前会话，使用其ID；否则传undefined让后端处理
          const conversationId = chatStore.currentConversation?._id;
          const response = await uploadFiles(formData, conversationId);
          console.log("Upload response:", response);
          uploadedFilesInfo = response.uploaded_files as Attachment[];
          selectedFiles.value = [];
        }

        messageContent = userInput.value.trim();
        
        // 保存消息数据用于重试
        lastMessageData.value = {
          sender: 'user',
          content: messageContent,
          attachments: uploadedFilesInfo,
          search_ai_active: searchAIActive.value,
          search_rosti_active: searchRostiActive.value,
          search_online_active: searchOnlineActive.value,
          show_think_process: showThinkProcess.value,
        };
      } else {
        // 重试时使用之前保存的数据
        if (!lastMessageData.value) {
          ElMessage.error('没有可重试的消息数据');
          return;
        }
        messageContent = lastMessageData.value.content;
        uploadedFilesInfo = lastMessageData.value.attachments || [];
      }

      // 发送消息
      if (messageContent || uploadedFilesInfo.length > 0) {
        const searchOptions = {
          search_ai_active: searchAIActive.value,
          search_rosti_active: searchRostiActive.value,
          search_online_active: searchOnlineActive.value,
          show_think_process: showThinkProcess.value,
        };

        // 直接调用chat store方法，不使用弹性重连包装
        // 因为chat store方法内部已有完整的错误处理和UI更新逻辑
        if (chatStore.currentConversation) {
          // 有当前会话，向现有会话添加消息
          console.log('Adding message to existing conversation:', chatStore.currentConversation._id);
          
          const newMessage: Message = {
            sender: 'user',
            content: messageContent,
            attachments: uploadedFilesInfo,
            ...searchOptions
          };
          
          await chatStore.addMessageToConversation(chatStore.currentConversation._id, newMessage);
        } else {
          // 没有当前会话，创建新会话并添加消息
          console.log('Creating new conversation and adding message');
          await chatStore.createConversationAndAddMessage(messageContent, uploadedFilesInfo, searchOptions);
        }
        
        if (!isRetry) {
          userInput.value = '';
        }
        
        // 成功完成，清理重试状态
        resetRetryState();
      }

    } catch (error: any) {
      console.error("Error in message sending:", error);
      
      // 检查是否为网络错误，如果是，设置重试状态
      if (isNetworkError(error)) {
        retryState.value.error = error.message;
        retryState.value.retryCount = 0; // 重置重试计数
        ElMessage.warning('消息发送失败，您可以选择重试');
      } else {
        // 非网络错误，由chat store处理，我们不干预
        console.log('Non-network error, letting chat store handle it');
      }
    } finally {
      // 清除发送状态
      chatStore.isSending = false;
    }
  };

  // 手动重试函数
  const retryLastMessage = async () => {
    if (!canRetry.value) {
      ElMessage.warning('当前无法重试');
      return;
    }
    
    ElMessage.info('正在重试发送消息...');
    await sendMessage(true);
  };

  // 使用部分响应
  const usePartialResponse = () => {
    if (!retryState.value.partialResponse) {
      ElMessage.warning('没有可用的部分响应');
      return;
    }

    const botMessage = messages.value.find((msg: any) => msg._id === lastBotMessageId.value) as Message;
    if (botMessage) {
      botMessage.content = retryState.value.partialResponse;
      botMessage.loading = false;
    }
    
    resetRetryState();
    ElMessage.success('已使用部分响应');
  };

  // 取消错误状态
  const dismissError = () => {
    resetRetryState();
  };

  return {
    searchAIActive,
    searchRostiActive,
    searchOnlineActive,
    MAX_WORD_COUNT,
    sendMessage,
    
    // 弹性重连相关
    retryState: computed(() => retryState.value),
    canRetry,
    isSending,
    retryLastMessage,
    usePartialResponse,
    dismissError,
    resetRetryState
  };
}