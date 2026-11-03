import React, { useState, useEffect, useMemo } from 'react';
import {
  Trophy,
  Filter,
  Search,
  ArrowRightLeft,
  FileSpreadsheet,
  FileCode,
  AlertCircle,
} from 'lucide-react';

import Navbar from './components/Navbar';
import UploadSection from './components/UploadSection';
import KPICards from './components/KPICards';
import CandidateCard from './components/CandidateCard';
import WeightsSliders from './components/WeightsSliders';
import DeepDiveModal from './components/DeepDiveModal';
import HeadToHead from './components/HeadToHead';
import { DEFAULT_WEIGHTS, reorderCandidates } from './utils/scoring';

export default function App() {
  const [backendStatus, setBackendStatus] = useState('connecting');
  const [jdText, setJdText] = useState('');
  const [jdFile, setJdFile] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [weights, setWeights] = useState(DEFAULT_WEIGHTS);

  const [rawResults, setRawResults] = useState([]);
  const [jdSkills, setJdSkills] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Filters & View State
  const [activeTab, setActiveTab] = useState('leaderboard'); // 'leaderboard' | 'headtohead'
  const [minScoreFilter, setMinScoreFilter] = useState(0);
  const [selectedSkillsFilter, setSelectedSkillsFilter] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  // Modals & Selection
  const [inspectCandidate, setInspectCandidate] = useState(null);
  const [compareList, setCompareList] = useState([]);

  // 1. Initial Health Check
  useEffect(() => {
    fetch('/api/health')
      .then((res) => {
        if (!res.ok) throw new Error('Health check failed');
        return res.json();
      })
      .then(() => setBackendStatus('healthy'))
      .catch(() => setBackendStatus('error'));
  }, []);

  // 2. Perform Ranking via Backend API
  const handleRank = async () => {
    setIsLoading(true);
    setErrorMsg(null);

    try {
      const formData = new FormData();
      if (jdFile) {
        formData.append('jd_file', jdFile);
      } else {
        formData.append('jd_text', jdText);
      }

      resumes.forEach((f) => {
        formData.append('resumes', f);
      });

      formData.append('weights', JSON.stringify(weights));

      const response = await fetch('/api/rank', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to rank resumes.');
      }

      const data = await response.json();
      setRawResults(data.results || []);
      setJdSkills(data.jd_skills || []);

      if (data.results && data.results.length >= 2) {
        setCompareList([data.results[0], data.results[1]]);
      } else if (data.results && data.results.length === 1) {
        setCompareList([data.results[0]]);
      }
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message || 'An error occurred during ranking.');
    } finally {
      setIsLoading(false);
    }
  };

  // 3. Instant Client-Side Recalculation on Weight or Filter Changes
  const rankedResults = useMemo(() => {
    if (!rawResults || rawResults.length === 0) return [];
    return reorderCandidates(rawResults, weights);
  }, [rawResults, weights]);

  // 4. Apply Filters (Score threshold, Selected Skills, Search Query)
  const filteredResults = useMemo(() => {
    return rankedResults.filter((candidate) => {
      if (candidate.final_score < minScoreFilter) return false;

      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        if (!candidate.filename.toLowerCase().includes(q)) return false;
      }

      if (selectedSkillsFilter.length > 0) {
        const candidateSkillSet = new Set(
          (candidate.matched_skills || []).map((s) => s.toLowerCase())
        );
        const hasAll = selectedSkillsFilter.every((req) =>
          candidateSkillSet.has(req.toLowerCase())
        );
        if (!hasAll) return false;
      }

      return true;
    });
  }, [rankedResults, minScoreFilter, searchQuery, selectedSkillsFilter]);

  // Candidate comparison selection toggle
  const handleSelectForCompare = (candidate) => {
    setCompareList((prev) => {
      const exists = prev.some((c) => c.filename === candidate.filename);
      if (exists) {
        return prev.filter((c) => c.filename !== candidate.filename);
      }
      if (prev.length >= 2) {
        return [prev[1], candidate];
      }
      return [...prev, candidate];
    });
  };

  // Export handlers
  const handleExport = async (format) => {
    try {
      const response = await fetch(`/api/export/${format}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ results: rankedResults }),
      });

      if (!response.ok) throw new Error(`Export ${format} failed`);

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `resume_rankings.${format}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert(`Export failed: ${err.message}`);
    }
  };

  // Detected skills across all current cohort candidates
  const cohortSkills = useMemo(() => {
    const set = new Set();
    rawResults.forEach((r) => {
      (r.matched_skills || []).forEach((s) => set.add(s));
    });
    return Array.from(set).sort();
  }, [rawResults]);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <Navbar backendStatus={backendStatus} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Banner */}
        {errorMsg && (
          <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-900 flex items-start space-x-3 text-xs shadow-2xs">
            <AlertCircle className="h-5 w-5 text-rose-500 shrink-0 mt-0.5" />
            <div>
              <strong className="font-bold">Evaluation Error:</strong> {errorMsg}
            </div>
          </div>
        )}

        {/* 1. Upload & Setup Section */}
        <UploadSection
          jdText={jdText}
          setJdText={setJdText}
          jdFile={jdFile}
          setJdFile={setJdFile}
          resumes={resumes}
          setResumes={setResumes}
          onRank={handleRank}
          isLoading={isLoading}
          jdSkills={jdSkills}
        />

        {/* Results Container */}
        {rankedResults.length > 0 && (
          <div className="space-y-6">
            {/* KPI Summary Row */}
            <KPICards results={rankedResults} />

            {/* Weights Sliders (Decoupled real-time recalculation) */}
            <WeightsSliders weights={weights} setWeights={setWeights} />

            {/* Navigation & Controls Bar */}
            <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
              {/* Tabs */}
              <div className="flex items-center space-x-2">
                <button
                  type="button"
                  onClick={() => setActiveTab('leaderboard')}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition cursor-pointer ${
                    activeTab === 'leaderboard'
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  <Trophy className="h-4 w-4" />
                  <span>Leaderboard ({filteredResults.length})</span>
                </button>

                <button
                  type="button"
                  onClick={() => setActiveTab('headtohead')}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition cursor-pointer ${
                    activeTab === 'headtohead'
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  <ArrowRightLeft className="h-4 w-4" />
                  <span>Head-to-Head Compare</span>
                  {compareList.length > 0 && (
                    <span className="ml-1 text-[10px] px-1.5 py-0.2 rounded-full bg-indigo-200 text-indigo-900">
                      {compareList.length}
                    </span>
                  )}
                </button>
              </div>

              {/* Exports */}
              <div className="flex items-center space-x-2">
                <button
                  type="button"
                  onClick={() => handleExport('csv')}
                  className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-200 hover:border-slate-300 text-slate-700 bg-white hover:bg-slate-50 text-xs font-semibold transition cursor-pointer shadow-2xs"
                >
                  <FileSpreadsheet className="h-3.5 w-3.5 text-emerald-600" />
                  <span>Export CSV</span>
                </button>

                <button
                  type="button"
                  onClick={() => handleExport('json')}
                  className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-200 hover:border-slate-300 text-slate-700 bg-white hover:bg-slate-50 text-xs font-semibold transition cursor-pointer shadow-2xs"
                >
                  <FileCode className="h-3.5 w-3.5 text-indigo-600" />
                  <span>Export JSON</span>
                </button>
              </div>
            </div>

            {/* TAB CONTENT */}
            {activeTab === 'leaderboard' && (
              <div className="space-y-4">
                {/* Search & Interactive Filter Bar */}
                <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm grid grid-cols-1 md:grid-cols-12 gap-4">
                  {/* Search */}
                  <div className="md:col-span-4 relative">
                    <Search className="h-4 w-4 text-slate-400 absolute left-3 top-3" />
                    <input
                      type="text"
                      placeholder="Search candidate by filename..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                    />
                  </div>

                  {/* Score Filter */}
                  <div className="md:col-span-4 flex items-center space-x-3 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200/60">
                    <span className="text-xs font-semibold text-slate-600 shrink-0">
                      Min Score: <strong className="text-indigo-600 font-mono">{minScoreFilter}</strong>
                    </span>
                    <input
                      type="range"
                      min="0"
                      max="90"
                      step="5"
                      value={minScoreFilter}
                      onChange={(e) => setMinScoreFilter(Number(e.target.value))}
                      className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                    />
                  </div>

                  {/* Skill Filter Dropdown */}
                  <div className="md:col-span-4 flex items-center space-x-2">
                    <Filter className="h-4 w-4 text-slate-400 shrink-0" />
                    <select
                      value=""
                      onChange={(e) => {
                        const val = e.target.value;
                        if (val && !selectedSkillsFilter.includes(val)) {
                          setSelectedSkillsFilter([...selectedSkillsFilter, val]);
                        }
                      }}
                      className="w-full text-xs p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                    >
                      <option value="">Filter by Skill (e.g. Python, Docker)...</option>
                      {cohortSkills.map((s) => (
                        <option key={s} value={s}>
                          {s}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Active Skill Pills Filter */}
                  {selectedSkillsFilter.length > 0 && (
                    <div className="md:col-span-12 flex items-center gap-1.5 flex-wrap pt-1">
                      <span className="text-[11px] font-semibold text-slate-500">Active Skill Filters:</span>
                      {selectedSkillsFilter.map((skill) => (
                        <span
                          key={skill}
                          className="inline-flex items-center space-x-1 text-xs px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200"
                        >
                          <span>{skill}</span>
                          <button
                            type="button"
                            onClick={() =>
                              setSelectedSkillsFilter(selectedSkillsFilter.filter((s) => s !== skill))
                            }
                            className="hover:text-rose-600 cursor-pointer text-indigo-400 font-bold ml-1"
                          >
                            ×
                          </button>
                        </span>
                      ))}
                      <button
                        type="button"
                        onClick={() => setSelectedSkillsFilter([])}
                        className="text-[11px] text-rose-500 hover:underline font-semibold ml-2 cursor-pointer"
                      >
                        Clear All
                      </button>
                    </div>
                  )}
                </div>

                {/* Candidate Cards Grid */}
                {filteredResults.length === 0 ? (
                  <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
                    <p className="text-sm font-semibold text-slate-700">No candidates match the selected filters.</p>
                    <p className="text-xs text-slate-400 mt-1">Try lowering the minimum score or clearing skill filters.</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                    {filteredResults.map((candidate) => (
                      <CandidateCard
                        key={candidate.filename}
                        candidate={candidate}
                        onInspect={(c) => setInspectCandidate(c)}
                        onSelectForCompare={handleSelectForCompare}
                        isSelectedForCompare={compareList.some((c) => c.filename === candidate.filename)}
                      />
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* TAB: HEAD-TO-HEAD COMPARE */}
            {activeTab === 'headtohead' && (
              <HeadToHead results={rankedResults} initialCandidates={compareList} />
            )}
          </div>
        )}
      </main>

      {/* Candidate Deep Dive Modal */}
      {inspectCandidate && (
        <DeepDiveModal candidate={inspectCandidate} onClose={() => setInspectCandidate(null)} />
      )}
    </div>
  );
}
