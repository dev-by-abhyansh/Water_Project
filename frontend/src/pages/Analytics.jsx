import React, { useState, useEffect } from 'react';
import { LineChart, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, Cell } from 'recharts';
import { Activity, Droplets, TrendingUp, Loader2 } from 'lucide-react';
import axios from 'axios';

export default function Analytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/analytics');
        setData(response.data);
      } catch (err) {
        console.error("Error fetching analytics:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
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
        <h2 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <Activity className="text-blue-600" /> System Analytics
        </h2>
        <p className="text-slate-500 font-medium mt-1">Historical trends and pollutant distribution analysis</p>
      </div>

      <div className="grid grid-cols-12 gap-6">
        
        {/* 12-Month WQI Trend (Large Chart) */}
        <div className="col-span-12 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="font-bold text-slate-800 text-lg">12-Month WQI Trend</h3>
              <p className="text-sm text-slate-500">Average regional Water Quality Index over time</p>
            </div>
            <div className="flex items-center gap-2 bg-blue-50 text-blue-700 px-3 py-1.5 rounded-lg text-sm font-bold">
              <TrendingUp size={16} /> Seasonal Spike Detected
            </div>
          </div>
          
          <div className="w-full h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.monthly_trend} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorWqi" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                <Tooltip 
                  contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  labelStyle={{ fontWeight: 'bold', color: '#1e293b' }}
                />
                <Area type="monotone" dataKey="avg_wqi" name="Average WQI" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorWqi)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Pollutants Bar Chart */}
        <div className="col-span-7 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center gap-2 mb-6">
            <Droplets className="text-red-500" />
            <h3 className="font-bold text-slate-800 text-lg">Primary Pollutants</h3>
          </div>
          <div className="w-full h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.pollutant_breakdown} layout="vertical" margin={{ top: 0, right: 30, left: 40, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                <XAxis type="number" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: '#475569', fontSize: 12, fontWeight: 600 }} width={100} />
                <Tooltip cursor={{fill: '#f8fafc'}} />
                <Bar dataKey="count" name="Stations Affected" fill="#ef4444" radius={[0, 4, 4, 0]} barSize={24} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* WQI Category Distribution */}
        <div className="col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <h3 className="font-bold text-slate-800 text-lg mb-6">Classification Volume</h3>
          <div className="w-full h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.wqi_distribution} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="category" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12, fontWeight: 600 }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                <Tooltip cursor={{fill: '#f8fafc'}} />
                <Bar dataKey="count" name="Total Stations" radius={[4, 4, 0, 0]} barSize={40}>
                  {data.wqi_distribution.map((entry, index) => {
                    // Dynamically color the bars based on category safety
                    const isPoor = entry.category.toLowerCase().includes('poor') || entry.category.toLowerCase().includes('unsafe');
                    const isGood = entry.category.toLowerCase().includes('good') || entry.category.toLowerCase().includes('excellent');
                    return <Cell key={`cell-${index}`} fill={isPoor ? '#ef4444' : isGood ? '#10b981' : '#f59e0b'} />;
                  })}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
}