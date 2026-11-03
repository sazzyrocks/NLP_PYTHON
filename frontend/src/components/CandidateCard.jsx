import React from 'react';
import { ChevronRight, ArrowRightLeft } from 'lucide-react';
import { getTier } from '../utils/scoring';

export default function CandidateCard({
  candidate,
  onInspect,
  onSelectForCompare,
  isSelectedForCompare,
}) {
  const tier = getTier(candidate.final_score);

  const getRankBadge = (rank) => {
    if (rank === 1) {
      return (
        <span className="h-7 w-7 rounded-full bg-amber-100 text-amber-700 border border-amber-300 font-extrabold text-xs flex items-center justify-center shadow-2xs">
          🥇 1
        </span>
      );
    }
    if (rank === 2) {
      return (
        <span className="h-7 w-7 rounded-full bg-slate-200 text-slate-700 border border-slate-300 font-extrabold text-xs flex items-center justify-center shadow-2xs">
          🥈 2
        </span>
      );
    }
    if (rank === 3) {
      return (
        <span className="h-7 w-7 rounded-full bg-amber-900/10 text-amber-800 border border-amber-800/30 font-extrabold text-xs flex items-center justify-center shadow-2xs">
          🥉 3
        </span>
      );
    }
    return (
      <span className="h-7 w-7 rounded-full bg-slate-100 text-slate-600 font-bold text-xs flex items-center justify-center border border-slate-200">
        #{rank}
      </span>
    );
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-md transition-all duration-200 p-5 flex flex-col justify-between">
      <div>
        {/* Top Header: Rank, Filename, Tier Badge */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center space-x-2.5 truncate">
            {getRankBadge(candidate.rank)}
            <div className="truncate">
              <h3 className="text-sm font-bold text-slate-900 truncate" title={candidate.filename}>
                {candidate.filename}
              </h3>
              <span className={`inline-block mt-0.5 text-[11px] px-2 py-0.5 rounded-md border font-semibold ${tier.color}`}>
                {tier.icon} {tier.label}
              </span>
            </div>
          </div>

          {/* Big Score Callout */}
          <div className="text-right shrink-0">
            <div className="text-2xl font-black text-slate-900 leading-none">
              {candidate.final_score.toFixed(1)}
              <span className="text-xs font-normal text-slate-400">/100</span>
            </div>
            <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Match Score</span>
          </div>
        </div>

        {/* Breakdown Progress Bars */}
        <div className="space-y-2 py-3 border-y border-slate-100 text-xs">
          {/* Semantic */}
          <div>
            <div className="flex justify-between text-[11px] font-medium text-slate-600 mb-0.5">
              <span>Semantic Similarity</span>
              <span className="font-mono font-bold text-indigo-600">{candidate.semantic_score.toFixed(1)}%</span>
            </div>
            <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-indigo-600 rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, candidate.semantic_score)}%` }}
              />
            </div>
          </div>

          {/* Skill Match */}
          <div>
            <div className="flex justify-between text-[11px] font-medium text-slate-600 mb-0.5">
              <span>Skill Coverage</span>
              <span className="font-mono font-bold text-emerald-600">
                {candidate.skill_score !== null ? `${candidate.skill_score.toFixed(1)}%` : 'N/A'}
              </span>
            </div>
            <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                style={{
                  width: `${candidate.skill_score !== null ? Math.min(100, candidate.skill_score) : 0}%`,
                }}
              />
            </div>
          </div>

          {/* Experience */}
          <div>
            <div className="flex justify-between text-[11px] font-medium text-slate-600 mb-0.5">
              <span>Experience Section</span>
              <span className="font-mono font-bold text-amber-600">
                {candidate.experience_section_score.toFixed(1)}%
              </span>
            </div>
            <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-amber-500 rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, candidate.experience_section_score)}%` }}
              />
            </div>
          </div>

          {/* Lexical */}
          <div>
            <div className="flex justify-between text-[11px] font-medium text-slate-600 mb-0.5">
              <span>Lexical Overlap (TF-IDF)</span>
              <span className="font-mono font-bold text-cyan-600">{candidate.lexical_score.toFixed(1)}%</span>
            </div>
            <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-cyan-500 rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, candidate.lexical_score)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Matched Skills Chips */}
        <div className="mt-3">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[11px] font-semibold text-slate-600">
              Matched Skills ({candidate.matched_skills.length}):
            </span>
            {candidate.missing_skills.length > 0 && (
              <span className="text-[10px] text-rose-500 font-medium">
                {candidate.missing_skills.length} missing
              </span>
            )}
          </div>
          <div className="flex flex-wrap gap-1 max-h-16 overflow-hidden">
            {candidate.matched_skills.length > 0 ? (
              candidate.matched_skills.slice(0, 7).map((skill) => (
                <span
                  key={skill}
                  className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200/80"
                >
                  {skill}
                </span>
              ))
            ) : (
              <span className="text-[11px] text-slate-400 italic">No direct taxonomy skills found</span>
            )}
            {candidate.matched_skills.length > 7 && (
              <span className="text-[10px] text-slate-400 font-medium px-1.5 py-0.5">
                +{candidate.matched_skills.length - 7} more
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Footer Actions */}
      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
        <button
          type="button"
          onClick={() => onSelectForCompare(candidate)}
          className={`flex items-center space-x-1.5 text-xs font-semibold px-2.5 py-1.5 rounded-lg border transition cursor-pointer ${
            isSelectedForCompare
              ? 'bg-indigo-600 text-white border-indigo-600'
              : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-indigo-50 hover:text-indigo-600'
          }`}
        >
          <ArrowRightLeft className="h-3 w-3" />
          <span>{isSelectedForCompare ? 'Selected' : 'Compare'}</span>
        </button>

        <button
          type="button"
          onClick={() => onInspect(candidate)}
          className="flex items-center space-x-1 text-xs font-bold text-indigo-600 hover:text-indigo-800 hover:underline cursor-pointer"
        >
          <span>Deep Dive Analysis</span>
          <ChevronRight className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}

