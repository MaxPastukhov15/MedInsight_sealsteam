import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type Theme = 'light' | 'dark' | 'system';

interface UIState {
  isSidebarOpen: boolean;
  sidebarWidth: number;
  theme: Theme;
  language: string;
  inputHeight: number;
  isChartOpen: boolean;
  selectedChartMessageId: string | null;
  isAboutModalOpen: boolean;
  isSettingsModalOpen: boolean;
  
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setSidebarWidth: (width: number) => void;
  setTheme: (theme: Theme) => void;
  setLanguage: (language: string) => void;
  setInputHeight: (height: number) => void;
  openChart: (messageId: string) => void;
  closeChart: () => void;
  toggleChart: () => void;
  setSelectedChartMessageId: (messageId: string | null) => void;
  openAboutModal: () => void;
  closeAboutModal: () => void;
  openSettingsModal: () => void;
  closeSettingsModal: () => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      isSidebarOpen: true,
      sidebarWidth: 260,
      theme: 'system',
      language: 'en',
      inputHeight: 80,
      isChartOpen: false,
      selectedChartMessageId: null,
      isAboutModalOpen: false,
      isSettingsModalOpen: false,
      
      toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
      setSidebarOpen: (open) => set({ isSidebarOpen: open }),
      setSidebarWidth: (width) => set({ sidebarWidth: width }),
      setTheme: (theme) => set({ theme }),
      setLanguage: (language) => set({ language }),
      setInputHeight: (height) => set({ inputHeight: height }),
      openChart: (messageId) => set({ isChartOpen: true, selectedChartMessageId: messageId }),
      closeChart: () => set({ isChartOpen: false }),
      toggleChart: () => set((state) => ({ isChartOpen: !state.isChartOpen })),
      setSelectedChartMessageId: (messageId) => set({ selectedChartMessageId: messageId }),
      openAboutModal: () => set({ isAboutModalOpen: true }),
      closeAboutModal: () => set({ isAboutModalOpen: false }),
      openSettingsModal: () => set({ isSettingsModalOpen: true }),
      closeSettingsModal: () => set({ isSettingsModalOpen: false }),
    }),
    {
      name: 'ui-storage',
    }
  )
);
