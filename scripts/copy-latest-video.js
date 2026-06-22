const fs = require('fs');
const path = require('path');

const resultsDir = path.join(__dirname, '../output/playwright/test-results');
const out = path.join(__dirname, '../output/playwright/checkout-flow.webm');

function findLatestWebm(dir) {
  let best = null;
  let bestTime = 0;

  function walk(current) {
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const fullPath = path.join(current, entry.name);
      if (entry.isDirectory()) {
        walk(fullPath);
        continue;
      }
      if (entry.name !== 'video.webm') continue;
      const mtime = fs.statSync(fullPath).mtimeMs;
      if (mtime > bestTime) {
        bestTime = mtime;
        best = fullPath;
      }
    }
  }

  if (fs.existsSync(dir)) walk(dir);
  return best;
}

const src = findLatestWebm(resultsDir);
if (!src) {
  console.error(`No video.webm found under ${resultsDir}`);
  process.exit(1);
}

fs.mkdirSync(path.dirname(out), { recursive: true });
fs.copyFileSync(src, out);
console.log(`Copied ${src} -> ${out}`);
