import { useEffect, useRef } from 'react';
// @ts-ignore
import Plotly from 'plotly.js-dist-min';
import { useUIStore, useChatStore } from '../../../stores';
import './ChartPanel.css';

const ChartPanel = () => {
  const { isChartOpen, selectedChartMessageId, closeChart, inputHeight, theme } = useUIStore();
  const { getCurrentChat } = useChatStore();
  const chartRef = useRef<HTMLDivElement>(null);
  const resizeObserverRef = useRef<ResizeObserver | null>(null);

  useEffect(() => {
    const container = chartRef.current;
    if (!container) return;

    const currentChat = getCurrentChat();
    const msg = currentChat?.messages.find(m => m.id === selectedChartMessageId);

    if (isChartOpen && msg) {
      const isDark = theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);

      const layoutCommon = {
        margin: { l: 60, r: 20, t: 40, b: 60 },
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: {
          color: isDark ? '#e0e0e0' : '#333'
        },
        xaxis: {
          gridcolor: isDark ? '#444' : '#eee',
          zerolinecolor: isDark ? '#444' : '#eee'
        },
        yaxis: {
          gridcolor: isDark ? '#444' : '#eee',
          zerolinecolor: isDark ? '#444' : '#eee'
        }
      };

      // Check for full Plotly JSON from backend
      if (msg.plotlyData) {
        const { data, layout } = msg.plotlyData;
        Plotly.newPlot(container, data, {
          ...layout,
          ...layoutCommon,
          xaxis: { ...layout.xaxis, ...layoutCommon.xaxis },
          yaxis: { ...layout.yaxis, ...layoutCommon.yaxis }
        }, { displayModeBar: true, responsive: true });
      }
      // Fallback to legacy chart format
      else if (msg.chart && msg.chart.points.length > 0) {
        const chart = msg.chart;
        const x = chart.points.map(d => d.month);
        const y = chart.points.map(d => d.cases);

        const traceColor = '#007bff'; // Primary color

        const trace = chart.mode === 'bar'
          ? ({ x, y, type: 'bar', marker: { color: traceColor }, name: 'Случаи' } as any)
          : ({ x, y, type: 'scatter', mode: 'lines+markers', marker: { color: traceColor, size: 6 }, line: { color: traceColor, width: 2 }, name: 'Случаи' } as any);

        const layout = {
          title: chart.title,
          ...layoutCommon,
          xaxis: { ...layoutCommon.xaxis, title: 'Месяц' },
          yaxis: { ...layoutCommon.yaxis, title: 'Количество случаев', zeroline: false },
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
  }, [isChartOpen, selectedChartMessageId, theme]);

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
