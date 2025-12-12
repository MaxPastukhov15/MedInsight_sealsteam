import { useEffect } from 'react';
import ChatPage from './components/chat/ChatPage/ChatPage';
import { useChatStore, useUIStore } from './stores';
import './App.css';

function App() {
  const { createChat, currentChatId, chats } = useChatStore();
  const { theme, fontSize, autoSaveChats } = useUIStore();

  useEffect(() => {
    const root = document.documentElement;
    let size = '0.9375rem';
    
    switch (fontSize) {
      case 'small':
        size = '0.8125rem';
        break;
      case 'medium':
        size = '0.9375rem';
        break;
      case 'large':
        size = '1.0625rem';
        break;
    }
    
    root.style.setProperty('--font-size-message', size);
  }, [fontSize]);

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark-theme');
      root.classList.remove('light-theme');
    } else if (theme === 'light') {
      root.classList.add('light-theme');
      root.classList.remove('dark-theme');
    } else {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      root.classList.add(`${systemTheme}-theme`);
      root.classList.remove(`${systemTheme === 'dark' ? 'light' : 'dark'}-theme`);
      
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = (e: MediaQueryListEvent) => {
        const newTheme = e.matches ? 'dark' : 'light';
        root.classList.add(`${newTheme}-theme`);
        root.classList.remove(`${newTheme === 'dark' ? 'light' : 'dark'}-theme`);
      };
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, [theme]);

  useEffect(() => {
    if (!autoSaveChats) {
      useChatStore.setState({ chats: [], currentChatId: null });
    }
  }, []);

  useEffect(() => {
    if (!currentChatId && chats.length === 0) {
      createChat('Medical Analytics Chat');
    } else if (!currentChatId && chats.length > 0) {
        useChatStore.getState().setCurrentChat(chats[0].id);
    }
  }, [currentChatId, createChat, chats.length]);

  return (
    <ChatPage />
  );
}

export default App;
