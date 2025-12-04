import TopBar from '../../layout/TopBar/TopBar';
import MessageList from '../MessageList/MessageList';
import ManageInput from '../ManageInput/ManageInput';
import './ChatWindow.css';

interface ChatWindowProps {
  isSidebarOpen: boolean;
  onToggleSidebar: () => void;
}

const ChatWindow = ({ isSidebarOpen, onToggleSidebar }: ChatWindowProps) => {
  return (
    <div className="chat-window">
      <TopBar isSidebarOpen={isSidebarOpen} onToggleSidebar={onToggleSidebar} />
      <MessageList />
      <ManageInput />
    </div>
  );
};

export default ChatWindow;
