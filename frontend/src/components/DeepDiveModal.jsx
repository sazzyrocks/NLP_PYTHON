import React, { useEffect } from 'react';
import { X, CheckCircle, Lightbulb, FileText, Target } from 'lucide-react';
import { getTier } from '../utils/scoring';

export default function DeepDiveModal({ candidate, onClose }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!candidate) return null;

  const tier = getTier(candidate.final_score);

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-3xl w-full shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-5 bg-gradient-to-r from-slate-900 to-indigo-950 text-white flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="h-8 w-8 rounded-full bg-white/10 text-indigo-300 flex items-center justify-center font-bold text-sm">
              #{candidate.rank}
            </span>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-lg font-bold truncate max-w-md" title={candidate.filename}>
                  {candidate.filename}
                </h2>
                <span className={`text-xs px-2 py-0.5 rounded-md font-semibold border ${tier.color}`}>
                  {tier.icon} {tier.label}
                </span>
              </div>
              <p className="text-xs text-indigo-200/80 mt-0.5">Comprehensive Explainable Candidate Evaluation</p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="h-8 w-8 rounded-full bg-white/10 hover:bg-white/20 text-slate-300 hover:text-white flex items-center justify-center transition cursor-pointer"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Scrollable Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Top Score Matrix */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            <div className="bg-indigo-50/60 rounded-xl p-3 border border-indigo-100 text-center col-span-2 sm:col-span-1">
              <span className="text-[10px] uppercase font-bold text-indigo-700 tracking-wider">Final Match</span>
              <div className="text-2xl font-black text-indigo-950 mt-1">{candidate.final_score.toFixed(1)}</div>
              <span className="text-[10px] text-indigo-500 font-medium">Weighted Score</span>
            </div>

            <div className="bg-slate-50 rounded-xl p-3 border border-slate-200/70 text-center">
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Semantic</span>
              <div className="text-xl font-bold text-slate-900 mt-1">{candidate.semantic_score.toFixed(1)}%</div>
              <span className="text-[10px] text-slate-400">Embedding Sim</span>
            </div>

            <div className="bg-slate-50 rounded-xl p-3 border border-slate-200/70 text-center">
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Skills</span>
              <div className="text-xl font-bold text-slate-900 mt-1">
                {candidate.skill_score !== null ? `${candidate.skill_score.toFixed(1)}%` : 'N/A'}
              </div>
              <span className="text-[10px] text-slate-400">Taxonomy Match</span>
            </div>

            <div className="bg-slate-50 rounded-xl p-3 border border-slate-200/70 text-center">
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Experience</span>
              <div className="text-xl font-bold text-slate-900 mt-1">
                {candidate.experience_section_score.toFixed(1)}%
              </div>
              <span className="text-[10px] text-slate-400">Section Align</span>
            </div>

            <div className="bg-slate-50 rounded-xl p-3 border border-slate-200/70 text-center">
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Lexical</span>
              <div className="text-xl font-bold text-slate-900 mt-1">{candidate.lexical_score.toFixed(1)}%</div>
              <span className="text-[10px] text-slate-400">TF-IDF Overlap</span>
            </div>
          </div>

          {/* Actionable Tailoring Recommendations */}
          <div>
            <div className="flex items-center space-x-2 mb-3">
              <Lightbulb className="h-4 w-4 text-amber-500" />
              <h3 className="text-sm font-bold text-slate-900">Tailoring & Resume Optimization Advice</h3>
            </div>

            {candidate.suggestions && candidate.suggestions.length > 0 ? (
              <div className="space-y-2">
                {candidate.suggestions.map((s, idx) => (
                  <div
                    key={idx}
                    className="flex items-start space-x-2.5 p-3 rounded-lg bg-amber-50/70 border border-amber-200/70 text-xs text-amber-950 leading-relaxed"
                  >
                    <span className="text-amber-600 font-bold mt-0.5">•</span>
                    <span>{typeof s === 'string' ? s : s.suggestion}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-900 flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-emerald-600 shrink-0" />
                <span>Profile strongly aligns with job description requirements. No immediate critical gaps detected.</span>
              </div>
            )}
          </div>

          {/* Detailed Skill Breakdown */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <Target className="h-4 w-4 text-indigo-600" />
              <span>Extracted Taxonomy Skill Breakdown</span>
            </h3>

            {/* Matched Skills */}
            <div className="p-4 rounded-xl bg-emerald-50/50 border border-emerald-200/60">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-emerald-900 flex items-center space-x-1.5">
                  <span className="h-2 w-2 rounded-full bg-emerald-500" />
                  <span>Matched Skills ({candidate.matched_skills.length})</span>
                </span>
                <span className="text-[10px] text-emerald-700 font-medium">Present in both Resume & JD</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {candidate.matched_skills.length > 0 ? (
                  candidate.matched_skills.map((skill) => (
                    <span
                      key={skill}
                      className="text-xs font-semibold px-2.5 py-1 rounded-full bg-white text-emerald-800 border border-emerald-300 shadow-2xs"
                    >
                      {skill}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-400 italic">No direct matches</span>
                )}
              </div>
            </div>

            {/* Missing Skills */}
            <div className="p-4 rounded-xl bg-rose-50/50 border border-rose-200/60">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-rose-900 flex items-center space-x-1.5">
                  <span className="h-2 w-2 rounded-full bg-rose-500" />
                  <span>Missing JD Skills ({candidate.missing_skills.length})</span>
                </span>
                <span className="text-[10px] text-rose-700 font-medium">Required by JD, absent in candidate</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {candidate.missing_skills.length > 0 ? (
                  candidate.missing_skills.map((skill) => (
                    <span
                      key={skill}
                      className="text-xs font-semibold px-2.5 py-1 rounded-full bg-white text-rose-800 border border-rose-300 shadow-2xs"
                    >
                      {skill}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-emerald-700 font-medium">All specified JD skills matched!</span>
                )}
              </div>
            </div>

            {/* Extra Skills */}
            {candidate.extra_skills && candidate.extra_skills.length > 0 && (
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/70">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-slate-700 flex items-center space-x-1.5">
                    <span className="h-2 w-2 rounded-full bg-indigo-500" />
                    <span>Bonus Skills Detected ({candidate.extra_skills.length})</span>
                  </span>
                  <span className="text-[10px] text-slate-500 font-medium">Additional capabilities on resume</span>
                </div>
                <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto">
                  {candidate.extra_skills.map((skill) => (
                    <span
                      key={skill}
                      className="text-xs font-medium px-2.5 py-1 rounded-full bg-white text-slate-700 border border-slate-200 shadow-2xs"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Section Scores if available */}
          {candidate.section_scores && Object.keys(candidate.section_scores).length > 0 && (
            <div>
              <h3 className="text-sm font-bold text-slate-900 mb-2 flex items-center space-x-2">
                <FileText className="h-4 w-4 text-indigo-600" />
                <span>Section-Aware Semantic Alignment</span>
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {Object.entries(candidate.section_scores).map(([sec, score]) => (
                  <div key={sec} className="bg-slate-50 rounded-lg p-2.5 border border-slate-200 text-center">
                    <span className="text-[11px] font-semibold text-slate-600 capitalize block truncate">
                      {sec}
                    </span>
                    <span className="text-base font-bold text-slate-900 font-mono mt-0.5 block">
                      {typeof score === 'number' ? `${score.toFixed(1)}%` : score}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-200 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-200 hover:bg-slate-300 text-slate-800 text-xs font-semibold transition cursor-pointer"
          >
            Close Deep Dive
          </button>
        </div>
      </div>
    </div>
  );
}

