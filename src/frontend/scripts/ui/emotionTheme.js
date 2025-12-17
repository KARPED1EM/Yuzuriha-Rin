// @ts-check

/** Multi-emotion glow renderer */
export function applyEmotionTheme(emotionMap) {
  const container = document.querySelector(".app-container");
  if (!container) return;
  if (!emotionMap || typeof emotionMap !== "object") {
    clearEmotionTheme();
    return;
  }

  /** Base HSL palette */
  const palette = {
    neutral: { h: 0, s: 0, l: 70 },

    angry: { h: 4, s: 90, l: 50 },
    excited: { h: 22, s: 95, l: 54 },
    happy: { h: 52, s: 95, l: 58 },

    caring: { h: 145, s: 70, l: 48 },
    playful: { h: 95, s: 85, l: 52 },
    confused: { h: 182, s: 72, l: 46 },
    surprised: { h: 198, s: 88, l: 56 },

    sad: { h: 220, s: 78, l: 54 },
    serious: { h: 235, s: 58, l: 44 },

    anxious: { h: 275, s: 70, l: 52 },
    shy: { h: 305, s: 62, l: 60 },
    embarrassed: { h: 332, s: 86, l: 58 },
    affectionate: { h: 350, s: 90, l: 58 },

    tired: { h: 210, s: 22, l: 60 },
    bored: { h: 40, s: 18, l: 62 },
  };

  /** Intensity tuning */
  const intensity = {
    low:     { alpha: 0.10, dl: 20, ds: -46 },
    medium:  { alpha: 0.20, dl: 14, ds: -32 },
    high:    { alpha: 0.35, dl: 8,  ds: -16 },
    extreme: { alpha: 0.50, dl: -4, ds: 0 },
  };

  const colors = [];
  for (const [rawKey, rawVal] of Object.entries(emotionMap)) {
    const key = String(rawKey || "").toLowerCase();
    if (!key || key === "neutral") continue;
    const base = palette[key];
    if (!base) continue;
    const iv = intensity[String(rawVal || "").toLowerCase()] || intensity.medium;

    colors.push({
      key,
      h: base.h,
      s: clamp(base.s + iv.ds, 4, 92),
      l: clamp(base.l + iv.dl, 30, 84),
      a: clamp(iv.alpha, 0.06, 1),
    });
  }

  if (colors.length === 0) {
    clearEmotionTheme();
    return;
  }

  const ordered = orderColorsGently(colors);
  const gradient = buildGlowGradient(ordered);
  applyGradientWithTransition(container, gradient);
}

export function clearEmotionTheme() {
  const container = document.querySelector(".app-container");
  if (!container) return;
  container.style.setProperty("--emotion-opacity-1", "0");
  container.style.setProperty("--emotion-opacity-2", "0");
  container.classList.remove("emotion-enabled");
}

let activeLayer = 1;

/** Cross-fade layers */
function applyGradientWithTransition(container, gradient) {
  const nextLayer = activeLayer === 1 ? 2 : 1;
  container.style.setProperty(`--emotion-gradient-${nextLayer}`, gradient);
  container.style.setProperty("--emotion-opacity-1", nextLayer === 1 ? "1" : "0");
  container.style.setProperty("--emotion-opacity-2", nextLayer === 2 ? "1" : "0");
  container.classList.add("emotion-enabled");
  activeLayer = nextLayer;
}

/** Build gradient for full-page background with smooth color blending */
function buildGlowGradient(colors) {
  const stops = colors.map(
    (c) => `hsla(${c.h} ${c.s}% ${c.l}% / ${c.a})`
  );

  if (stops.length === 1) {
    const c = stops[0];
    // Single color: use radial gradient from center with elliptical shape
    return `radial-gradient(ellipse at 50% 50%, ${c} 0%, transparent 70%)`;
  }

  // Horizontal gradient (left to right) for all multi-color cases
  // Background element is 300% size, viewport is center 1/3 (33.33% - 66.67%)
  // Add padding on both ends to ensure coverage during rotation
  const viewportStart = 25;  // Start before viewport center
  const viewportEnd = 75;    // End after viewport center
  const range = viewportEnd - viewportStart;

  const gradientStops = colors.map((_, i) => {
    const pos = viewportStart + (i * range) / (colors.length - 1);
    return `${stops[i]} ${pos}%`;
  });

  // Extend gradient to edges for full coverage
  const firstColor = stops[0];
  const lastColor = stops[stops.length - 1];

  // Use linear gradient with extended edges
  return `linear-gradient(to right, ${firstColor} 0%, ${gradientStops.join(", ")}, ${lastColor} 100%)`;
}

/** Gentle hue ordering - improved for smoother transitions */
function orderColorsGently(input) {
  if (input.length <= 1) return input;

  const remaining = input.slice();

  // Find the color with the most extreme hue (best starting point for circular arrangement)
  let startIdx = 0;
  for (let i = 1; i < remaining.length; i++) {
    if (remaining[i].h < remaining[startIdx].h) {
      startIdx = i;
    }
  }

  const start = remaining.splice(startIdx, 1)[0];
  const ordered = [start];

  // Greedy nearest-neighbor algorithm for smooth transitions
  while (remaining.length) {
    const last = ordered[ordered.length - 1];
    let bestIdx = 0;
    let bestD = Infinity;

    for (let i = 0; i < remaining.length; i++) {
      const d = colorDistance(last, remaining[i]);
      if (d < bestD) {
        bestD = d;
        bestIdx = i;
      }
    }
    ordered.push(remaining.splice(bestIdx, 1)[0]);
  }

  // Try to optimize by checking if reversing improves the loop closure
  const firstToLast = colorDistance(ordered[0], ordered[ordered.length - 1]);
  ordered.reverse();
  const reversedFirstToLast = colorDistance(ordered[0], ordered[ordered.length - 1]);

  if (reversedFirstToLast > firstToLast) {
    ordered.reverse(); // Revert if original was better
  }

  return ordered;
}

/** HSL distance - improved weights for more natural transitions */
function colorDistance(a, b) {
  // Calculate hue distance considering circular nature (0° = 360°)
  const dhRaw = Math.abs(a.h - b.h);
  const dh = Math.min(dhRaw, 360 - dhRaw) / 180;

  // Saturation and lightness differences
  const ds = Math.abs(a.s - b.s) / 100;
  const dl = Math.abs(a.l - b.l) / 100;

  // Alpha difference (less important)
  const da = Math.abs(a.a - b.a);

  // Weighted combination - prioritize hue for color wheel harmony
  // Higher hue weight ensures colors flow naturally around the color wheel
  return dh * 2.0 + ds * 0.5 + dl * 0.8 + da * 0.3;
}

function clamp(v, min, max) {
  return Math.max(min, Math.min(max, v));
}
