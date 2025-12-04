import { useState, useEffect, useRef } from 'react';
import { useChatStore, useUIStore } from '../../../stores';
import './ManageInput.css';

const ManageInput = () => {
  const [messageText, setMessageText] = useState('');
  const { sendMessage, isLoading } = useChatStore();
  const { setInputHeight } = useUIStore();
  const inputRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSendMessage = () => {
    if (messageText.trim() && !isLoading) {
      sendMessage(messageText.trim());
      setMessageText('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      const originalOverflow = textareaRef.current.style.overflow;
      textareaRef.current.style.overflow = 'hidden';
      textareaRef.current.style.height = 'auto';
      const newHeight = Math.min(textareaRef.current.scrollHeight, 120);
      textareaRef.current.style.height = `${newHeight}px`;
      textareaRef.current.style.overflow = originalOverflow;
      if (textareaRef.current.scrollHeight > 120) {
        textareaRef.current.style.overflowY = 'auto';
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessageText(e.target.value);
    
    if (!e.target.value.trim()) {
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
        textareaRef.current.style.overflowY = 'auto';
      }
    } else {
      adjustTextareaHeight();
    }
  };

  useEffect(() => {
    const updateHeight = () => {
      if (inputRef.current) {
        const height = inputRef.current.offsetHeight;
        setInputHeight(height);
      }
    };

    const resizeObserver = new ResizeObserver(() => {
      updateHeight();
    });

    if (inputRef.current) {
      resizeObserver.observe(inputRef.current);
      updateHeight();
    }

    return () => {
      if (inputRef.current) {
        resizeObserver.unobserve(inputRef.current);
      }
    };
  }, [setInputHeight]);

  return (
    <div className="manage-input" ref={inputRef}>
      <div className="input-container">
        <textarea 
          ref={textareaRef}
          placeholder="Type a message..." 
          className="message-input"
          value={messageText}
          onChange={handleChange}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
          rows={1}
          style={{ resize: 'none' }}
        />
        <button 
          className="send-button"
          onClick={handleSendMessage}
          disabled={isLoading || !messageText.trim()}
        >
          <img src="/square-arrow-up-svgrepo-com.svg" alt="Send" className="send-icon" />
        </button>
      </div>
    </div>
  );
};

export default ManageInput;