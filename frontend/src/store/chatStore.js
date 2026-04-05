// Chat store - messages and conversations
import { create } from 'zustand';
import { chatAPI } from '../services/api';
import { socketService } from '../services/socket';

export const useChatStore = create((set, get) => ({
  conversations: [],
  activeConversation: null,
  messages: {},
  isLoading: false,

  // Initialize socket listeners
  initSocketListeners: () => {
    socketService.on('new_message', (message) => {
      const { messages, activeConversation } = get();
      const convKey = message.sender_id === activeConversation?.user_id 
        ? activeConversation.user_id 
        : message.receiver_id === activeConversation?.user_id 
          ? activeConversation.user_id 
          : null;
      
      if (convKey) {
        set({
          messages: {
            ...messages,
            [convKey]: [...(messages[convKey] || []), message],
          },
        });
      }
    });
  },

  // Fetch conversations
  fetchConversations: async () => {
    set({ isLoading: true });
    try {
      // In a real app, call API to get conversations
      // For now, just set empty
      set({ conversations: [], isLoading: false });
    } catch (error) {
      set({ isLoading: false });
    }
  },

  // Set active conversation
  setActiveConversation: (conversation) => {
    set({ activeConversation: conversation });
    if (conversation?.user_id) {
      get().fetchMessages(conversation.user_id);
    }
  },

  // Fetch messages for a conversation
  fetchMessages: async (userId) => {
    set({ isLoading: true });
    try {
      const response = await chatAPI.getMessages(userId, { limit: 50 });
      set({
        messages: { ...get().messages, [userId]: response.data },
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
    }
  },

  // Send message
  sendMessage: async (receiverId, content) => {
    try {
      const response = await chatAPI.sendMessage({
        receiver_id: receiverId,
        content,
        type: 'text',
      });
      const message = response.data;
      set((state) => ({
        messages: {
          ...state.messages,
          [receiverId]: [...(state.messages[receiverId] || []), message],
        },
      }));
      return true;
    } catch (error) {
      return false;
    }
  },

  // Delete message
  deleteMessage: async (messageId, receiverId) => {
    try {
      await chatAPI.deleteMessage(messageId);
      set((state) => ({
        messages: {
          ...state.messages,
          [receiverId]: state.messages[receiverId]?.map((m) =>
            m.id === messageId ? { ...m, is_deleted: true } : m
          ) || [],
        },
      }));
      return true;
    } catch (error) {
      return false;
    }
  },

  // Add reaction
  addReaction: async (messageId, emoji) => {
    try {
      await chatAPI.addReaction({ message_id: messageId, emoji });
      return true;
    } catch (error) {
      return false;
    }
  },

  // Clear active conversation
  clearActiveConversation: () => {
    set({ activeConversation: null });
  },
}));

export default useChatStore;