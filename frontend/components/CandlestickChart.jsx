import React, { useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';

const CandlestickChart = ({ symbol, interval, tradeTime }) => {
  const chartContainerRef = useRef();
  const chartRef = useRef();

  useEffect(() => {
    // Create chart instance
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: {
        background: { color: '#ffffff' },
        textColor: '#333333',
        fontSize: 12,
        fontFamily: 'Times New Roman'
      },
      grid: {
        vertLines: { color: 'rgba(0, 102, 178, 0.1)' },
        horzLines: { color: 'rgba(0, 102, 178, 0.1)' }
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
      crosshair: {
        mode: 1
      }
    });

    // Add candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#28a745',
      downColor: '#dc3545',
      borderVisible: false,
      wickUpColor: '#28a745',
      wickDownColor: '#dc3545'
    });

    // Add trade marker
    const markers = [{
      time: new Date(tradeTime).getTime() / 1000,
      position: 'aboveBar',
      color: '#0066B2',
      shape: 'arrowDown',
      text: 'Trade Entry'
    }];

    // Fetch and update data
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/candles/${symbol}/${interval}`);
        const data = await response.json();
        
        candlestickSeries.setData(data);
        candlestickSeries.setMarkers(markers);
        
        // Fit content to view
        chart.timeScale().fitContent();
      } catch (error) {
        console.error('Error fetching candle data:', error);
      }
    };

    fetchData();
    chartRef.current = chart;

    // Clean up
    return () => {
      chart.remove();
    };
  }, [symbol, interval, tradeTime]);

  return (
    <div className="candlestick-chart" ref={chartContainerRef}>
      <div className="chart-header">
        <h3>{symbol} Price Chart</h3>
        <span className="interval-badge">{interval}</span>
      </div>
    </div>
  );
};

export default CandlestickChart;