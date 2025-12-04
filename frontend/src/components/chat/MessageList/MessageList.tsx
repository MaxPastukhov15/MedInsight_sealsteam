import { useChatStore, useUIStore } from '../../../stores';
import { UserMessage, AgentMessage } from '../Message';
import ThinkingIndicator from '../ThinkingIndicator/ThinkingIndicator';
import { useEffect, useRef } from 'react';
import './MessageList.css';

const MessageList = () => {
  const { getCurrentChat, isLoading, currentChatId } = useChatStore();
  const { inputHeight } = useUIStore();
  const currentChat = getCurrentChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [currentChat?.messages, isLoading]);

  return (
    <div className="message-list" style={{ paddingBottom: `${inputHeight + 20}px` }}>
      {!currentChat && (
        <div style={{ padding: '20px', color: '#888' }}>
          No active chat. Current chat ID: {currentChatId || 'null'}
        </div>
      )}
      {currentChat && currentChat.messages.length === 0 && (
        <div style={{ padding: '20px', color: '#888' }}>
          Chat is empty. Start a conversation!
        </div>
      )}
      {currentChat && currentChat.messages.map((message) => (
        message.role === 'user' ? (
          <UserMessage 
            key={message.id} 
            text={message.text} 
            timestamp={message.timestamp} 
          />
        ) : (
          <AgentMessage 
            key={message.id} 
            id={message.id}
            text={message.text} 
            timestamp={message.timestamp} 
            chart={message.chart}
            plotlyData={message.plotlyData}
            steps={message.steps}
          />
        )
      ))}
      {isLoading && <ThinkingIndicator />}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;
