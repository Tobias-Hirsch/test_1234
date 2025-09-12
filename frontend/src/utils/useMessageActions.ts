import { ref, nextTick } from 'vue';
import { storeToRefs } from 'pinia';
import { ElMessage } from 'element-plus';
import { useI18n } from 'vue-i18n';
import { useChatStore, Message } from '@/stores/chat';
import { useAuthStore } from '@/stores/auth';

export function useMessageActions() {
  const { t } = useI18n();
  const chatStore = useChatStore();
  const authStore = useAuthStore();
  const { messages } = storeToRefs(chatStore);

  const userInput = ref(''); // This ref will be bound to the input area in RostiChatInterface.vue

  const editMessage = (content: string) => {
    userInput.value = content;
    nextTick(() => {
      const textarea = document.querySelector('.textarea-input textarea') as HTMLTextAreaElement;
      if (textarea) {
        textarea.focus();
        textarea.setSelectionRange(textarea.value.length, textarea.value.length);
      }
    });
  };

  const copyMessage = async (content: string) => {
    // The navigator.clipboard API is only available in secure contexts (HTTPS or localhost).
    // We need a fallback for insecure contexts (like HTTP on a production server).
    if (navigator.clipboard && window.isSecureContext) {
      // Modern, secure method
      try {
        await navigator.clipboard.writeText(content);
        ElMessage.success(t('rostiChat.copySuccess'));
      } catch (err) {
        console.error('Failed to copy message using navigator.clipboard: ', err);
        ElMessage.error(t('rostiChat.copyFailed'));
      }
    } else {
      // Fallback for insecure contexts
      const textArea = document.createElement('textarea');
      textArea.value = content;
      
      // Make the textarea invisible
      textArea.style.position = 'absolute';
      textArea.style.left = '-9999px';
      
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      
      try {
        document.execCommand('copy');
        ElMessage.success(t('rostiChat.copySuccess'));
      } catch (err) {
        console.error('Failed to copy message using execCommand: ', err);
        ElMessage.error(t('rostiChat.copyFailed'));
      } finally {
        document.body.removeChild(textArea);
      }
    }
  };

  const regenerateMessage = () => {
    const lastUserMessage = messages.value.slice().reverse().find((msg: Message) => msg.sender === 'user');
    if (lastUserMessage) {
      userInput.value = lastUserMessage.content;
      return userInput.value; // Return the user input for regeneration
    } else {
      ElMessage.warning(t('rostiChat.noPreviousUserMessage'));
      return '';
    }
  };

  const exportToWord = async (content: string) => {
    try {
      const { Document, Packer, Paragraph, TextRun } = await import('docx');

      const createParagraphsFromMarkdown = (markdown: string) => {
        const paragraphs: InstanceType<typeof Paragraph>[] = [];
        const lines = markdown.split('\n');

        lines.forEach(line => {
          if (line.startsWith('# ')) {
            paragraphs.push(new Paragraph({ text: line.substring(2), heading: 'Heading1' }));
          } else if (line.startsWith('## ')) {
            paragraphs.push(new Paragraph({ text: line.substring(3), heading: 'Heading2' }));
          } else if (line.startsWith('### ')) {
            paragraphs.push(new Paragraph({ text: line.substring(4), heading: 'Heading3' }));
          } else if (line.startsWith('- ') || line.startsWith('* ')) {
            paragraphs.push(new Paragraph({ text: line.substring(2), style: 'ListParagraph' }));
          } else if (line.trim() === '') {
            paragraphs.push(new Paragraph({ text: '' }));
          } else {
            paragraphs.push(new Paragraph({ children: [new TextRun(line)] }));
          }
        });

        return paragraphs;
      };

      const doc = new Document({
        sections: [{
          properties: {},
          children: createParagraphsFromMarkdown(content),
        }],
      });

      const blob = await Packer.toBlob(doc);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'RostiChat_Output.docx'; // Change extension to .docx
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      ElMessage.success(t('rostiChat.exportSuccess'));
    } catch (error) {
      console.error('Failed to export to DOCX:', error);
      ElMessage.error(t('rostiChat.exportFailed')); // Assuming you have an exportFailed translation
    }
  };

  const handleFeedback = async (messageId: string, type: 'like' | 'dislike') => {
    if (!messageId) return;

    const message = messages.value.find((m: Message) => m._id === messageId);
    if (!message) return;

    const originalFeedback = message.feedback;
    const newFeedback = originalFeedback === type ? null : type;

    // Optimistically update UI
    message.feedback = newFeedback;

    try {
      const response = await fetch(`/api/chat/messages/${messageId}/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authStore.token}`,
        },
        body: JSON.stringify({ rating: newFeedback }),
      });

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }

      if (newFeedback) {
        ElMessage.success(t('rostiChat.feedbackThanks'));
      }
    } catch (error) {
      console.error('Failed to send feedback:', error);
      ElMessage.error(t('rostiChat.feedbackFailed'));
      // Revert state on API failure
      message.feedback = originalFeedback;
    }
  };

  return {
    userInput,
    editMessage,
    copyMessage,
    regenerateMessage,
    exportToWord,
    handleFeedback, // Export the new function
  };
}