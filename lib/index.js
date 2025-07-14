import { ILauncher } from '@jupyterlab/launcher';
import { ICommandPalette, MainAreaWidget } from '@jupyterlab/apputils';
import { requestAPI } from './handler.js';
import { Widget } from '@lumino/widgets';
const buildFirefoxHTML = (iframeId, url, status = '') => {
    // If there's an error or the URL is blank, show a status page
    if (url === 'about:blank' || status.includes('error')) {
        return `
      <div style="display:flex; flex-direction:column; height:100%; background:#f8f9fa;">
        <div style="padding:20px; text-align:center;">
          <h2 style="color:#dc3545;">🔧 Firefox Launcher Status</h2>
          <div style="background:white; border-radius:8px; padding:20px; margin:20px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
            <p><strong>Current Status:</strong> ${status || 'Attempting to connect to VNC service...'}</p>
            <p><strong>URL:</strong> ${url}</p>
            <div style="margin-top:20px;">
              <button onclick="window.location.reload()" style="padding:10px 20px; background:#007bff; color:white; border:none; border-radius:4px; cursor:pointer;">
                🔄 Retry Connection
              </button>
            </div>
          </div>
          <div style="text-align:left; background:#f8f9fa; padding:15px; border-radius:5px; margin:20px;">
            <h4>Troubleshooting:</h4>
            <ul style="margin:10px 0;">
              <li>Check that the Firefox launcher backend is running</li>
              <li>Verify VNC services are active on the server</li>
              <li>Ensure proper network connectivity to VNC ports</li>
              <li>Try refreshing this tab after a few seconds</li>
            </ul>
          </div>
        </div>
      </div>`;
    }
    // Normal Firefox interface with working URL
    return `
    <div style="display:flex; flex-direction:column; height:100%;">
      <!-- URL Navigation Bar -->
      <div style="display:flex; align-items:center; padding:8px; gap:8px; background:#f8f9fa; border-bottom:1px solid #dee2e6;">
        <button id="ff-back" title="Back">⬅️</button>
        <button id="ff-forward" title="Forward">➡️</button>
        <button id="ff-refresh" title="Refresh">🔄</button>
        <button id="ff-home" title="Home">🏠</button>
        <input 
          id="ff-url-bar" 
          type="text" 
          placeholder="Enter URL (e.g., https://google.com)" 
          style="flex:1; padding:6px 12px; border:1px solid #ced4da; border-radius:4px; font-size:14px;"
          value=""
        />
        <button id="ff-go" title="Go" style="padding:6px 12px; background:#007bff; color:white; border:none; border-radius:4px; cursor:pointer;">Go</button>
        <div style="border-left:1px solid #dee2e6; height:24px; margin:0 8px;"></div>
        <button id="ff-fullscreen" title="Fullscreen">⛶</button>
        <button id="ff-close" title="Close" style="color:#dc3545;">❌</button>
      </div>
      
      <!-- Status indicator -->
      <div style="padding:4px 8px; ${status.includes('failed') ? 'background:#fff3cd; border-bottom:1px solid #ffeaa7;' : 'background:#d4edda; border-bottom:1px solid #c3e6cb;'} font-size:12px;">
        ${status.includes('failed') ? '🟡' : '🟢'} ${status || 'Connected to VNC'}: ${url}
      </div>
      
      <!-- Firefox VNC Iframe -->
      <iframe 
        id="${iframeId}"
        src="${url}" 
        style="width:100%; flex:1; border:none;"
        allowfullscreen
      ></iframe>
    </div>`;
};
const requestFullscreen = (element) => {
    if (element.requestFullscreen) {
        element.requestFullscreen();
    }
    else if (element.webkitRequestFullscreen) {
        element.webkitRequestFullscreen();
    }
    else if (element.mozRequestFullScreen) {
        element.mozRequestFullScreen();
    }
    else if (element.msRequestFullscreen) {
        element.msRequestFullscreen();
    }
};
const handleFullscreenChange = () => {
    if (!document.fullscreenElement &&
        !document.webkitFullscreenElement &&
        !document.mozFullScreenElement &&
        !document.msFullscreenElement) {
        console.log('Exited fullscreen mode');
    }
};
const extension = {
    id: 'jupyterlab-firefox-launcher:plugin',
    description: 'JupyterLab extension to launch Firefox in a tab',
    autoStart: true,
    requires: [ILauncher, ICommandPalette],
    activate: async (app, launcher, palette) => {
        const command = 'firefox:open';
        const label = 'Firefox Browser';
        app.commands.addCommand(command, {
            label,
            execute: async () => {
                var _a, _b, _c;
                console.log('[Firefox Launcher] Command executed');
                // Request the backend to launch Firefox and get the VNC URL
                let vncUrl = '';
                let isBackendWorking = false;
                try {
                    console.log('[Firefox Launcher] Making launch request to backend...');
                    const response = await requestAPI('launch', { method: 'POST' });
                    console.log('[Firefox Launcher] Backend response:', response);
                    if (response && response.url) {
                        vncUrl = response.url;
                        isBackendWorking = true;
                        console.log('[Firefox Launcher] ✅ Backend URL received:', vncUrl);
                    }
                    else {
                        console.warn('[Firefox Launcher] ❌ Backend response missing URL:', response);
                    }
                }
                catch (e) {
                    console.error('[Firefox Launcher] ❌ Backend API call failed:', e);
                }
                // If backend failed, construct JupyterHub proxy URL for direct Firefox access
                if (!isBackendWorking) {
                    console.log('[Firefox Launcher] 🔧 Constructing JupyterHub Firefox proxy URL...');
                    // Try to detect JupyterHub environment and build URL
                    const currentUrl = window.location.href;
                    console.log('[Firefox Launcher] Current URL:', currentUrl);
                    if (currentUrl.includes('/user/')) {
                        // Extract JupyterHub base and user info  
                        const match = currentUrl.match(/(https?:\/\/[^\/]+\/user\/[^\/]+)/);
                        if (match) {
                            const jupyterHubBase = match[1];
                            // Construct direct Firefox debugging URL through JupyterHub proxy
                            vncUrl = `${jupyterHubBase}/proxy/9222/`;
                            console.log('[Firefox Launcher] 🎯 Using direct Firefox URL:', vncUrl);
                        }
                    }
                    // Final fallback
                    if (!vncUrl) {
                        vncUrl = 'about:blank';
                        console.warn('[Firefox Launcher] ⚠️ Could not construct Firefox URL');
                    }
                }
                const content = new Widget();
                content.node.style.height = '100%';
                content.node.style.width = '100%';
                content.node.style.overflow = 'hidden';
                const iframeId = 'firefox-iframe';
                let statusMessage = '';
                if (!isBackendWorking) {
                    statusMessage = 'Direct Firefox access via JupyterHub proxy (no VNC)';
                }
                else {
                    statusMessage = 'Connected successfully via backend API';
                }
                content.node.innerHTML = buildFirefoxHTML(iframeId, vncUrl, statusMessage);
                const widget = new MainAreaWidget({ content });
                widget.id = 'firefox-browser';
                widget.title.label = label;
                widget.title.closable = true;
                widget.node.style.height = '100%';
                app.shell.add(widget, 'main');
                app.shell.activateById(widget.id);
                const iframe = content.node.querySelector(`#${iframeId}`);
                if (!iframe) {
                    console.error('Firefox iframe not found');
                    return;
                }
                (_a = content.node.querySelector('#ff-refresh')) === null || _a === void 0 ? void 0 : _a.addEventListener('click', () => {
                    iframe.src = iframe.src;
                });
                (_b = content.node.querySelector('#ff-close')) === null || _b === void 0 ? void 0 : _b.addEventListener('click', () => {
                    widget.close();
                });
                (_c = content.node.querySelector('#ff-fullscreen')) === null || _c === void 0 ? void 0 : _c.addEventListener('click', () => {
                    requestFullscreen(iframe);
                });
                // Auto exit fullscreen on ESC key
                document.addEventListener('fullscreenchange', handleFullscreenChange);
                document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
                document.addEventListener('mozfullscreenchange', handleFullscreenChange);
                document.addEventListener('MSFullscreenChange', handleFullscreenChange);
            }
        });
        launcher.add({
            command,
            category: 'Other',
            rank: 1
        });
        palette.addItem({
            command,
            category: 'Firefox'
        });
    }
};
export default extension;
