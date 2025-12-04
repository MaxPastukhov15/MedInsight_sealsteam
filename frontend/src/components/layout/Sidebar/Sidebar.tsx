import { useChatStore, useUIStore } from '../../../stores';
import './Sidebar.css';

interface SidebarProps {
  onToggle: () => void;
  isOpen: boolean;
}

const Sidebar = ({ onToggle, isOpen }: SidebarProps) => {
  const { clearChat, getCurrentChat } = useChatStore();
  const { openSettingsModal, openAboutModal } = useUIStore();

  const handleNewChat = () => {
    const currentChat = getCurrentChat();
    if (currentChat) {
      clearChat(currentChat.id);
    }
  };

  const handleSettings = () => {
    openSettingsModal();
  };

  const handleAbout = () => {
    openAboutModal();
  };

  return (
    <div className={`sidebar ${isOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
      <div className="sidebar-content">
        <div className="sidebar-header">
          <div className="logo-container">
            <img src="/Sealsteam_l.svg" alt="SealSteam" className="logo" />
          </div>
          <button className="sidebar-toggle" onClick={onToggle}>
            <img src="/sidebar-collapse-layout-toggle-nav-navbar-svgrepo-com.svg" alt="Close Sidebar" className="sidebar-close-icon" />
          </button>
        </div>
        <div className="sidebar-new-chat">
          <button className="new-chat-large-button" onClick={handleNewChat}>
            <img src="/chat-new-svgrepo-com.svg" alt="New Chat" className="new-chat-large-icon" />
            <span>New Chat</span>
          </button>
        </div>
        <div className="sidebar-body">
          {/* Nothing there xD */}
        </div>
        <div className="sidebar-footer">
          <button className="settings-button" onClick={handleSettings}>
            <img src="/settings-svgrepo-com.svg" alt="Settings" className="settings-icon" />
            <span>Settings</span>
          </button>
          <button className="about-button" onClick={handleAbout}>
            <img src="/about-svgrepo-com.svg" alt="About" className="about-icon" />
            <span>About</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
