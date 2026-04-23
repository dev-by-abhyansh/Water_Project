import React from 'react';
import { FileDown, FileSpreadsheet, FileText, Printer, CheckCircle2 } from 'lucide-react';

export default function Reports() {
  
  // This function triggers the download from your FastAPI backend
  const handleDownloadCSV = () => {
    window.open('http://127.0.0.1:8000/api/export/csv', '_blank');
  };

  // This opens the browser's print dialog to save the page as a PDF
  const handlePrintPDF = () => {
    window.print();
  };

  return (
    <div className="p-8 min-h-screen bg-slate-50">
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <FileDown className="text-blue-600" /> Data Exports & Reports
        </h2>
        <p className="text-slate-500 font-medium mt-1">Download AI predictions, raw datasets, and executive summaries.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl">
        
        {/* Full Dataset CSV Download */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow flex flex-col">
          <div className="w-12 h-12 bg-green-50 text-green-600 rounded-xl flex items-center justify-center mb-4">
            <FileSpreadsheet size={24} />
          </div>
          <h3 className="font-bold text-slate-800 text-lg mb-2">Full AI Prediction Dataset</h3>
          <p className="text-sm text-slate-500 flex-1 mb-6">
            Export the complete dataset including WQI scores, status classifications, and AI confidence metrics for all monitored stations.
          </p>
          <button 
            onClick={handleDownloadCSV}
            className="w-full py-2.5 bg-slate-900 text-white font-bold rounded-lg hover:bg-slate-800 transition-colors flex items-center justify-center gap-2"
          >
            <FileDown size={18} /> Download CSV
          </button>
        </div>

        {/* Executive Summary PDF */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow flex flex-col">
          <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center mb-4">
            <FileText size={24} />
          </div>
          <h3 className="font-bold text-slate-800 text-lg mb-2">Executive Summary</h3>
          <p className="text-sm text-slate-500 flex-1 mb-6">
            Generate a printable layout of the current dashboard analytics, perfect for stakeholder meetings and compliance reporting.
          </p>
          <button 
            onClick={handlePrintPDF}
            className="w-full py-2.5 bg-blue-50 text-blue-700 font-bold rounded-lg hover:bg-blue-100 transition-colors flex items-center justify-center gap-2 border border-blue-200"
          >
            <Printer size={18} /> Print to PDF
          </button>
        </div>

      </div>

      {/* Audit Log / Success Banner */}
      <div className="mt-10 bg-slate-900 rounded-2xl p-6 shadow-sm border border-slate-800 max-w-6xl">
        <h3 className="font-bold text-white text-lg mb-4 border-b border-slate-700 pb-2">Recent System Exports</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-3 text-slate-300">
              <CheckCircle2 size={16} className="text-green-400" />
              <span>Automated Daily Backup - Predictions DB</span>
            </div>
            <span className="text-slate-500">Today, 02:00 AM</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-3 text-slate-300">
              <CheckCircle2 size={16} className="text-green-400" />
              <span>Automated Daily Backup - Features DB</span>
            </div>
            <span className="text-slate-500">Today, 02:05 AM</span>
          </div>
        </div>
      </div>

    </div>
  );
}