import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useEffect } from 'react';
import './AgentMessage.css';
import { useUIStore } from '../../../../stores';
import { translations, type Language } from '../../../../utils/translations';
import type { Step } from '../../../../stores/chatStore';
import StepsTrace from './StepsTrace';

interface AgentMessageProps {
  id: string;
  text: string;
  timestamp: Date;
  chart?: { title: string; mode: 'line' | 'bar'; points: { month: string; cases: number }[] };
  plotlyData?: any;
  steps?: Step[];
}

const AgentMessage = ({ id, text, chart, plotlyData, steps }: AgentMessageProps) => {
  const { openChart, language } = useUIStore();
  const hasChart = chart || plotlyData;
  const isComplete = !!text;
  const t = translations[language as Language] || translations.en;

  useEffect(() => {
    if (hasChart) {
      openChart(id);
    }
  }, [hasChart, id, openChart]);

  return (
    <div className="agent-message">
      <div className="agent-message-content">
        {steps && steps.length > 0 && <StepsTrace steps={steps} collapsed={isComplete} />}
        {text && (
          <div className="agent-message-text">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
          </div>
        )}
        {hasChart && (
          <div className="agent-message-actions">
            <button className="agent-message-open-chart" onClick={() => openChart(id)}>{t.chat.openChart}</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentMessage;
