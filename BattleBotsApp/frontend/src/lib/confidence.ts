/** Format confidence as a precise percentage (not rounded to 5s). */
export function formatConfidence(confidence: number): string {
  const pct = confidence * 100;
  if (pct >= 10) return `${pct.toFixed(1)}%`;
  return `${pct.toFixed(2)}%`;
}

export function confidenceTone(confidence: number): string {
  const pct = confidence * 100;
  if (pct >= 70) return "text-winner";
  if (pct >= 50) return "text-spark-400";
  return "text-loser";
}
