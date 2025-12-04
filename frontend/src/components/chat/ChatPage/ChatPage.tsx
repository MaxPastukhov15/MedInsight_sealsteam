import { useUIStore } from '../../../stores';
import Sidebar from '../../layout/Sidebar/Sidebar';
import ChatWindow from '../ChatWindow/ChatWindow';
import AboutModal from '../../modals/AboutModal/AboutModal';
import SettingsModal from '../../modals/SettingsModal/SettingsModal';
import './ChatPage.css';

import ChartPanel from '../../chart/ChartPanel/ChartPanel';

const ChatPage = () => {
  const { isSidebarOpen, toggleSidebar, isChartOpen, isAboutModalOpen, isSettingsModalOpen, closeAboutModal, closeSettingsModal } = useUIStore();

  return (
    <div className={`chat-page${isChartOpen ? ' chart-open' : ''}`}>
      <Sidebar isOpen={isSidebarOpen} onToggle={toggleSidebar} />
      <ChatWindow isSidebarOpen={isSidebarOpen} onToggleSidebar={toggleSidebar} />
      <ChartPanel />
      <AboutModal isOpen={isAboutModalOpen} onClose={closeAboutModal} />
      <SettingsModal isOpen={isSettingsModalOpen} onClose={closeSettingsModal} />
    </div>
  );
};

export default ChatPage;
