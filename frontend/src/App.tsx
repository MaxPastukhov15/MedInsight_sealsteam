import { useEffect } from 'react';
import ChatPage from './components/chat/ChatPage/ChatPage';
import { useChatStore } from './stores';
import './App.css';

function App() {
  const { createChat, currentChatId } = useChatStore();

  useEffect(() => {
    if (!currentChatId) {
      createChat('Medical Analytics Chat');
    }
  }, [currentChatId, createChat]);

  return (
    <ChatPage />
  );
}

export default App;
