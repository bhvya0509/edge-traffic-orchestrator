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
  const [metrics, setMetrics] = useState<TrafficMetrics>({ total: 0, auto: 0, car: 0, motorbike: 0, bus: 0, eriksha: 0 });
  const [status, setStatus] = useState<'Connecting' | 'Live' | 'Disconnected'>('Connecting');
  const [density, setDensity] = useState<'Low' | 'Moderate' | 'High'>('Low');

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws/traffic');
    
    socket.onopen = () => setStatus('Live');
    
    socket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      setMetrics(data);
      
      // Calculate dynamic density logic based on total vehicles
      if (data.total >= 15) setDensity('High');
      else if (data.total >= 7) setDensity('Moderate');
      else setDensity('Low');
    };
    
    socket.onclose = () => setStatus('Disconnected');
    
    return () => socket.close();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 p-6 font-sans">
      {/* Header */}
      <header className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
            Edge Traffic Orchestrator
          </h1>
          <p className="text-slate-400 mt-1">Real-time Intersection Telemetry</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-slate-400">System Status:</span>
          <div className={`px-4 py-1.5 rounded-full text-sm font-bold flex items-center gap-2 ${
            status === 'Live' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 
            status === 'Connecting' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 
            'bg-red-500/20 text-red-400 border border-red-500/30'
          }`}>
            <div className={`w-2 h-2 rounded-full ${status === 'Live' ? 'bg-emerald-400 animate-pulse' : 'bg-current'}`} />
            {status}
          </div>
        </div>
      </header>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Live Feed & Timeline */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Video Feed Panel */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
            <div className="border-b border-slate-800 bg-slate-900/50 px-4 py-3 flex justify-between items-center">
              <h2 className="font-semibold flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                Live Inference Feed
              </h2>
              <span className="text-xs text-slate-400 font-mono">Camera 01 - YOLOv8n</span>
            </div>
            <div className="aspect-video bg-slate-950 relative flex items-center justify-center">
              {/* To stream real video, replace this div with: */}
              {/* <img src="http://localhost:8000/video_feed" className="w-full h-full object-cover" alt="Live Feed" /> */}
              <div className="text-center text-slate-500">
                <p className="mb-2">Awaiting Video Stream</p>
                <p className="text-xs font-mono">Ready to connect to Python backend</p>
              </div>
            </div>
          </div>

          {/* Density Timeline */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
            <h2 className="font-semibold mb-4 text-slate-300">Traffic Density Timeline</h2>
            <div className="h-32 flex items-end gap-2">
              {/* A visual mockup of the timeline updating dynamically with the current total */}
              {[40, 25, 60, 30, 80, 45, 90, 50, 65, 30, 70, (metrics.total * 5) + 10].map((val, i) => (
                <div key={i} className="flex-1 bg-blue-500/20 rounded-t-sm hover:bg-blue-500/40 transition-colors" 
                     style={{ height: `${Math.min(val, 100)}%` }}></div>
              ))}
            </div>
          </div>

        </div>

        {/* Right Column: Telemetry Cards & Controls */}
        <div className="space-y-6">
          
          {/* Metrics Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2 bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 p-5 rounded-xl">
              <p className="text-sm text-slate-400 font-medium">Total Vehicles</p>
              <p className="text-4xl font-bold text-white mt-1">{metrics.total}</p>
              <div className="mt-3 text-sm flex justify-between items-center">
                <span className="text-slate-400">Current Density:</span>
                <span className={`font-medium ${density === 'High' ? 'text-red-400' : density === 'Moderate' ? 'text-amber-400' : 'text-emerald-400'}`}>
                  {density}
                </span>
              </div>
            </div>

            <MetricCard title="Cars" value={metrics.car} color="blue" />
            <MetricCard title="Motorbikes" value={metrics.motorbike} color="emerald" />
            <MetricCard title="Autos" value={metrics.auto} color="amber" />
            <MetricCard title="Buses" value={metrics.bus} color="purple" />
            <MetricCard title="E-Rickshaws" value={metrics.eriksha} color="pink" />
          </div>

          {/* Hardware Controls */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
            <h2 className="font-semibold mb-4 text-slate-300">Hardware Controls</h2>
            <div className="space-y-3">
              <button className="w-full bg-slate-800 hover:bg-slate-700 border border-slate-700 text-sm font-medium py-2.5 rounded-lg transition-colors flex justify-between px-4">
                <span>Toggle Intersection LEDs</span>
                <span className="text-emerald-400">Active</span>
              </button>
              <button className="w-full bg-slate-800 hover:bg-slate-700 border border-slate-700 text-sm font-medium py-2.5 rounded-lg transition-colors flex justify-between px-4">
                <span>Override Signal Phase</span>
                <span className="text-slate-400">Auto</span>
              </button>
              <button className="w-full bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 text-red-400 text-sm font-medium py-2.5 rounded-lg transition-colors">
                Emergency Stop (All Red)
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, color }: { title: string, value: number, color: string }) {
  const colorMap: Record<string, string> = {
    blue: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
    emerald: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    amber: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
    purple: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
    pink: 'text-pink-400 bg-pink-500/10 border-pink-500/20',
  };

  return (
    <div className={`border p-4 rounded-xl flex flex-col justify-between ${colorMap[color]}`}>
      <span className="text-sm font-medium opacity-80">{title}</span>
      <span className="text-3xl font-bold mt-2">{value}</span>
    </div>
  );
}
