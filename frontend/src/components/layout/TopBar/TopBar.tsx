import { useChatStore } from '../../../stores';
import './TopBar.css';

interface TopBarProps {
  isSidebarOpen: boolean;
  onToggleSidebar: () => void;
}

const TopBar = ({ isSidebarOpen, onToggleSidebar }: TopBarProps) => {
  const { clearChat, getCurrentChat } = useChatStore();

  const handleNewChat = () => {
    const currentChat = getCurrentChat();
    if (currentChat) {
      clearChat(currentChat.id);
    }
  };

  return (
    <div className="top-bar">
      <div className="top-bar-left">
        {!isSidebarOpen && (
                  <button className="sidebar-toggle-button" onClick={onToggleSidebar}>
                    <img src="/sidebar-expand-layout-toggle-nav-navbar-svgrepo-com.svg" alt="Open Sidebar" className="sidebar-toggle-icon" />
                  </button>
                )}
        {!isSidebarOpen && (
          <button className="new-chat-button" onClick={handleNewChat}>
            <img src="/chat-new-svgrepo-com.svg" alt="New Chat" className="new-chat-icon" />
          </button>
        )}
      </div>
      <div className="top-bar-content">
        Medical Analytics AI-Agent
      </div>
    </div>
  );
};

export default TopBar;
