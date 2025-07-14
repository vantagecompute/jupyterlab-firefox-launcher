// Script to copy package.json to the labextension folder (CommonJS for Node.js)
const fs = require('fs');
const path = require('path');

const src = path.join(__dirname, 'package.json');
const destDir = path.join(__dirname, 'jupyterlab_firefox_launcher', 'labextension');
const dest = path.join(destDir, 'package.json');

if (!fs.existsSync(destDir)) {
  fs.mkdirSync(destDir, { recursive: true });
}

fs.copyFileSync(src, dest);
console.log(`Copied package.json to ${dest}`);
