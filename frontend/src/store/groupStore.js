// Group store - group state management
import { create } from 'zustand';
import { groupAPI } from '../services/api';

export const useGroupStore = create((set, get) => ({
  groups: [],
  activeGroup: null,
  members: {},
  messages: {},
  isLoading: false,

  // Fetch user's groups
  fetchGroups: async () => {
    // In a real app, fetch from API
    set({ isLoading: true });
    set({ groups: [], isLoading: false });
  },

  // Create group
  createGroup: async (name, description) => {
    try {
      const response = await groupAPI.create({ name, description });
      set((state) => ({ groups: [...state.groups, response.data] }));
      return response.data;
    } catch (error) {
      return null;
    }
  },

  // Set active group
  setActiveGroup: (group) => {
    set({ activeGroup: group });
    if (group?.id) {
      get().fetchGroupMembers(group.id);
      get().fetchGroupMessages(group.id);
    }
  },

  // Fetch group members
  fetchGroupMembers: async (groupId) => {
    try {
      const response = await groupAPI.getMembers(groupId);
      set({ members: { ...get().members, [groupId]: response.data } });
    } catch (error) {
      console.error('Failed to fetch members:', error);
    }
  },

  // Fetch group messages
  fetchGroupMessages: async (groupId) => {
    set({ isLoading: true });
    try {
      const response = await groupAPI.getMessages(groupId);
      set({
        messages: { ...get().messages, [groupId]: response.data },
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
    }
  },

  // Add member to group
  addMember: async (groupId, userId, role = 'member') => {
    try {
      await groupAPI.addMember(groupId, { user_id: userId, role });
      get().fetchGroupMembers(groupId);
      return true;
    } catch (error) {
      return false;
    }
  },

  // Remove member
  removeMember: async (groupId, userId) => {
    try {
      await groupAPI.removeMember(groupId, userId);
      get().fetchGroupMembers(groupId);
      return true;
    } catch (error) {
      return false;
    }
  },

  // Update member
  updateMember: async (groupId, userId, data) => {
    try {
      await groupAPI.updateMember(groupId, userId, data);
      get().fetchGroupMembers(groupId);
      return true;
    } catch (error) {
      return false;
    }
  },

  // Leave group
  leaveGroup: async (groupId) => {
    const userId = 'current_user_id'; // Get from user store
    return get().removeMember(groupId, userId);
  },

  // Clear active group
  clearActiveGroup: () => {
    set({ activeGroup: null });
  },
}));

export default useGroupStore;