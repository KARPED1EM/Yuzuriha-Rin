// @ts-check

/**
 * Multi-emotion glow renderer:
 * - ignores neutral
 * - intensity controls saturation/lightness/alpha
 * - multiple emotions form a smooth conic gradient (ordered gently)
 * - transitions via cross-fade between 2 layers
 * @param {Record<string, string>} emotionMap
 */
export function applyEmotionTheme(emotionMap) {
  const shell = document.getElementById("wechatShell");
  if (!shell) return;
  if (!emotionMap || typeof emotionMap !== "object") {
    clearEmotionTheme();
    return;
  }

  /** @type {Record<string, {h:number,s:number,l:number}>} */
  const palette = {
    neutral: { h: 0, s: 0, l: 70 }, // ignored
    // High-contrast, easy-to-recognize hues (avoid adjacent hues where possible).
    // Warm
    angry: { h: 4, s: 90, l: 50 }, // deep red
    excited: { h: 22, s: 95, l: 54 }, // vivid orange
    happy: { h: 52, s: 95, l: 58 }, // bright yellow
    // Green / teal
    caring: { h: 145, s: 70, l: 48 }, // green
    playful: { h: 95, s: 85, l: 52 }, // lime-green
    confused: { h: 182, s: 72, l: 46 }, // teal
    surprised: { h: 198, s: 88, l: 56 }, // cyan
    // Blue
    sad: { h: 220, s: 78, l: 54 }, // blue
    serious: { h: 235, s: 58, l: 44 }, // deep navy-blue
    // Purple / pink
    anxious: { h: 275, s: 70, l: 52 }, // purple
    shy: { h: 305, s: 62, l: 60 }, // violet-pink
    embarrassed: { h: 332, s: 86, l: 58 }, // magenta
    affectionate: { h: 350, s: 90, l: 58 }, // rose
    // Low-saturation states
    tired: { h: 210, s: 22, l: 60 }, // desaturated blue-gray
    bored: { h: 40, s: 18, l: 62 }, // warm gray
  };

  /** @type {Record<string, {alpha:number, dl:number, ds:number}>} */
  const intensity = {
    low: { alpha: 0.28, dl: 14, ds: -14 },
    medium: { alpha: 0.5, dl: 7, ds: -6 },
    high: { alpha: 0.74, dl: 0, ds: 0 },
    extreme: { alpha: 0.92, dl: -8, ds: 6 },
  };

  /** @type {{h:number,s:number,l:number,a:number,key:string}[]} */
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
      s: clamp(base.s + iv.ds, 8, 96),
      l: clamp(base.l + iv.dl, 28, 78),
      a: clamp(iv.alpha, 0.25, 1),
    });
  }

  if (colors.length === 0) {
    clearEmotionTheme();
    return;
  }

  const ordered = orderColorsGently(colors);
  const gradient = buildGlowGradient(ordered);
  applyGradientWithTransition(shell, gradient);
}

export function clearEmotionTheme() {
  const shell = document.getElementById("wechatShell");
  if (!shell) return;
  shell.style.setProperty("--glow-opacity-1", "0");
  shell.style.setProperty("--glow-opacity-2", "0");
  shell.classList.remove("glow-enabled");
}

let activeLayer = 1;

/**
 * @param {HTMLElement} shell
 * @param {string} gradient
 */
function applyGradientWithTransition(shell, gradient) {
  const nextLayer = activeLayer === 1 ? 2 : 1;
  shell.style.setProperty(`--glow-gradient-${nextLayer}`, gradient);
  shell.style.setProperty("--glow-opacity-1", nextLayer === 1 ? "1" : "0");
  shell.style.setProperty("--glow-opacity-2", nextLayer === 2 ? "1" : "0");
  shell.classList.add("glow-enabled");
  activeLayer = nextLayer;
}

/**
 * @param {{h:number,s:number,l:number,a:number}[]} colors
 */
function buildGlowGradient(colors) {
  const stops = colors.map((c) => `hsla(${c.h} ${c.s}% ${c.l}% / ${c.a})`);
  if (stops.length === 1) {
    const c = stops[0];
    return `radial-gradient(circle at 50% 50%, ${c} 0%, rgba(0,0,0,0) 70%)`;
  }
  // Conic gradients blend smoothly between consecutive colors.
  return `conic-gradient(from 180deg, ${stops.join(", ")}, ${stops[0]})`;
}

/**
 * Greedy nearest-neighbor ordering by HSL distance.
 * @param {{h:number,s:number,l:number,a:number,key:string}[]} input
 */
function orderColorsGently(input) {
  const remaining = input.slice();
  remaining.sort((a, b) => a.a - b.a);
  const start = remaining.shift();
  if (!start) return [];
  const ordered = [start];

  while (remaining.length > 0) {
    const last = ordered[ordered.length - 1];
    let bestIdx = 0;
    let bestD = Number.POSITIVE_INFINITY;
    for (let i = 0; i < remaining.length; i += 1) {
      const d = colorDistance(last, remaining[i]);
      if (d < bestD) {
        bestD = d;
        bestIdx = i;
      }
    }
    ordered.push(remaining.splice(bestIdx, 1)[0]);
  }
  return ordered;
}

/**
 * @param {{h:number,s:number,l:number}} a
 * @param {{h:number,s:number,l:number}} b
 */
function colorDistance(a, b) {
  const dhRaw = Math.abs(a.h - b.h);
  const dh = Math.min(dhRaw, 360 - dhRaw) / 180;
  const ds = Math.abs(a.s - b.s) / 100;
  const dl = Math.abs(a.l - b.l) / 100;
  return dh * 1.4 + ds * 0.7 + dl * 1.0;
}

function clamp(v, min, max) {
  return Math.max(min, Math.min(max, v));
}
