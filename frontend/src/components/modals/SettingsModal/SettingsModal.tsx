import * as Dialog from '@radix-ui/react-dialog';
import './SettingsModal.css';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const SettingsModal = ({ isOpen, onClose }: SettingsModalProps) => {
  return (
    <Dialog.Root open={isOpen} onOpenChange={onClose}>
      <Dialog.Portal>
        <Dialog.Overlay className="DialogOverlay" />
        <Dialog.Content className="DialogContent">
          <Dialog.Title className="DialogTitle">Settings</Dialog.Title>
          <Dialog.Description className="DialogDescription">
            Customize the application according to your preferences
          </Dialog.Description>
          
          <div className="settings-content">
            <div className="settings-section">
              <h3>Appearance</h3>
              <div className="setting-item">
                <label htmlFor="theme">Theme</label>
                <select id="theme" className="setting-select">
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="auto">Auto</option>
                </select>
              </div>
              <div className="setting-item">
                <label htmlFor="language">Language</label>
                <select id="language" className="setting-select">
                  <option value="en">English</option>
                  <option value="ru">Русский</option>
                </select>
              </div>
            </div>
            
            <div className="settings-section">
              <h3>Chat</h3>
              <div className="setting-item">
                <label htmlFor="fontSize">Font Size</label>
                <select id="fontSize" className="setting-select">
                  <option value="small">Small</option>
                  <option value="medium" selected>Medium</option>
                  <option value="large">Large</option>
                </select>
              </div>
              <div className="setting-item">
                <label htmlFor="autoSave">Auto-save Chats</label>
                <div className="toggle-container">
                  <input type="checkbox" id="autoSave" className="toggle-input" defaultChecked />
                  <label htmlFor="autoSave" className="toggle-label"></label>
                </div>
              </div>
            </div>
          </div>
          
          <div className="dialog-actions">
            <button className="primary-button" onClick={onClose}>
              Save Changes
            </button>
            <button className="secondary-button" onClick={onClose}>
              Cancel
            </button>
          </div>
          
          <Dialog.Close asChild>
            <button className="IconButton" aria-label="Close">
              ✕
            </button>
          </Dialog.Close>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
};

export default SettingsModal;