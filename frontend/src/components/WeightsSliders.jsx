import React from 'react';
import { Sliders, RefreshCw } from 'lucide-react';
import { DEFAULT_WEIGHTS } from '../utils/scoring';

export default function WeightsSliders({ weights, setWeights }) {
  const handleChange = (key, value) => {
    setWeights((prev) => ({
      ...prev,
      [key]: parseFloat(value),
    }));
  };

  const handleReset = () => {
    setWeights(DEFAULT_WEIGHTS);
  };

  const total = (
    weights.semantic_score +
    weights.skill_score +
    weights.experience_section_score +
    weights.lexical_score
  ).toFixed(2);

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
        <div className="flex items-center space-x-2">
          <Sliders className="h-4 w-4 text-indigo-600" />
          <h3 className="text-sm font-bold text-slate-800">Scoring Factor Weights</h3>
          <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-600 font-semibold border border-indigo-100">
            Real-Time Recalculation
          </span>
        </div>
        <div className="flex items-center space-x-3">
          <span className={`text-xs font-mono font-medium ${parseFloat(total) === 1.0 ? 'text-emerald-600' : 'text-amber-600'}`}>
            Total Sum: {total}
          </span>
          <button
            type="button"
            onClick={handleReset}
            className="flex items-center space-x-1 text-xs text-slate-500 hover:text-indigo-600 font-medium transition cursor-pointer"
          >
            <RefreshCw className="h-3 w-3" />
            <span>Reset</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Semantic Score */}
        <div className="bg-slate-50/80 p-3 rounded-lg border border-slate-200/60">
          <div className="flex justify-between items-center text-xs mb-1">
            <span className="font-semibold text-slate-700">Semantic Embedding</span>
            <span className="font-mono font-bold text-indigo-600">{Math.round(weights.semantic_score * 100)}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={weights.semantic_score}
            onChange={(e) => handleChange('semantic_score', e.target.value)}
            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
          />
          <p className="text-[10px] text-slate-400 mt-1">all-MiniLM-L6-v2 deep sentence vectors</p>
        </div>

        {/* Skill Score */}
        <div className="bg-slate-50/80 p-3 rounded-lg border border-slate-200/60">
          <div className="flex justify-between items-center text-xs mb-1">
            <span className="font-semibold text-slate-700">Taxonomy Skill Match</span>
            <span className="font-mono font-bold text-emerald-600">{Math.round(weights.skill_score * 100)}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={weights.skill_score}
            onChange={(e) => handleChange('skill_score', e.target.value)}
            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-emerald-600"
          />
          <p className="text-[10px] text-slate-400 mt-1">spaCy PhraseMatcher with token boundary</p>
        </div>

        {/* Experience Section Score */}
        <div className="bg-slate-50/80 p-3 rounded-lg border border-slate-200/60">
          <div className="flex justify-between items-center text-xs mb-1">
            <span className="font-semibold text-slate-700">Experience Relevance</span>
            <span className="font-mono font-bold text-amber-600">{Math.round(weights.experience_section_score * 100)}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={weights.experience_section_score}
            onChange={(e) => handleChange('experience_section_score', e.target.value)}
            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-amber-600"
          />
          <p className="text-[10px] text-slate-400 mt-1">Targeted section alignment vs JD</p>
        </div>

        {/* Lexical Score */}
        <div className="bg-slate-50/80 p-3 rounded-lg border border-slate-200/60">
          <div className="flex justify-between items-center text-xs mb-1">
            <span className="font-semibold text-slate-700">Lexical TF-IDF</span>
            <span className="font-mono font-bold text-cyan-600">{Math.round(weights.lexical_score * 100)}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={weights.lexical_score}
            onChange={(e) => handleChange('lexical_score', e.target.value)}
            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-cyan-600"
          />
          <p className="text-[10px] text-slate-400 mt-1">Unigram & bigram vocabulary overlap</p>
        </div>
      </div>
    </div>
  );
}

