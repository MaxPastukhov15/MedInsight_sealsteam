import * as Dialog from '@radix-ui/react-dialog';
import { useUIStore, type Theme, type FontSize } from '../../../stores/uiStore';
import { translations, type Language } from '../../../utils/translations';
import './SettingsModal.css';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const SettingsModal = ({ isOpen, onClose }: SettingsModalProps) => {
  const {
    theme, setTheme,
    language, setLanguage,
    fontSize, setFontSize,
    autoSaveChats, setAutoSaveChats
  } = useUIStore();

  const t = translations[language as Language] || translations.en;

  return (
    <Dialog.Root open={isOpen} onOpenChange={onClose}>
      <Dialog.Portal>
        <Dialog.Overlay className="DialogOverlay" />
        <Dialog.Content className="DialogContent">
          <Dialog.Title className="DialogTitle">{t.settings.title}</Dialog.Title>
          <Dialog.Description className="DialogDescription">
            {t.settings.description}
          </Dialog.Description>

          <div className="settings-content">
            <div className="settings-section">
              <h3>{t.settings.appearance}</h3>
              <div className="setting-item">
                <label htmlFor="theme">{t.settings.theme}</label>
                <select
                  id="theme"
                  className="setting-select"
                  value={theme}
                  onChange={(e) => setTheme(e.target.value as Theme)}
                >
                  <option value="light">{t.settings.themeLight}</option>
                  <option value="dark">{t.settings.themeDark}</option>
                  <option value="system">{t.settings.themeAuto}</option>
                </select>
              </div>
              <div className="setting-item">
                <label htmlFor="language">{t.settings.language}</label>
                <select
                  id="language"
                  className="setting-select"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                >
                  <option value="en">English</option>
                  <option value="ru">Русский</option>
                </select>
              </div>
            </div>

            <div className="settings-section">
              <h3>{t.settings.chat}</h3>
              <div className="setting-item">
                <label htmlFor="fontSize">{t.settings.fontSize}</label>
                <select
                  id="fontSize"
                  className="setting-select"
                  value={fontSize}
                  onChange={(e) => setFontSize(e.target.value as FontSize)}
                >
                  <option value="small">{t.settings.fontSizeSmall}</option>
                  <option value="medium">{t.settings.fontSizeMedium}</option>
                  <option value="large">{t.settings.fontSizeLarge}</option>
                </select>
              </div>
              <div className="setting-item">
                <label htmlFor="autoSave">{t.settings.autoSave}</label>
                <div className="toggle-container">
                  <input
                    type="checkbox"
                    id="autoSave"
                    className="toggle-input"
                    checked={autoSaveChats}
                    onChange={(e) => setAutoSaveChats(e.target.checked)}
                  />
                  <label htmlFor="autoSave" className="toggle-label"></label>
                </div>
              </div>
            </div>
          </div>

          <div className="dialog-actions">
            <button className="primary-button" onClick={onClose}>
              {t.settings.done}
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
