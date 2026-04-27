import React from 'react';

export default function TestDashboard() {
  return (
    <div style={{
      backgroundColor: '#0f172a', 
      color: '#ffffff', 
      padding: '2rem',
      minHeight: '100vh',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1 style={{ 
        fontSize: '2.5rem', 
        textAlign: 'center', 
        marginBottom: '2rem',
        color: '#3b82f6'
      }}>
        🚀 NobleLogic Trading System
      </h1>
      
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '1.5rem'
      }}>
        <div style={{
          backgroundColor: '#1e293b',
          padding: '1.5rem',
          borderRadius: '0.5rem',
          border: '1px solid #334155'
        }}>
          <h2 style={{ color: '#22c55e', marginBottom: '1rem' }}>✅ System Status</h2>
          <p style={{ fontSize: '1.25rem' }}>OPERATIONAL</p>
          <p style={{ color: '#64748b' }}>Frontend: React + Vite</p>
          <p style={{ color: '#64748b' }}>Backend: Flask + TensorFlow</p>
        </div>

        <div style={{
          backgroundColor: '#1e293b',
          padding: '1.5rem',
          borderRadius: '0.5rem',
          border: '1px solid #334155'
        }}>
          <h2 style={{ color: '#3b82f6', marginBottom: '1rem' }}>🎮 GPU Acceleration</h2>
          <p style={{ fontSize: '1.25rem' }}>READY</p>
          <p style={{ color: '#64748b' }}>WebGL Graphics: Enabled</p>
          <p style={{ color: '#64748b' }}>ML Processing: CPU Optimized</p>
        </div>

        <div style={{
          backgroundColor: '#1e293b',
          padding: '1.5rem',
          borderRadius: '0.5rem',
          border: '1px solid #334155'
        }}>
          <h2 style={{ color: '#f59e0b', marginBottom: '1rem' }}>🌐 API Status</h2>
          <p style={{ fontSize: '1.25rem' }}>CONNECTED</p>
          <p style={{ color: '#64748b' }}>Binance.US: Active</p>
          <p style={{ color: '#64748b' }}>Real-time Data: Streaming</p>
        </div>
      </div>

      <div style={{
        marginTop: '3rem',
        textAlign: 'center',
        padding: '2rem',
        backgroundColor: '#1e293b',
        borderRadius: '0.5rem',
        border: '1px solid #334155'
      }}>
        <h2 style={{ color: '#8b5cf6', marginBottom: '1rem' }}>🎯 Trading System Ready</h2>
        <p style={{ marginBottom: '1rem' }}>
          GPU-accelerated machine learning and WebGL-powered graphics are operational.
        </p>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button style={{
            backgroundColor: '#22c55e',
            color: 'white',
            padding: '0.75rem 1.5rem',
            border: 'none',
            borderRadius: '0.375rem',
            cursor: 'pointer',
            fontSize: '1rem',
            fontWeight: 'bold'
          }}>
            Start Live Trading
          </button>
          <button style={{
            backgroundColor: '#3b82f6',
            color: 'white',
            padding: '0.75rem 1.5rem',
            border: 'none',
            borderRadius: '0.375rem',
            cursor: 'pointer',
            fontSize: '1rem',
            fontWeight: 'bold'
          }}>
            View GPU Charts
          </button>
          <button style={{
            backgroundColor: '#8b5cf6',
            color: 'white',
            padding: '0.75rem 1.5rem',
            border: 'none',
            borderRadius: '0.375rem',
            cursor: 'pointer',
            fontSize: '1rem',
            fontWeight: 'bold'
          }}>
            ML Analysis
          </button>
        </div>
      </div>
    </div>
  );
}