import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Activity, AlertTriangle, Eye, ShieldAlert, FileText, Settings, LogOut } from 'lucide-react';

export default function Sidebar() {
  const location = useLocation();

  const navItems = [
    { name: 'Overview', path: '/overview', icon: LayoutDashboard },
    { name: 'Analytics', path: '/analytics', icon: Activity },
    { name: 'Alert System', path: '/alerts', icon: AlertTriangle },
    { name: 'Station Inspector', path: '/inspector', icon: Eye },
    { name: 'Remediation Engine', path: '/remediation', icon: ShieldAlert },
    { name: 'Reports', path: '/reports', icon: FileText },
  ];

  return (
    <div className="w-64 h-screen bg-slate-900 text-slate-300 flex flex-col fixed left-0 top-0 z-50">
      <div className="p-6 flex items-center gap-3 border-b border-slate-800">
        <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center text-white font-bold">W</div>
        <h1 className="text-white font-bold text-lg leading-tight">Water Quality<br/>Monitor</h1>
      </div>
      
      <div className="flex-1 py-6 px-4 space-y-2">
        {navItems.map((item) => {
          const isActive = location.pathname.includes(item.path);
          return (
            <Link 
              key={item.name}
              to={item.path}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive ? 'bg-blue-600 text-white' : 'hover:bg-slate-800 hover:text-white'
              }`}
            >
              <item.icon size={20} />
              <span className="font-medium">{item.name}</span>
            </Link>
          );
        })}
      </div>

      <div className="p-4 border-t border-slate-800 space-y-2">
        <button className="w-full flex items-center gap-3 px-4 py-2 hover:bg-slate-800 rounded-lg transition-colors">
          <Settings size={20} /> <span>Settings</span>
        </button>
        <button className="w-full flex items-center gap-3 px-4 py-2 hover:bg-slate-800 text-red-400 rounded-lg transition-colors">
          <LogOut size={20} /> <span>Sign Out</span>
        </button>
      </div>
    </div>
  );
}