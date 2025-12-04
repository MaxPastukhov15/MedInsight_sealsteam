import './UserMessage.css';

interface UserMessageProps {
  text: string;
  timestamp: Date;
}

const UserMessage = ({ text }: UserMessageProps) => {
  return (
    <div className="user-message">
      <div className="user-message-content">
        <div className="user-message-text">{text}</div>
      </div>
    </div>
  );
};

export default UserMessage;