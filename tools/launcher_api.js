const { exec } = require('child_process');
const path = require('path');
const os = require('os');
const fs = require('fs');

const CHROME_PATH =
  process.env.CHROME_PATH ||
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

const USERDATA =
  process.env.USERDATA ||
  path.join(os.homedir(), 'AppData', 'Local', 'Google', 'Chrome', 'User Data');

const START_PORT = 9222;

// 🔥 SAME FUNCTION (UNCHANGED)
function parseSelection(input) {
  input = input.toLowerCase();

  if (input.startsWith('only')) {
    const n = parseInt(input.replace('only', '').trim(), 10);
    return isNaN(n) ? [] : [n - 1];
  }

  if (/^\d+$/.test(input)) {
    const n = parseInt(input, 10);
    return Array.from({ length: n }, (_, i) => i);
  }

  const result = new Set();
  const parts = input.split(',');

  for (const part of parts) {
    if (part.includes('-')) {
      const [a, b] = part.split('-').map(x => parseInt(x.trim(), 10));
      if (!isNaN(a) && !isNaN(b) && a <= b) {
        for (let i = a; i <= b; i++) result.add(i - 1);
      }
    } else {
      const n = parseInt(part.trim(), 10);
      if (!isNaN(n)) result.add(n - 1);
    }
  }

  return [...result].sort((a, b) => a - b);
}

// 🔥 MAIN FUNCTION (FIXED PORT LOGIC)
async function run(input) {

  const indexes = parseSelection(input);
  if (!indexes.length) {
    console.log("Invalid input");
    return;
  }

  const maxIndex = Math.max(...indexes) + 1;

  const cfgPath = path.join(__dirname, 'profiles_config.json');
  let profiles = [];

  if (fs.existsSync(cfgPath)) {
    try { profiles = JSON.parse(fs.readFileSync(cfgPath, 'utf8')); } catch { }
  }

  for (let i = profiles.length; i < maxIndex; i++) {
    profiles.push(`Profile ${i + 1}`);
  }

  fs.writeFileSync(cfgPath, JSON.stringify(profiles, null, 2), 'utf8');

  const FLAGS = `
    --disable-gpu
    --disable-software-rasterizer
    --disable-background-networking
    --disable-sync
    --no-first-run
    --no-default-browser-check
    --metrics-recording-only
    --disable-hang-monitor
    --disable-client-side-phishing-detection
    --disk-cache-size=52428800
    --media-cache-size=52428800
  `.replace(/\s+/g, ' ').trim();

  // 🔥 IMPORTANT FIX: PORT = PROFILE BASED (NOT INCREMENT)
  for (const i of indexes) {

    const prof = profiles[i];
    const profPath = path.join(USERDATA, prof);

    try { fs.mkdirSync(profPath, { recursive: true }); } catch { }

    // ✅ FIXED PORT (NEVER CHANGES)
    const port = START_PORT + i;

    const cmd =
      `"${CHROME_PATH}" ${FLAGS} ` +
      `--remote-debugging-port=${port} ` +
      `--remote-allow-origins=* ` +
      `--user-data-dir="${profPath}" ` +
      `--new-window`;

    console.log(`Launching ${prof} on port ${port}`);

    exec(cmd);

    await new Promise(r => setTimeout(r, 1200));
  }
}

// 🔥 CLI ARG support
const input = process.argv[2];
if (input) {
  run(input);
}