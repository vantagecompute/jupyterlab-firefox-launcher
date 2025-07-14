const fs = require('fs');
const path = require('path');

// Read the root package.json
const rootPackagePath = path.join(__dirname, 'package.json');
const labextensionDir = path.join(__dirname, 'jupyterlab_firefox_launcher', 'labextension');
const labextensionPackagePath = path.join(labextensionDir, 'package.json');

try {
  // Read root package.json
  const rootPackage = JSON.parse(fs.readFileSync(rootPackagePath, 'utf8'));
  
  // Create a copy for the labextension
  const labextensionPackage = { ...rootPackage };
  
  // Ensure labextension directory exists
  if (!fs.existsSync(labextensionDir)) {
    console.log('📁 Creating labextension directory...');
    fs.mkdirSync(labextensionDir, { recursive: true });
  }
  
  // Add the jupyterlab specific build info if it exists in the labextension
  if (fs.existsSync(labextensionPackagePath)) {
    const existingLabPackage = JSON.parse(fs.readFileSync(labextensionPackagePath, 'utf8'));
    if (existingLabPackage.jupyterlab && existingLabPackage.jupyterlab._build) {
      console.log('🔧 Preserving JupyterLab build metadata...');
      labextensionPackage.jupyterlab = {
        ...labextensionPackage.jupyterlab,
        _build: existingLabPackage.jupyterlab._build
      };
    }
  }
  
  // Write to labextension directory
  fs.writeFileSync(labextensionPackagePath, JSON.stringify(labextensionPackage, null, 2));
  
  console.log(`✅ Successfully copied package.json to labextension directory (v${labextensionPackage.version})`);
} catch (error) {
  console.error('❌ Error copying package.json:', error.message);
  process.exit(1);
}