import React, { useState, useEffect } from 'react';
import './TestModeMonitor.css';

const TestModeMonitor = () => {
    const [testData, setTestData] = useState(null);
    const [performance, setPerformance] = useState(null);
    const [timeLeft, setTimeLeft] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const statusRes = await fetch('http://localhost:3001/api/test/status');
                const status = await statusRes.json();
                setTestData(status);

                // Calculate time left until 10-minute report
                const elapsedMs = Date.now() - status.startTime;
                const remainingMs = Math.max(0, 600000 - elapsedMs); // 10 minutes in ms
                setTimeLeft(Math.ceil(remainingMs / 1000));

                if (elapsedMs >= 600000) {
                    const perfRes = await fetch('http://localhost:3001/api/test/performance');
                    const perf = await perfRes.json();
                    setPerformance(perf);
                }
            } catch (error) {
                console.error('Error fetching test data:', error);
            }
        };

        // Update every second
        const interval = setInterval(fetchData, 1000);
        return () => clearInterval(interval);
    }, []);

    if (!testData) return <div>Loading...</div>;

    return (
        <div className="test-mode-monitor">
            <div className="status-panel">
                <h2>Test Mode Status</h2>
                <div className="metrics">
                    <div className="metric">
                        <label>Balance:</label>
                        <value>${testData.balance.toFixed(2)}</value>
                    </div>
                    <div className="metric">
                        <label>Active Positions:</label>
                        <value>{testData.activePositions.length}</value>
                    </div>
                    <div className="metric">
                        <label>Win Rate:</label>
                        <value>
                            {testData.testMetrics.totalTrades > 0
                                ? ((testData.testMetrics.successfulTrades / testData.testMetrics.totalTrades) * 100).toFixed(1)
                                : 0}%
                        </value>
                    </div>
                    <div className="metric">
                        <label>Total Trades:</label>
                        <value>{testData.testMetrics.totalTrades}</value>
                    </div>
                </div>
                {timeLeft > 0 ? (
                    <div className="report-countdown">
                        Performance Report in: {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}
                    </div>
                ) : performance ? (
                    <div className="performance-report">
                        <h3>Performance Analysis</h3>
                        <div className="suggestions">
                            {performance.improvementSuggestions.map((suggestion, i) => (
                                <div key={i} className={`suggestion ${suggestion.priority.toLowerCase()}`}>
                                    <strong>{suggestion.category}:</strong>
                                    <p>{suggestion.suggestion}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                ) : null}
            </div>
        </div>
    );
};

export default TestModeMonitor;