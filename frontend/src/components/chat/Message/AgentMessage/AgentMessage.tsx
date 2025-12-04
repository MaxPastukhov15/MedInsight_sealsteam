import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './AgentMessage.css';
import { useUIStore } from '../../../../stores';
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
  const { openChart } = useUIStore();
  const hasChart = chart || plotlyData;
  const isComplete = !!text;

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
            <button className="agent-message-open-chart" onClick={() => openChart(id)}>Open chart</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentMessage;
