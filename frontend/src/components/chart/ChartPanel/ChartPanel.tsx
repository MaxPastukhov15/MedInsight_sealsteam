import { useEffect, useRef } from 'react';
// @ts-ignore
import Plotly from 'plotly.js-dist-min';
import { useUIStore, useChatStore } from '../../../stores';
import './ChartPanel.css';

const ChartPanel = () => {
  const { isChartOpen, selectedChartMessageId, closeChart, inputHeight } = useUIStore();
  const { getCurrentChat } = useChatStore();
  const chartRef = useRef<HTMLDivElement>(null);
  const resizeObserverRef = useRef<ResizeObserver | null>(null);

  useEffect(() => {
    const container = chartRef.current;
    if (!container) return;

    const currentChat = getCurrentChat();
    const msg = currentChat?.messages.find(m => m.id === selectedChartMessageId);
    
    if (isChartOpen && msg) {
      // Check for full Plotly JSON from backend
      if (msg.plotlyData) {
        const { data, layout } = msg.plotlyData;
        Plotly.newPlot(container, data, {
          ...layout,
          margin: { l: 60, r: 20, t: 40, b: 60 },
        }, { displayModeBar: true, responsive: true });
      }
      // Fallback to legacy chart format
      else if (msg.chart && msg.chart.points.length > 0) {
        const chart = msg.chart;
        const x = chart.points.map(d => d.month);
        const y = chart.points.map(d => d.cases);

        const trace = chart.mode === 'bar'
          ? ({ x, y, type: 'bar', marker: { color: '#2b6cb0' }, name: 'Случаи' } as any)
          : ({ x, y, type: 'scatter', mode: 'lines+markers', marker: { color: '#2b6cb0', size: 6 }, line: { color: '#2b6cb0', width: 2 }, name: 'Случаи' } as any);

        const layout = {
          title: chart.title,
          margin: { l: 60, r: 20, t: 40, b: 60 },
          xaxis: { title: 'Месяц' },
          yaxis: { title: 'Количество случаев', zeroline: false, gridcolor: '#eee' },
        } as any;

        Plotly.newPlot(container, [trace], layout, { displayModeBar: true, responsive: true });
      } else {
        Plotly.purge(container);
        return;
      }

      if (!resizeObserverRef.current) {
        resizeObserverRef.current = new ResizeObserver(() => {
          Plotly.Plots.resize(container);
        });
      }
      resizeObserverRef.current.observe(container);
    } else {
      if (container) {
        Plotly.purge(container);
      }
    }

    return () => {
      const ro = resizeObserverRef.current;
      if (ro && chartRef.current) {
        ro.unobserve(chartRef.current);
      }
    };
  }, [isChartOpen, selectedChartMessageId]);

  const contentHeight = `calc(100vh - ${inputHeight}px - 48px)`;

  return (
    <div className={`chart-panel${isChartOpen ? ' open' : ''}`}>
      <div className="chart-panel__top">
        <div className="chart-panel__title">График</div>
        <button className="chart-panel__close" onClick={closeChart} aria-label="Закрыть">×</button>
      </div>
      <div className="chart-panel__content" style={{ height: contentHeight }}>
        <div ref={chartRef} className="chart-panel__plot" />
      </div>
    </div>
  );
};

export default ChartPanel;
