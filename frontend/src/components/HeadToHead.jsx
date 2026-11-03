import React, { useState, useEffect } from 'react';
import { ArrowRightLeft, Trophy } from 'lucide-react';
import { getTier } from '../utils/scoring';

export default function HeadToHead({ results, initialCandidates }) {
  const [candidateAId, setCandidateAId] = useState(
    initialCandidates?.[0]?.filename || results[0]?.filename || ''
  );
  const [candidateBId, setCandidateBId] = useState(
    initialCandidates?.[1]?.filename || results[1]?.filename || results[0]?.filename || ''
  );

  useEffect(() => {
    if (initialCandidates && initialCandidates.length >= 2) {
      setCandidateAId(initialCandidates[0].filename);
      setCandidateBId(initialCandidates[1].filename);
    }
  }, [initialCandidates]);

  const candidateA = results.find((c) => c.filename === candidateAId) || results[0];
  const candidateB = results.find((c) => c.filename === candidateBId) || results[1] || results[0];

  if (!candidateA || !candidateB) return null;

  const scoreA = candidateA.final_score;
  const scoreB = candidateB.final_score;
  const delta = (scoreA - scoreB).toFixed(1);
  const isTie = Math.abs(scoreA - scoreB) < 0.01;
  const winner = scoreA > scoreB ? candidateA : candidateB;

  const tierA = getTier(scoreA);
  const tierB = getTier(scoreB);

  // Skill sets calculation
  const setA = new Set(candidateA.matched_skills || []);
  const setB = new Set(candidateB.matched_skills || []);

  const sharedSkills = [...setA].filter((x) => setB.has(x)).sort();
  const onlyA = [...setA].filter((x) => !setB.has(x)).sort();
  const onlyB = [...setB].filter((x) => !setA.has(x)).sort();

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
      <div className="flex items-center space-x-2 pb-4 mb-6 border-b border-slate-100">
        <ArrowRightLeft className="h-5 w-5 text-indigo-600" />
        <h2 className="text-base font-bold text-slate-900">Head-to-Head Candidate Comparison</h2>
      </div>

      {/* Selectors */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1.5">
            Candidate 🅰️
          </label>
          <select
            value={candidateAId}
            onChange={(e) => setCandidateAId(e.target.value)}
            className="w-full text-xs font-medium p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
          >
            {results.map((c) => (
              <option key={c.filename} value={c.filename}>
                #{c.rank} - {c.filename} ({c.final_score.toFixed(1)}/100)
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1.5">
            Candidate 🅱️
          </label>
          <select
            value={candidateBId}
            onChange={(e) => setCandidateBId(e.target.value)}
            className="w-full text-xs font-medium p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
          >
            {results.map((c) => (
              <option key={c.filename} value={c.filename}>
                #{c.rank} - {c.filename} ({c.final_score.toFixed(1)}/100)
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Winner Banner */}
      <div className="p-4 rounded-xl bg-indigo-50/70 border border-indigo-200/80 mb-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-full bg-indigo-600 text-white flex items-center justify-center shrink-0 shadow-sm">
            <Trophy className="h-5 w-5" />
          </div>
          <div>
            <div className="text-xs text-indigo-700 font-semibold uppercase tracking-wider">Evaluation Verdict</div>
            <div className="text-sm font-bold text-slate-900">
              {isTie ? (
                <span>It is an exact tie between both candidates!</span>
              ) : (
                <span>
                  Winner: <strong className="text-indigo-950 font-black">{winner.filename}</strong>
                </span>
              )}
            </div>
          </div>
        </div>

        {!isTie && (
          <span className="text-xs px-3 py-1.5 rounded-lg bg-white border border-indigo-200 text-indigo-900 font-bold font-mono shadow-2xs">
            Margin: {delta > 0 ? `+${delta}` : delta} pts in favor of 🅰️
          </span>
        )}
      </div>

      {/* Comparison Table */}
      <div className="overflow-x-auto border border-slate-200 rounded-xl mb-6">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-bold">
              <th className="p-3">Evaluation Metric</th>
              <th className="p-3">
                🅰️ {candidateA.filename}
                <span className={`ml-2 text-[10px] px-1.5 py-0.5 rounded font-semibold border ${tierA.color}`}>
                  {tierA.label}
                </span>
              </th>
              <th className="p-3">
                🅱️ {candidateB.filename}
                <span className={`ml-2 text-[10px] px-1.5 py-0.5 rounded font-semibold border ${tierB.color}`}>
                  {tierB.label}
                </span>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-medium text-slate-800">
            <tr className="bg-indigo-50/30 font-bold">
              <td className="p-3">Final Match Score</td>
              <td className="p-3 font-mono text-indigo-700 text-sm">{candidateA.final_score.toFixed(1)}/100</td>
              <td className="p-3 font-mono text-indigo-700 text-sm">{candidateB.final_score.toFixed(1)}/100</td>
            </tr>
            <tr>
              <td className="p-3 text-slate-600">Semantic Similarity</td>
              <td className="p-3 font-mono">{candidateA.semantic_score.toFixed(1)}%</td>
              <td className="p-3 font-mono">{candidateB.semantic_score.toFixed(1)}%</td>
            </tr>
            <tr>
              <td className="p-3 text-slate-600">Taxonomy Skill Match</td>
              <td className="p-3 font-mono">
                {candidateA.skill_score !== null ? `${candidateA.skill_score.toFixed(1)}%` : 'N/A'}
              </td>
              <td className="p-3 font-mono">
                {candidateB.skill_score !== null ? `${candidateB.skill_score.toFixed(1)}%` : 'N/A'}
              </td>
            </tr>
            <tr>
              <td className="p-3 text-slate-600">Experience Relevance</td>
              <td className="p-3 font-mono">{candidateA.experience_section_score.toFixed(1)}%</td>
              <td className="p-3 font-mono">{candidateB.experience_section_score.toFixed(1)}%</td>
            </tr>
            <tr>
              <td className="p-3 text-slate-600">Lexical Overlap (TF-IDF)</td>
              <td className="p-3 font-mono">{candidateA.lexical_score.toFixed(1)}%</td>
              <td className="p-3 font-mono">{candidateB.lexical_score.toFixed(1)}%</td>
            </tr>
            <tr>
              <td className="p-3 text-slate-600">Matched Skills Count</td>
              <td className="p-3 font-mono font-semibold">{candidateA.matched_skills.length} skills</td>
              <td className="p-3 font-mono font-semibold">{candidateB.matched_skills.length} skills</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Venn-like Skill Overlap */}
      <div>
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-3">
          Skill Overlap Analysis
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          {/* Unique to A */}
          <div className="p-3.5 rounded-xl bg-blue-50/70 border border-blue-200">
            <span className="font-bold text-blue-900 block mb-2">
              Unique to 🅰️ ({onlyA.length}):
            </span>
            <div className="flex flex-wrap gap-1">
              {onlyA.length > 0 ? (
                onlyA.map((s) => (
                  <span key={s} className="px-2 py-0.5 rounded-full bg-white text-blue-800 border border-blue-200 font-medium">
                    {s}
                  </span>
                ))
              ) : (
                <span className="text-slate-400 italic">None</span>
              )}
            </div>
          </div>

          {/* Shared */}
          <div className="p-3.5 rounded-xl bg-emerald-50/70 border border-emerald-200">
            <span className="font-bold text-emerald-900 block mb-2">
              Shared by Both ({sharedSkills.length}):
            </span>
            <div className="flex flex-wrap gap-1">
              {sharedSkills.length > 0 ? (
                sharedSkills.map((s) => (
                  <span key={s} className="px-2 py-0.5 rounded-full bg-white text-emerald-800 border border-emerald-200 font-semibold">
                    {s}
                  </span>
                ))
              ) : (
                <span className="text-slate-400 italic">No common skills</span>
              )}
            </div>
          </div>

          {/* Unique to B */}
          <div className="p-3.5 rounded-xl bg-purple-50/70 border border-purple-200">
            <span className="font-bold text-purple-900 block mb-2">
              Unique to 🅱️ ({onlyB.length}):
            </span>
            <div className="flex flex-wrap gap-1">
              {onlyB.length > 0 ? (
                onlyB.map((s) => (
                  <span key={s} className="px-2 py-0.5 rounded-full bg-white text-purple-800 border border-purple-200 font-medium">
                    {s}
                  </span>
                ))
              ) : (
                <span className="text-slate-400 italic">None</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

