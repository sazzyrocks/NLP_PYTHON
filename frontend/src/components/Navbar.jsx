import React from 'react';
import { FileText, Cpu, CheckCircle2, AlertCircle } from 'lucide-react';

export default function Navbar({ backendStatus }) {
  return (
    <header className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border-b border-indigo-900/50 shadow-lg text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="h-11 w-11 rounded-xl bg-indigo-600/30 border border-indigo-400/40 flex items-center justify-center text-indigo-300 shadow-inner">
            <FileText className="h-6 w-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-indigo-100 to-indigo-300 bg-clip-text text-transparent">
                Semantic Resume Ranker
              </h1>
              <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-400/30">
                v2.0 React
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Explainable NLP screening powered by dense embeddings & spaCy phrase matching
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="hidden sm:flex items-center space-x-2 text-xs px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 shadow-sm">
            <Cpu className="h-3.5 w-3.5 text-indigo-400" />
            <span className="text-slate-300">Model:</span>
            <span className="font-mono text-indigo-300 font-medium">all-MiniLM-L6-v2</span>
          </div>

          <div
            className={`flex items-center space-x-1.5 text-xs px-3 py-1.5 rounded-lg border font-medium ${
              backendStatus === 'healthy'
                ? 'bg-emerald-950/40 text-emerald-300 border-emerald-500/40'
                : backendStatus === 'connecting'
                ? 'bg-amber-950/40 text-amber-300 border-amber-500/40'
                : 'bg-rose-950/40 text-rose-300 border-rose-500/40'
            }`}
          >
            {backendStatus === 'healthy' ? (
              <>
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                <span>Backend Online</span>
              </>
            ) : backendStatus === 'connecting' ? (
              <>
                <span className="h-2 w-2 rounded-full bg-amber-400 animate-pulse" />
                <span>Connecting...</span>
              </>
            ) : (
              <>
                <AlertCircle className="h-3.5 w-3.5 text-rose-400" />
                <span>Backend Offline</span>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

