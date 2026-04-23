import React, { useState, useEffect } from 'react';
import { Activity, AlertTriangle, ShieldCheck, Target, Loader2, Clock } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';

export default function Overview() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOverview = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/overview');
        setData(response.data);
      } catch (err) {
        console.error("Error fetching overview:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchOverview();
  }, []);

  if (loading || !data) {
    return (
      <div className="p-8 min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 className="animate-spin text-blue-600" size={48} />
      </div>
    );
  }

  return (
    <div className="p-8 min-h-screen bg-slate-50">
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-800">System Overview</h2>
        <p className="text-slate-500 font-medium mt-1">Government Water Quality Monitoring Command Center</p>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-4 gap-6 mb-6">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-4 bg-blue-50 text-blue-600 rounded-xl"><Target size={24} /></div>
          <div>
            <p className="text-sm font-bold text-slate-500 uppercase tracking-wider">Total Stations</p>
            <p className="text-3xl font-black text-slate-800">{data.kpis.total_stations}</p>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-4 bg-purple-50 text-purple-600 rounded-xl"><Activity size={24} /></div>
          <div>
            <p className="text-sm font-bold text-slate-500 uppercase tracking-wider">Avg WQI</p>
            <p className="text-3xl font-black text-slate-800">{data.kpis.avg_wqi}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-4 bg-red-50 text-red-600 rounded-xl"><AlertTriangle size={24} /></div>
          <div>
            <p className="text-sm font-bold text-slate-500 uppercase tracking-wider">Critical Alerts</p>
            <p className="text-3xl font-black text-red-600">{data.kpis.critical_alerts}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-4 bg-green-50 text-green-600 rounded-xl"><ShieldCheck size={24} /></div>
          <div>
            <p className="text-sm font-bold text-slate-500 uppercase tracking-wider">AI Confidence</p>
            <p className="text-3xl font-black text-slate-800">{data.kpis.avg_confidence}%</p>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-12 gap-6">
        
        {/* Donut Chart: Safety Distribution */}
        <div className="col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col">
          <h3 className="font-bold text-slate-800 text-lg mb-1">Safety Distribution</h3>
          <p className="text-sm text-slate-500 mb-4">Proportion of safe vs unsafe water bodies</p>
          <div className="flex-1 min-h-[250px] flex items-center justify-center relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={data.distribution} innerRadius={80} outerRadius={110} paddingAngle={5} dataKey="value" stroke="none">
                  {data.distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip cursor={{fill: '#f8fafc'}} />
              </PieChart>
            </ResponsiveContainer>
            {/* Center Text for Donut */}
            <div className="absolute flex flex-col items-center justify-center pointer-events-none">
              <span className="text-3xl font-black text-slate-800">{data.kpis.total_stations}</span>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total</span>
            </div>
          </div>
          {/* Custom Legend */}
          <div className="flex justify-center gap-6 mt-4">
            {data.distribution.map((item) => (
              <div key={item.name} className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></span>
                <span className="text-sm font-semibold text-slate-600">{item.name} ({item.value})</span>
              </div>
            ))}
          </div>
        </div>

        {/* Bar Chart: Top Unsafe States */}
        <div className="col-span-7 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col">
          <h3 className="font-bold text-slate-800 text-lg mb-1">Top Unsafe Regions</h3>
          <p className="text-sm text-slate-500 mb-4">States with the highest count of critical violations</p>
          <div className="flex-1 min-h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.top_states} layout="vertical" margin={{ top: 0, right: 30, left: 40, bottom: 0 }}>
                <XAxis type="number" hide />
                <YAxis dataKey="state" type="category" axisLine={false} tickLine={false} style={{ fontSize: '12px', fill: '#64748b', fontWeight: 600 }} width={120} />
                <Tooltip cursor={{fill: '#f8fafc'}} />
                <Bar dataKey="count" fill="#ef4444" radius={[0, 4, 4, 0]} barSize={32} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Activity Ticker */}
        <div className="col-span-12 bg-slate-900 rounded-2xl p-4 shadow-sm flex items-center justify-between text-slate-300">
          <div className="flex items-center gap-3">
            <Clock size={18} className="text-blue-400" />
            <span className="text-sm font-medium">Latest Model Sync: Complete. All 2023 predictions loaded successfully.</span>
          </div>
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">System Online</span>
        </div>

      </div>
    </div>
  );
}