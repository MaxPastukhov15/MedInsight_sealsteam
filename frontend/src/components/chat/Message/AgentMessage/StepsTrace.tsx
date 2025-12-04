import { useState, useEffect } from 'react';
import type { Step } from '../../../../stores/chatStore';
import './StepsTrace.css';

interface StepsTraceProps {
  steps: Step[];
  collapsed?: boolean;
}

const formatOutput = (output: string | undefined, tool: string): React.ReactNode => {
  if (!output) return <span className="step-output-pending">...</span>;
  
  // Try to parse as JSON for SQL results
  try {
    const parsed = JSON.parse(output);
    if (Array.isArray(parsed) && parsed.length > 0) {
      const limited = parsed.slice(0, 10);
      const cols = Object.keys(limited[0]);
      return (
        <div className="step-table-container">
          <table className="step-table">
            <thead>
              <tr>
                {cols.map(col => <th key={col}>{col}</th>)}
              </tr>
            </thead>
            <tbody>
              {limited.map((row, i) => (
                <tr key={i}>
                  {cols.map(col => (
                    <td key={col}>{String(row[col] ?? '').slice(0, 50)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          {parsed.length > 10 && <div className="step-table-truncated">... and {parsed.length - 10} more rows</div>}
        </div>
      );
    }
  } catch {}
  
  // For chart tool, show simple message
  if (tool === 'chart') {
    return <div className="step-output-text">Graph generated</div>;
  }
  
  // Default: truncated text
  const truncated = output.length > 300 ? output.slice(0, 300) + '...' : output;
  return <pre className="step-output-text">{truncated}</pre>;
};

const StepsTrace = ({ steps, collapsed }: StepsTraceProps) => {
  const [expanded, setExpanded] = useState(!collapsed);

  useEffect(() => {
    if (collapsed) {
      setExpanded(false);
    }
  }, [collapsed]);

  if (!steps || steps.length === 0) return null;

  return (
    <div className="steps-trace">
      <button className="steps-trace-toggle" onClick={() => setExpanded(!expanded)}>
        Trace ({steps.length} steps) {expanded ? '[-]' : '[+]'}
      </button>
      {expanded && (
        <div className="steps-trace-content">
          {steps.map((step, idx) => (
            <div key={idx} className={`step-card step-${step.status}`}>
              <div className="step-header">
                <span className="step-title">{step.title}</span>
                <span className="step-tool">({step.tool})</span>
                {step.duration !== undefined && (
                  <span className="step-duration">{step.duration.toFixed(2)}s</span>
                )}
              </div>
              {step.input && (
                <div className="step-input">
                  <span className="step-label">Input:</span>
                  <pre className="step-input-text">{step.input.length > 200 ? step.input.slice(0, 200) + '...' : step.input}</pre>
                </div>
              )}
              <div className="step-output">
                <span className="step-label">Output:</span>
                {formatOutput(step.output, step.tool)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default StepsTrace;
