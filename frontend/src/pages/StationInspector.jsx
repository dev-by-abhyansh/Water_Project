import React, { useState, useEffect } from 'react';
import { Search, Bell, User, AlertCircle, CheckCircle2, Clock, ShieldAlert, Loader2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import axios from 'axios';

export default function StationInspector() {
  // State for live data, loading status, and errors
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // State for the search bar
  const [searchInput, setSearchInput] = useState('2504');
  const [activeStation, setActiveStation] = useState('2504');

  // Fetch data from FastAPI backend
  const fetchStationData = async (stationId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`http://127.0.0.1:8000/api/station/${stationId}`);
      setData(response.data);
    } catch (err) {
      console.error("Error fetching data:", err);
      setError(`Could not find data for Station ${stationId}. Please check the code and try again.`);
    } finally {
      setLoading(false);
    }
  };

  // Run the fetch function when the activeStation changes
  useEffect(() => {
    if (activeStation) {
      fetchStationData(activeStation);
    }
  }, [activeStation]);

  // Handle when the user presses "Enter" in the search bar
  const handleSearch = (e) => {
    if (e.key === 'Enter') {
      setActiveStation(searchInput);
    }
  };

  // If the data is currently loading, show a spinner
  if (loading) {
    return (
      <div className="p-8 min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <Loader2 className="animate-spin text-blue-600 mx-auto mb-4" size={48} />
          <p className="text-slate-500 font-medium">Analyzing Station Data...</p>
        </div>
      </div>
    );
  }

  // If there was an error (e.g., station not found), show an error banner
  if (error || !data) {
    return (
      <div className="p-8 min-h-screen bg-slate-50">
        <div className="bg-red-50 text-red-600 p-6 rounded-2xl border border-red-200 flex items-start gap-4 shadow-sm max-w-3xl mx-auto mt-10">
          <AlertCircle size={32} className="mt-1 flex-shrink-0" />
          <div>
            <h2 className="text-xl font-bold mb-1">Station Not Found</h2>
            <p className="font-medium">{error}</p>
            <button 
              onClick={() => { setActiveStation('2504'); setSearchInput('2504'); }}
              className="mt-4 px-4 py-2 bg-red-100 text-red-700 rounded-lg font-bold text-sm hover:bg-red-200 transition-colors"
            >
              Return to Station 2504
            </button>
          </div>
        </div>
      </div>
    );
  }

  // --- UI RENDER (When Data is Loaded Successfully) ---
  
  // Dynamic styling based on whether the station is SAFE, MARGINAL, or UNSAFE
  const isUnsafe = data.status === 'UNSAFE';
  const statusColors = isUnsafe 
    ? { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', icon: 'bg-red-100 text-red-600' }
    : { bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'text-yellow-700', icon: 'bg-yellow-100 text-yellow-600' }; // Defaults to Warning colors if not unsafe

  // Map the parameters from the API into an array we can easily loop through for the grid
  const liveParameters = [
    { label: "pH Level", val: data.parameters.pH },
    { label: "Dissolved O2", val: data.parameters.DO },
    { label: "BOD", val: data.parameters.BOD },
    { label: "Fecal Coliform", val: data.parameters.Fecal_Coliform, alert: isUnsafe },
    { label: "Nitrate", val: data.parameters.Nitrate },
    { label: "Conductivity", val: data.parameters.Conductivity },
    { label: "Temperature", val: data.parameters.Temp },
    { label: "Turbidity", val: data.parameters.Turbidity },
  ];

  return (
    <div className="p-8 min-h-screen bg-slate-50">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h2 className="text-2xl font-bold text-slate-800">Station Inspector</h2>
        <div className="flex items-center gap-6">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 text-slate-400" size={20} />
            <input 
              type="text" 
              placeholder="Search Station Code (Press Enter)..." 
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onKeyDown={handleSearch}
              className="pl-10 pr-4 py-2 border border-slate-200 rounded-full w-72 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white shadow-sm"
            />
          </div>
          <span className="text-sm text-slate-500 font-medium">Live API Connected</span>
          <div className="flex gap-4 items-center border-l pl-4 border-slate-200">
            <Bell className="text-slate-500 cursor-pointer hover:text-slate-800" size={20} />
            <div className="w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center text-slate-600"><User size={16}/></div>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-12 gap-6">
        
        {/* Status Banner */}
        <div className={`col-span-12 ${statusColors.bg} border ${statusColors.border} rounded-2xl p-6 flex justify-between items-center shadow-sm`}>
          <div className="flex items-center gap-4">
            <div className={`p-3 rounded-full ${statusColors.icon}`}>
              <AlertCircle size={32} />
            </div>
            <div>
              <h3 className={`${statusColors.text} font-black text-2xl uppercase tracking-wider`}>
                Station {data.station_code} - Status: {data.status}
              </h3>
              <p className={`${statusColors.text} font-medium opacity-80`}>
                {data.station_name} • {data.state}
              </p>
            </div>
          </div>
          <div className={`text-right bg-white px-6 py-3 rounded-xl border ${statusColors.border} shadow-sm`}>
            <p className="text-slate-500 text-sm font-bold uppercase tracking-wide">AI Confidence</p>
            <p className="text-3xl font-black text-slate-800">{data.confidence}%</p>
          </div>
        </div>

        {/* WQI Score */}
        <div className="col-span-3 bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col items-center justify-center">
          <h4 className="text-slate-500 font-bold uppercase tracking-wider mb-4 text-sm w-full text-left">WQI Score</h4>
          <div className={`relative w-40 h-40 rounded-full border-[16px] border-slate-100 flex items-center justify-center transform rotate-45 ${isUnsafe ? 'border-t-red-500 border-r-red-500' : 'border-t-yellow-400 border-r-yellow-400'}`}>
            <div className="transform -rotate-45 text-center">
              <span className="text-4xl font-black text-slate-800">{data.wqi}</span>
              <p className={`${isUnsafe ? 'text-red-500' : 'text-yellow-600'} font-bold text-sm uppercase mt-1`}>{data.wqi_category}</p>
            </div>
          </div>
        </div>

        {/* Live Parameters */}
        <div className="col-span-5 bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
          <h4 className="text-slate-500 font-bold uppercase tracking-wider mb-4 text-sm">Live Parameters</h4>
          <div className="grid grid-cols-2 gap-4">
            {liveParameters.map((param, i) => (
              <div key={i} className={`p-4 rounded-xl border ${param.alert ? 'bg-red-50 border-red-200' : 'bg-slate-50 border-slate-100'}`}>
                <p className="text-sm text-slate-500 font-medium">{param.label}</p>
                <div className="flex justify-between items-end mt-1">
                  <span className={`text-xl font-bold ${param.alert ? 'text-red-700' : 'text-slate-800'}`}>
                    {param.val}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* SHAP Values Chart */}
        <div className="col-span-4 bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col">
          <h4 className="text-slate-500 font-bold uppercase tracking-wider mb-2 text-sm">Top Contaminants (SHAP)</h4>
          <p className="text-xs text-slate-400 mb-4">Impact on {data.status} Classification</p>
          <div className="flex-1 w-full min-h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.shap_values} layout="vertical" margin={{ top: 0, right: 30, left: 20, bottom: 0 }}>
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} style={{ fontSize: '12px', fill: '#64748b', fontWeight: 600 }} width={90}/>
                <Tooltip cursor={{fill: '#f8fafc'}} />
                <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={24}>
                  {data.shap_values.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill || '#ef4444'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Remediation Action Plan */}
        <div className="col-span-12 bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-6">
            <CheckCircle2 className={isUnsafe ? "text-red-500" : "text-yellow-500"} />
            <h4 className="text-slate-800 font-bold text-lg">
              Generated Action Plan for: <span className={isUnsafe ? "text-red-500" : "text-yellow-600"}>{data.shap_values[0]?.name || "Primary Contaminant"}</span>
            </h4>
          </div>
          
          <div className="grid grid-cols-3 gap-6">
            <div className="bg-red-50/50 border border-red-100 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-3 text-red-600 font-bold uppercase text-sm tracking-wider">
                <AlertCircle size={16} /> Immediate Action (0-48 Hrs)
              </div>
              <ul className="space-y-3 text-sm text-slate-700 font-medium">
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-400 mt-1.5 flex-shrink-0" />
                  Deploy mobile treatment units targeting {data.shap_values[0]?.name}.
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-400 mt-1.5 flex-shrink-0" />
                  Conduct localized inspections in the {data.state} catchment area.
                </li>
              </ul>
              <div className="mt-4 inline-block px-3 py-1 bg-white border border-red-200 text-red-600 text-xs font-bold rounded-full">Environmental Dept</div>
            </div>

            <div className="bg-orange-50/50 border border-orange-100 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-3 text-orange-600 font-bold uppercase text-sm tracking-wider">
                <Clock size={16} /> Short Term (1-3 Mos)
              </div>
              <ul className="space-y-3 text-sm text-slate-700 font-medium">
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-orange-400 mt-1.5 flex-shrink-0" />
                  Install advanced filtration and aeration units at the primary water intake point.
                </li>
              </ul>
              <div className="mt-4 inline-block px-3 py-1 bg-white border border-orange-200 text-orange-600 text-xs font-bold rounded-full">Water Works Dept</div>
            </div>

            <div className="bg-blue-50/50 border border-blue-100 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-3 text-blue-600 font-bold uppercase text-sm tracking-wider">
                <ShieldAlert size={16} /> Long Term (1+ Years)
              </div>
              <ul className="space-y-3 text-sm text-slate-700 font-medium">
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-1.5 flex-shrink-0" />
                  Upgrade municipal pipeline and treatment infrastructure in surrounding regions.
                </li>
              </ul>
              <div className="mt-4 inline-block px-3 py-1 bg-white border border-blue-200 text-blue-600 text-xs font-bold rounded-full">Urban Development</div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}