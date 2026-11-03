import React from 'react';
import { Trophy, BarChart3, Target, Users } from 'lucide-react';
import { getTier } from '../utils/scoring';

export default function KPICards({ results }) {
  if (!results || results.length === 0) return null;

  const topCandidate = results[0];
  const topTier = getTier(topCandidate.final_score);
  const avgScore = (results.reduce((acc, c) => acc + c.final_score, 0) / results.length).toFixed(1);

  const candidatesWithSkill = results.filter((c) => c.skill_score !== null);
  const avgSkill = candidatesWithSkill.length > 0
    ? (candidatesWithSkill.reduce((acc, c) => acc + c.skill_score, 0) / candidatesWithSkill.length).toFixed(1)
    : 'N/A';

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {/* Top Candidate */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm hover:shadow-md transition duration-200">
        <div className="flex items-center justify-between text-slate-500 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Top Match</span>
          <span className="p-2 rounded-lg bg-amber-50 text-amber-600 border border-amber-200/50">
            <Trophy className="h-4 w-4" />
          </span>
        </div>
        <div className="flex items-baseline space-x-2">
          <span className="text-3xl font-extrabold text-slate-900">{topCandidate.final_score.toFixed(1)}</span>
          <span className="text-sm font-medium text-slate-400">/ 100</span>
          <span className={`text-xs px-2 py-0.5 rounded-md border font-semibold ml-auto ${topTier.color}`}>
            {topTier.label}
          </span>
        </div>
        <p className="text-xs text-slate-600 font-medium truncate mt-2" title={topCandidate.filename}>
          {topCandidate.filename}
        </p>
      </div>

      {/* Cohort Average */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm hover:shadow-md transition duration-200">
        <div className="flex items-center justify-between text-slate-500 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Cohort Average</span>
          <span className="p-2 rounded-lg bg-indigo-50 text-indigo-600 border border-indigo-200/50">
            <BarChart3 className="h-4 w-4" />
          </span>
        </div>
        <div className="flex items-baseline space-x-1">
          <span className="text-3xl font-extrabold text-slate-900">{avgScore}</span>
          <span className="text-sm font-medium text-slate-400">/ 100</span>
        </div>
        <p className="text-xs text-slate-500 mt-2">Overall mean fit across cohort</p>
      </div>

      {/* Avg Skill Match */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm hover:shadow-md transition duration-200">
        <div className="flex items-center justify-between text-slate-500 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Avg Skill Coverage</span>
          <span className="p-2 rounded-lg bg-emerald-50 text-emerald-600 border border-emerald-200/50">
            <Target className="h-4 w-4" />
          </span>
        </div>
        <div className="flex items-baseline space-x-1">
          <span className="text-3xl font-extrabold text-slate-900">{avgSkill}</span>
          <span className="text-sm font-medium text-slate-400">{avgSkill !== 'N/A' ? '%' : ''}</span>
        </div>
        <p className="text-xs text-slate-500 mt-2">JD required taxonomy match ratio</p>
      </div>

      {/* Total Evaluated */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm hover:shadow-md transition duration-200">
        <div className="flex items-center justify-between text-slate-500 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Candidates</span>
          <span className="p-2 rounded-lg bg-blue-50 text-blue-600 border border-blue-200/50">
            <Users className="h-4 w-4" />
          </span>
        </div>
        <div className="flex items-baseline space-x-1">
          <span className="text-3xl font-extrabold text-slate-900">{results.length}</span>
          <span className="text-sm font-medium text-slate-400">Processed</span>
        </div>
        <p className="text-xs text-slate-500 mt-2">Parsed in-memory without disk writes</p>
      </div>
    </div>
  );
}

