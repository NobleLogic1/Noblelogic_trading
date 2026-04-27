import React, { useState, useEffect } from 'react';

const SimpleDashboard = () => {
  const [systemStatus, setSystemStatus] = useState('Loading...');
  const [backendConnected, setBackendConnected] = useState(false);

  useEffect(() => {
    testBackendConnection();
  }, []);

  const testBackendConnection = async () => {
    try {
      const response = await fetch('http://localhost:3001/api/health');
      if (response.ok) {
        const data = await response.json();
        setSystemStatus('Connected');
        setBackendConnected(true);
        console.log('Backend data:', data);
      } else {
        setSystemStatus('Backend Error');
      }
    } catch (error) {
      setSystemStatus('Connection Failed');
      console.error('Backend connection error:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-center">
          🚀 NobleLogic Trading System
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* System Status */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-semibold mb-4">System Status</h2>
            <div className={`text-2xl font-bold ${backendConnected ? 'text-green-400' : 'text-red-400'}`}>
              {systemStatus}
            </div>
          </div>

          {/* GPU Status */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-semibold mb-4">GPU Acceleration</h2>
            <div className="text-2xl font-bold text-blue-400">
              Ready
            </div>
          </div>

          {/* API Status */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-semibold mb-4">Binance.US API</h2>
            <div className="text-2xl font-bold text-green-400">
              Connected
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="flex flex-wrap gap-4">
            <button 
              onClick={testBackendConnection}
              className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold transition-colors"
            >
              Test Backend
            </button>
            <button className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-semibold transition-colors">
              Start GPU Charts
            </button>
            <button className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg font-semibold transition-colors">
              Run ML Analysis
            </button>
          </div>
        </div>

        {/* Connection Info */}
        <div className="mt-8 bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-semibold mb-4">Connection Info</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-400">Frontend:</span> http://localhost:5173
            </div>
            <div>
              <span className="text-gray-400">Backend:</span> http://localhost:3001
            </div>
            <div>
              <span className="text-gray-400">Status:</span> {backendConnected ? '✅ Online' : '❌ Offline'}
            </div>
            <div>
              <span className="text-gray-400">GPU:</span> Hardware Accelerated
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimpleDashboard;