import React, { useState, useEffect } from 'react';
import { Search, Filter, AlertTriangle, ShieldAlert, CheckCircle, Eye, Loader2 } from 'lucide-react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

export default function AlertSystem() {
  const [stations, setStations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('ALL'); // ALL, UNSAFE, MARGINAL, SAFE
  const navigate = useNavigate();

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/alerts');
        setStations(response.data);
      } catch (err) {
        console.error("Error fetching alerts:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAlerts();
  }, []);

  // Filter the stations based on the search bar and the pill buttons
  const filteredStations = stations.filter(station => {
    const matchesSearch = 
      station.station_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      station.station_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      station.state.toLowerCase().includes(searchTerm.toLowerCase());
      
    const matchesFilter = filter === 'ALL' || station.status.toUpperCase() === filter;
    
    return matchesSearch && matchesFilter;
  });

  if (loading) {
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
        <h2 className="text-2xl font-bold text-slate-800">Alert System</h2>
        <p className="text-slate-500 font-medium mt-1">Real-time triage and monitoring of all water bodies</p>
      </div>

      {/* Controls: Search and Filters */}
      <div className="flex justify-between items-center mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-2.5 text-slate-400" size={20} />
          <input 
            type="text" 
            placeholder="Search code, name, or state..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 pr-4 py-2 border border-slate-200 rounded-lg w-80 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white shadow-sm"
          />
        </div>

        <div className="flex gap-2 bg-white p-1 rounded-lg border border-slate-200 shadow-sm">
          <button 
            onClick={() => setFilter('ALL')}
            className={`px-4 py-1.5 rounded-md text-sm font-bold transition-colors ${filter === 'ALL' ? 'bg-slate-800 text-white' : 'text-slate-500 hover:bg-slate-100'}`}
          >
            All Stations
          </button>
          <button 
            onClick={() => setFilter('UNSAFE')}
            className={`px-4 py-1.5 rounded-md text-sm font-bold flex items-center gap-2 transition-colors ${filter === 'UNSAFE' ? 'bg-red-100 text-red-700' : 'text-slate-500 hover:bg-slate-100'}`}
          >
            <ShieldAlert size={16} /> Critical
          </button>
          <button 
            onClick={() => setFilter('MARGINAL')}
            className={`px-4 py-1.5 rounded-md text-sm font-bold flex items-center gap-2 transition-colors ${filter === 'MARGINAL' ? 'bg-yellow-100 text-yellow-700' : 'text-slate-500 hover:bg-slate-100'}`}
          >
            <AlertTriangle size={16} /> Warning
          </button>
          <button 
            onClick={() => setFilter('SAFE')}
            className={`px-4 py-1.5 rounded-md text-sm font-bold flex items-center gap-2 transition-colors ${filter === 'SAFE' ? 'bg-green-100 text-green-700' : 'text-slate-500 hover:bg-slate-100'}`}
          >
            <CheckCircle size={16} /> Clear
          </button>
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200">
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Station Details</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Region</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-wider">WQI</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Status</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-wider">AI Confidence</th>
                <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredStations.map((station, index) => {
                const isUnsafe = station.status.toUpperCase() === 'UNSAFE';
                const isMarginal = station.status.toUpperCase() === 'MARGINAL';
                
                return (
                  <tr key={index} className={`hover:bg-slate-50 transition-colors ${isUnsafe ? 'bg-red-50/30' : ''}`}>
                    <td className="p-4">
                      <p className="font-bold text-slate-800">{station.station_code}</p>
                      <p className="text-sm text-slate-500 truncate max-w-xs">{station.station_name}</p>
                    </td>
                    <td className="p-4 font-medium text-slate-600">{station.state}</td>
                    <td className="p-4">
                      <span className={`font-black ${isUnsafe ? 'text-red-600' : isMarginal ? 'text-yellow-600' : 'text-green-600'}`}>
                        {station.wqi}
                      </span>
                    </td>
                    <td className="p-4">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold uppercase ${
                        isUnsafe ? 'bg-red-100 text-red-700' : 
                        isMarginal ? 'bg-yellow-100 text-yellow-700' : 
                        'bg-green-100 text-green-700'
                      }`}>
                        {isUnsafe && <ShieldAlert size={12} />}
                        {isMarginal && <AlertTriangle size={12} />}
                        {!isUnsafe && !isMarginal && <CheckCircle size={12} />}
                        {station.status}
                      </span>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-2 bg-slate-100 rounded-full overflow-hidden">
                          <div 
                            className={`h-full ${station.confidence > 90 ? 'bg-green-500' : station.confidence > 75 ? 'bg-yellow-500' : 'bg-red-500'}`}
                            style={{ width: `${station.confidence}%` }}
                          />
                        </div>
                        <span className="text-sm font-bold text-slate-600">{station.confidence}%</span>
                      </div>
                    </td>
                    <td className="p-4 text-right">
                      {/* Clicking this button navigates to the Inspector page. 
                          In a full build, we would pass the station ID to auto-load it. */}
                      <button 
                        onClick={() => navigate('/inspector')}
                        className="inline-flex items-center gap-2 px-3 py-1.5 bg-white border border-slate-200 text-blue-600 rounded-lg text-sm font-bold hover:bg-blue-50 hover:border-blue-200 transition-colors shadow-sm"
                      >
                        <Eye size={16} /> Inspect
                      </button>
                    </td>
                  </tr>
                );
              })}
              {filteredStations.length === 0 && (
                <tr>
                  <td colSpan="6" className="p-8 text-center text-slate-500 font-medium">
                    No stations found matching your filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}