import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, Sparkles, X, Trash2 } from 'lucide-react';
import { SAMPLE_JD, SAMPLE_RESUMES } from '../sampleData';

export default function UploadSection({
  jdText,
  setJdText,
  jdFile,
  setJdFile,
  resumes,
  setResumes,
  onRank,
  isLoading,
  jdSkills,
}) {
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);
  const jdFileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      addFiles(Array.from(e.dataTransfer.files));
    }
  };

  const addFiles = (newFiles) => {
    const validExtensions = ['.pdf', '.docx', '.txt'];
    const filtered = newFiles.filter((f) =>
      validExtensions.some((ext) => f.name.toLowerCase().endsWith(ext))
    );
    setResumes((prev) => {
      const existingNames = new Set(prev.map((f) => f.name));
      const deduplicated = filtered.filter((f) => !existingNames.has(f.name));
      return [...prev, ...deduplicated];
    });
  };

  const removeResume = (index) => {
    setResumes((prev) => prev.filter((_, i) => i !== index));
  };

  const loadSampleData = () => {
    setJdText(SAMPLE_JD);
    setJdFile(null);

    // Create File objects for sample resumes
    const sampleFiles = SAMPLE_RESUMES.map((item) => {
      const blob = new Blob([item.content], { type: 'text/plain' });
      return new File([blob], item.name, { type: 'text/plain' });
    });
    setResumes(sampleFiles);
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 mb-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-100">
        <div>
          <h2 className="text-lg font-bold text-slate-900">1. Setup Evaluation Data</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Provide a Target Job Description and upload candidate resumes for in-memory NLP scoring.
          </p>
        </div>

        <button
          type="button"
          onClick={loadSampleData}
          className="inline-flex items-center space-x-2 px-3.5 py-2 text-xs font-semibold rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200/80 transition cursor-pointer shadow-2xs"
        >
          <Sparkles className="h-3.5 w-3.5 text-indigo-600" />
          <span>Load 1-Click Benchmark (JD + 3 Resumes)</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Job Description */}
        <div className="lg:col-span-6 flex flex-col">
          <div className="flex items-center justify-between mb-2">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center space-x-1.5">
              <span>Target Job Description</span>
              <span className="text-rose-500">*</span>
            </label>
            <span className="text-[11px] text-slate-400">
              {jdText ? `${jdText.split(/\s+/).filter(Boolean).length} words` : jdFile ? jdFile.name : 'Required'}
            </span>
          </div>

          <div className="flex-1 flex flex-col relative">
            <textarea
              rows={8}
              value={jdText}
              onChange={(e) => {
                setJdText(e.target.value);
                if (jdFile) setJdFile(null);
              }}
              placeholder="Paste job description requirements, responsibilities, and qualifications here..."
              className="w-full flex-1 p-3.5 text-xs text-slate-800 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-sans leading-relaxed resize-none"
            />

            <div className="mt-2 flex items-center justify-between">
              <span className="text-[11px] text-slate-400">Or upload document:</span>
              <input
                type="file"
                ref={jdFileInputRef}
                accept=".pdf,.docx,.txt"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setJdFile(e.target.files[0]);
                    setJdText('');
                  }
                }}
                className="hidden"
              />
              <button
                type="button"
                onClick={() => jdFileInputRef.current?.click()}
                className="text-xs text-indigo-600 hover:text-indigo-800 font-medium underline cursor-pointer"
              >
                {jdFile ? `Replace: ${jdFile.name}` : 'Upload JD (.pdf / .docx)'}
              </button>
            </div>
          </div>

          {/* Detected JD Skills Pill tags if available */}
          {jdSkills && jdSkills.length > 0 && (
            <div className="mt-3 p-2.5 bg-indigo-50/50 rounded-lg border border-indigo-100">
              <span className="text-[11px] font-semibold text-indigo-900 block mb-1.5">
                🎯 Extracted JD Skills ({jdSkills.length}):
              </span>
              <div className="flex flex-wrap gap-1 max-h-20 overflow-y-auto">
                {jdSkills.map((skill) => (
                  <span
                    key={skill}
                    className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-white text-indigo-700 border border-indigo-200 shadow-2xs"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Resumes Dropzone */}
        <div className="lg:col-span-6 flex flex-col">
          <div className="flex items-center justify-between mb-2">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center space-x-1.5">
              <span>Candidate Resumes</span>
              <span className="text-rose-500">*</span>
            </label>
            <span className="text-[11px] text-slate-400">
              {resumes.length} file{resumes.length === 1 ? '' : 's'} added
            </span>
          </div>

          {/* Dropzone */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition flex-1 flex flex-col items-center justify-center min-h-[160px] ${
              dragActive
                ? 'border-indigo-500 bg-indigo-50/50 scale-[0.99]'
                : 'border-slate-300 hover:border-indigo-400 bg-slate-50/50'
            }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              multiple
              accept=".pdf,.docx,.txt"
              onChange={(e) => {
                if (e.target.files) addFiles(Array.from(e.target.files));
              }}
              className="hidden"
            />
            <div className="h-10 w-10 rounded-full bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 mb-2 shadow-2xs">
              <UploadCloud className="h-5 w-5" />
            </div>
            <p className="text-xs font-semibold text-slate-700">
              Drag & Drop Resumes Here, or <span className="text-indigo-600 underline">Browse</span>
            </p>
            <p className="text-[11px] text-slate-400 mt-1">Supports PDF, DOCX, and TXT (Multiple files allowed)</p>
          </div>

          {/* File Chips */}
          {resumes.length > 0 && (
            <div className="mt-3">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[11px] font-semibold text-slate-600">Selected Documents:</span>
                <button
                  type="button"
                  onClick={() => setResumes([])}
                  className="text-[11px] text-rose-500 hover:text-rose-700 flex items-center space-x-1 cursor-pointer"
                >
                  <Trash2 className="h-3 w-3" />
                  <span>Clear All</span>
                </button>
              </div>
              <div className="max-h-28 overflow-y-auto space-y-1.5 pr-1">
                {resumes.map((file, idx) => (
                  <div
                    key={`${file.name}-${idx}`}
                    className="flex items-center justify-between px-3 py-1.5 rounded-lg bg-slate-100/80 border border-slate-200 text-xs"
                  >
                    <div className="flex items-center space-x-2 truncate mr-2">
                      <FileText className="h-3.5 w-3.5 text-indigo-500 shrink-0" />
                      <span className="truncate text-slate-700 font-medium">{file.name}</span>
                      <span className="text-[10px] text-slate-400 shrink-0">
                        ({(file.size / 1024).toFixed(0)} KB)
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        removeResume(idx);
                      }}
                      className="text-slate-400 hover:text-rose-500 transition cursor-pointer p-0.5"
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Action Button */}
      <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-end">
        <button
          type="button"
          onClick={onRank}
          disabled={isLoading || (!jdText && !jdFile) || resumes.length === 0}
          className={`inline-flex items-center space-x-2 px-6 py-2.5 rounded-xl font-bold text-sm text-white shadow-md transition cursor-pointer ${
            isLoading || (!jdText && !jdFile) || resumes.length === 0
              ? 'bg-slate-400 cursor-not-allowed opacity-60'
              : 'bg-indigo-600 hover:bg-indigo-700 active:scale-98 shadow-indigo-200'
          }`}
        >
          {isLoading ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              <span>Computing Embeddings & Rankings...</span>
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4" />
              <span>Rank Candidates ({resumes.length})</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}

