import * as Dialog from '@radix-ui/react-dialog';
import { useUIStore } from '../../../stores/uiStore';
import { translations, type Language } from '../../../utils/translations';
import './AboutModal.css';

interface AboutModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const AboutModal = ({ isOpen, onClose }: AboutModalProps) => {
  const { language } = useUIStore();
  const t = translations[language as Language] || translations.en;

  return (
    <Dialog.Root open={isOpen} onOpenChange={onClose}>
      <Dialog.Portal>
        <Dialog.Overlay className="DialogOverlay" />
        <Dialog.Content className="DialogContent">
          <Dialog.Title className="DialogTitle">{t.about.title}</Dialog.Title>
          <Dialog.Description className="DialogDescription">
            {t.about.description}
          </Dialog.Description>

          <div className="about-content">
            <div className="about-logo">
              <img src="/Sealsteam_l.svg" alt="SealSteam" className="about-logo-image" />
            </div>
            <p className="team-name">SealsTeam</p>
            <div className="about-info">
              <h2>MedInsight AI</h2>
              <p>{t.about.version}: 0.5.0</p>
              <p>{t.about.description}</p>
              
              <div className="about-features">
                <h3>{t.about.featuresTitle}</h3>
                <ul>
                  <li>{t.about.feature1}</li>
                  <li>{t.about.feature2}</li>
                  <li>{t.about.feature3}</li>
                  <li>{t.about.feature4}</li>
                </ul>
              </div>

              <div className="about-tech">
                <h3>{t.about.developer}:</h3>
                <p>SealsTeam</p>
              </div>
            </div>
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

export default AboutModal;
