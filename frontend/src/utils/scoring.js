/**
 * Client-side score recalculator matching Python src/scorer.py logic.
 * Enables zero-latency instant updates when sliders are moved.
 */

export const DEFAULT_WEIGHTS = {
  semantic_score: 0.35,
  skill_score: 0.40,
  experience_section_score: 0.15,
  lexical_score: 0.10,
};

export function calculateCandidateScore(candidate, weights) {
  let weightedSum = 0;
  let totalWeight = 0;

  // Semantic
  const wSem = weights.semantic_score ?? DEFAULT_WEIGHTS.semantic_score;
  weightedSum += wSem * candidate.semantic_score;
  totalWeight += wSem;

  // Skill Match (renormalize if not applicable)
  if (candidate.skill_score !== null && candidate.skill_score !== undefined) {
    const wSkill = weights.skill_score ?? DEFAULT_WEIGHTS.skill_score;
    weightedSum += wSkill * candidate.skill_score;
    totalWeight += wSkill;
  }

  // Experience Relevance
  const wExp = weights.experience_section_score ?? DEFAULT_WEIGHTS.experience_section_score;
  weightedSum += wExp * candidate.experience_section_score;
  totalWeight += wExp;

  // Lexical Overlap
  const wLex = weights.lexical_score ?? DEFAULT_WEIGHTS.lexical_score;
  weightedSum += wLex * candidate.lexical_score;
  totalWeight += wLex;

  if (totalWeight <= 0) return 0;
  const rawScore = weightedSum / totalWeight;
  return Number(Math.min(100, Math.max(0, rawScore)).toFixed(2));
}

export function reorderCandidates(candidates, weights) {
  const updated = candidates.map((c) => ({
    ...c,
    final_score: calculateCandidateScore(c, weights),
  }));

  updated.sort((a, b) => b.final_score - a.final_score);

  return updated.map((c, idx) => ({
    ...c,
    rank: idx + 1,
  }));
}

export function getTier(score) {
  if (score >= 80) {
    return {
      label: "Elite Fit",
      color: "bg-emerald-100 text-emerald-800 border-emerald-300",
      badgeColor: "emerald",
      icon: "🌟",
    };
  }
  if (score >= 65) {
    return {
      label: "Strong Fit",
      color: "bg-blue-100 text-blue-800 border-blue-300",
      badgeColor: "blue",
      icon: "✨",
    };
  }
  if (score >= 50) {
    return {
      label: "Moderate Fit",
      color: "bg-amber-100 text-amber-800 border-amber-300",
      badgeColor: "amber",
      icon: "⚡",
    };
  }
  return {
    label: "Low Fit",
    color: "bg-rose-100 text-rose-800 border-rose-300",
    badgeColor: "rose",
    icon: "🔻",
  };
}

