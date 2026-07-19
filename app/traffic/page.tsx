"use client";

import React, { useEffect, useState } from 'react';

interface TrafficMetrics {
  total: number;
  auto: number;
  car: number;
  motorbike: number;
  bus: number;
  eriksha: number;
}

export default function TrafficDashboard() {
  const [metrics, setMetrics] = useState<TrafficMetrics>({
    total: 0,
    auto: 0,
    car: 0,
    motorbike: 0,
    bus: 0,
    eriksha: 0,
  });
  
  const [status, setStatus] = useState<'Connecting' | 'Live' | 'Disconnected'>('Connecting');

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws/traffic');

    socket.onopen = () => {
      setStatus('Live');
      console.log('Connected to Edge AI Traffic Stream!');
    };

    socket.onmessage = (event) => {
      try {
        const liveData: TrafficMetrics = JSON.parse(event.data);
        setMetrics(liveData);
      } catch (error) {
        console.error('Error parsing telemetry frame:', error);
      }
    };

    socket.onclose = () => {
      setStatus('Disconnected');
      console.log('Stream disconnected.');
    };

    socket.onerror = (err) => {
      console.error('WebSocket Error:', err);
      setStatus('Disconnected');
    };

    return () => {
      socket.close();
    };
  }, []);

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif', backgroundColor: '#0f172a', color: '#f8fafc', minHeight: '100vh' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '32px' }}>
        <h2 style={{ margin: 0, fontSize: '24px', fontWeight: 600 }}>Edge Traffic Telemetry Dashboard</h2>
        <span style={{
          padding: '6px 12px',
          borderRadius: '9999px',
          fontSize: '12px',
          fontWeight: 'bold',
          backgroundColor: status === 'Live' ? '#1e293b' : '#311010',
          color: status === 'Live' ? '#4ade80' : '#f87171',
          border: status === 'Live' ? '1px solid #22c55e' : '1px solid #ef4444'
        }}>
          ● {status}
        </span>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '20px'
      }}>
        <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', padding: '24px', borderRadius: '12px' }}>
          <p style={{ margin: '0 0 8px 0', color: '#94a3b8', fontSize: '14px', fontWeight: 500 }}>Total Detected</p>
          <h1 style={{ margin: 0, fontSize: '36px', color: '#38bdf8' }}>{metrics.total}</h1>
        </div>
        <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', padding: '24px', borderRadius: '12px' }}>
          <p style={{ margin: '0 0 8px 0', color: '#94a3b8', fontSize: '14px', fontWeight: 500 }}>Autos</p>
          <h1 style={{ margin: 0, fontSize: '36px' }}>{metrics.auto}</h1>
        </div>
        <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', padding: '24px', borderRadius: '12px' }}>
          <p style={{ margin: '0 0 8px 0', color: '#94a3b8', fontSize: '14px', fontWeight: 500 }}>E-Rickshaws</p>
          <h1 style={{ margin: 0, fontSize: '36px' }}>{metrics.eriksha}</h1>
        </div>
        <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', padding: '24px', borderRadius: '12px' }}>
          <p style={{ margin: '0 0 8px 0', color: '#94a3b8', fontSize: '14px', fontWeight: 500 }}>Cars</p>
          <h1 style={{ margin: 0, fontSize: '36px' }}>{metrics.car}</h1>
        </div>
        <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', padding: '24px', borderRadius: '12px' }}>
          <p style={{ margin: '0 0 8px 0', color: '#94a3b8', fontSize: '14px', fontWeight: 500 }}>Motorbikes</p>
          <h1 style={{ margin: 0, fontSize: '36px' }}>{metrics.motorbike}</h1>
        </div>
      </div>
    </div>
  );
}
