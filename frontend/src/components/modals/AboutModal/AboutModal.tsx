import * as Dialog from '@radix-ui/react-dialog';
import './AboutModal.css';

interface AboutModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const AboutModal = ({ isOpen, onClose }: AboutModalProps) => {
  return (
    <Dialog.Root open={isOpen} onOpenChange={onClose}>
      <Dialog.Portal>
        <Dialog.Overlay className="DialogOverlay" />
        <Dialog.Content className="DialogContent">
          <Dialog.Title className="DialogTitle">About Medical Analytics AI-Agent</Dialog.Title>
          <Dialog.Description className="DialogDescription">
            Information about the application
          </Dialog.Description>
          
          <div className="about-content">
            <div className="about-logo">
              <img src="/Sealsteam_l.svg" alt="SealSteam" className="about-logo-image" />
            </div>
            <p className="team-name">SealsTeam</p>
            <div className="about-info">
              <h2>Medical Analytics AI-Agent</h2>
              <p>Version: 0.5.0</p>
              <p>AI assistant based on Large Language Model (LLM) technology for analyzing medical data from St. Petersburg and providing insights.</p>
              
              <div className="about-features">
                <h3>Key Features:</h3>
                <ul>
                  <li>Medical data analysis</li>
                  <li>Pattern recognition</li>
                  <li>Insight generation</li>
                  <li>Interactive chat interface</li>
                </ul>
              </div>
              
              <div className="about-tech">
                <h3>Technologies:</h3>
                <p>React, TypeScript, Zustand, Radix UI</p>
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