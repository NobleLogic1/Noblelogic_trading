import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';

const SystemMonitor = ({ testResults, onRefreshTest }) => {
    const [monitoringData, setMonitoringData] = useState({
        accuracy: 0,
        trades: [],
        healthScore: 100,
        alerts: []
    });

    useEffect(() => {
        fetchMonitoringData();
        const interval = setInterval(fetchMonitoringData, 60000); // Update every minute
        return () => clearInterval(interval);
    }, []);

    const fetchMonitoringData = async () => {
        try {
            const response = await fetch('/api/system/monitoring');
            const data = await response.json();
            setMonitoringData(data);
        } catch (error) {
            console.error('Error fetching monitoring data:', error);
        }
    };

    const getHealthStatus = (score) => {
        if (score >= 90) return { class: 'excellent', text: 'Excellent' };
        if (score >= 80) return { class: 'good', text: 'Good' };
        if (score >= 70) return { class: 'fair', text: 'Fair' };
        return { class: 'poor', text: 'Poor' };
    };

    const healthStatus = getHealthStatus(monitoringData.healthScore);

    const chartData = {
        labels: monitoringData.trades.map(t => new Date(t.timestamp).toLocaleTimeString()),
        datasets: [
            {
                label: 'Trade Accuracy',
                data: monitoringData.trades.map(t => t.accuracy * 100),
                borderColor: '#0066B2',
                fill: false
            },
            {
                label: 'System Health',
                data: monitoringData.trades.map(t => t.healthScore),
                borderColor: '#28a745',
                fill: false
            }
        ]
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                max: 100
            }
        }
    };

    return (
        <div className="system-monitor panel">
            <div className="panel-header">
                <h2>System Monitor</h2>
                <button className="refresh-button" onClick={onRefreshTest}>
                    Run System Test
                </button>
            </div>

            <div className="monitor-grid">
                {/* Health Score */}
                <div className={`health-score ${healthStatus.class}`}>
                    <h3>System Health</h3>
                    <div className="score">{monitoringData.healthScore.toFixed(1)}%</div>
                    <div className="status">{healthStatus.text}</div>
                </div>

                {/* Accuracy Metrics */}
                <div className="accuracy-metrics">
                    <h3>Trading Accuracy</h3>
                    <div className="metric">
                        <label>Current:</label>
                        <span>{(monitoringData.accuracy * 100).toFixed(1)}%</span>
                    </div>
                    <div className="metric">
                        <label>Target:</label>
                        <span>80%</span>
                    </div>
                    <div className="progress-bar">
                        <div 
                            className="progress" 
                            style={{ width: `${monitoringData.accuracy * 100}%` }}
                        />
                    </div>
                </div>

                {/* Performance Chart */}
                <div className="performance-chart">
                    <h3>System Performance</h3>
                    <div className="chart-container">
                        <Line data={chartData} options={chartOptions} />
                    </div>
                </div>

                {/* Alerts and Issues */}
                <div className="system-alerts">
                    <h3>System Alerts</h3>
                    <div className="alerts-list">
                        {monitoringData.alerts.map((alert, index) => (
                            <div key={index} className={`alert ${alert.severity}`}>
                                <span className="timestamp">
                                    {new Date(alert.timestamp).toLocaleTimeString()}
                                </span>
                                <span className="message">{alert.message}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SystemMonitor;