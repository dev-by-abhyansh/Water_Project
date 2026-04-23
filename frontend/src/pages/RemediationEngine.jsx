import React, { useState, useEffect } from 'react';
import { Search, ShieldAlert, AlertCircle, Clock, CheckCircle2, Factory, Loader2, Info } from 'lucide-react';
import axios from 'axios';

export default function RemediationEngine() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchInput, setSearchInput] = useState('');
  
  // We want the system to auto-load an unsafe station, we can pass a dummy 'init' to let the backend pick the first unsafe one
  const [activeStation, setActiveStation] = useState('init');

  const fetchRemediation = async (stationId) => {
    setLoading(true);
    try {
      const response = await axios.get(`http://127.0.0.1:8000/api/remediation/${stationId}`);
      setData(response.data);
      setSearchInput(response.data.station_code);
    } catch (err) {
      console.error("Error fetching remediation:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRemediation(activeStation);
  }, [activeStation]);

  const handleSearch = (e) => {
    if (e.key === 'Enter' && searchInput.trim() !== '') {
      setActiveStation(searchInput);
    }
  };

  if (loading || !data) {
    return (
      <div className="p-8 min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 className="animate-spin text-blue-600" size={48} />
      </div>
    );
  }

  const isSafe = data.status === 'SAFE';

  return (
    <div className="p-8 min-h-screen bg-slate-50">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Remediation Engine</h2>
          <p className="text-slate-500 font-medium mt-1">AI-Generated Action Plans for Polluted Water Bodies</p>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-2.5 text-slate-400" size={20} />
          <input 
            type="text" 
            placeholder="Enter Station Code (Press Enter)..." 
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            onKeyDown={handleSearch}
            className="pl-10 pr-4 py-2 border border-slate-200 rounded-full w-80 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white shadow-sm"
          />
        </div>
      </div>

      {/* Target Details Card */}
      <div className="bg-slate-900 text-white p-6 rounded-2xl shadow-sm mb-8 flex justify-between items-center border border-slate-800">
        <div className="flex items-center gap-4">
          <div className={`p-4 rounded-xl ${isSafe ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
            {isSafe ? <CheckCircle2 size={32} /> : <Factory size={32} />}
          </div>
          <div>
            <p className="text-slate-400 font-bold uppercase tracking-wider text-sm">Target Location</p>
            <h3 className="text-2xl font-black">Station {data.station_code}: {data.station_name}</h3>
            <p className="text-slate-300 font-medium mt-1">{data.state}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-slate-400 font-bold uppercase tracking-wider text-sm">Primary Contaminant</p>
          <div className={`mt-1 inline-flex items-center gap-2 px-4 py-2 rounded-lg font-black text-lg ${isSafe ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
            <AlertCircle size={20} />
            {isSafe ? 'None Detected' : data.top_pollutant}
          </div>
        </div>
      </div>

      {/* Kanban Layout for Action Plan */}
      {isSafe ? (
        <div className="bg-green-50 border border-green-200 rounded-2xl p-10 text-center">
          <CheckCircle2 className="mx-auto text-green-500 mb-4" size={48} />
          <h3 className="text-2xl font-bold text-green-800 mb-2">No Remediation Required</h3>
          <p className="text-green-600 font-medium">This station is currently classified as safe according to BIS standards. Continue standard monitoring protocols.</p>
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-6">
          
          {/* Column 1: Immediate Action */}
          <div className="flex flex-col gap-4">
            <div className="bg-red-600 text-white p-4 rounded-xl shadow-sm flex items-center justify-between">
              <div className="flex items-center gap-2 font-bold uppercase tracking-wider text-sm">
                <ShieldAlert size={18} /> Immediate Action
              </div>
              <span className="text-xs font-bold bg-white/20 px-2 py-1 rounded-md">0-48 Hrs</span>
            </div>
            
            {data.actions.immediate.map((action, idx) => (
              <div key={idx} className="bg-white border-l-4 border-red-500 p-5 rounded-xl shadow-sm hover:shadow-md transition-shadow">
                <p className="text-slate-700 font-medium text-sm leading-relaxed mb-4">{action}</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold px-3 py-1 bg-slate-100 text-slate-600 rounded-full">{data.actions.dept_immediate}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Column 2: Short Term */}
          <div className="flex flex-col gap-4">
            <div className="bg-orange-500 text-white p-4 rounded-xl shadow-sm flex items-center justify-between">
              <div className="flex items-center gap-2 font-bold uppercase tracking-wider text-sm">
                <Clock size={18} /> Short Term
              </div>
              <span className="text-xs font-bold bg-white/20 px-2 py-1 rounded-md">1-3 Months</span>
            </div>
            
            {data.actions.short_term.map((action, idx) => (
              <div key={idx} className="bg-white border-l-4 border-orange-400 p-5 rounded-xl shadow-sm hover:shadow-md transition-shadow">
                <p className="text-slate-700 font-medium text-sm leading-relaxed mb-4">{action}</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold px-3 py-1 bg-slate-100 text-slate-600 rounded-full">{data.actions.dept_short}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Column 3: Long Term */}
          <div className="flex flex-col gap-4">
            <div className="bg-blue-600 text-white p-4 rounded-xl shadow-sm flex items-center justify-between">
              <div className="flex items-center gap-2 font-bold uppercase tracking-wider text-sm">
                <Info size={18} /> Long Term
              </div>
              <span className="text-xs font-bold bg-white/20 px-2 py-1 rounded-md">1+ Years</span>
            </div>
            
            {data.actions.long_term.map((action, idx) => (
              <div key={idx} className="bg-white border-l-4 border-blue-500 p-5 rounded-xl shadow-sm hover:shadow-md transition-shadow">
                <p className="text-slate-700 font-medium text-sm leading-relaxed mb-4">{action}</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold px-3 py-1 bg-slate-100 text-slate-600 rounded-full">{data.actions.dept_long}</span>
                </div>
              </div>
            ))}
          </div>

        </div>
      )}
    </div>
  );
}