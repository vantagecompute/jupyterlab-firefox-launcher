import { ILauncher } from '@jupyterlab/launcher';
import { ICommandPalette, MainAreaWidget } from '@jupyterlab/apputils';
import { requestAPI } from './handler.js';
import { Widget } from '@lumino/widgets';
const buildFirefoxHTML = (iframeId, url) => {
    return `
    <div style="display:flex; justify-content:end; padding:4px; gap:8px; background:#f5f5f5;">
      <button id="ff-refresh">🔄 Refresh</button>
      <button id="ff-fullscreen">⛶ Fullscreen</button>
      <button id="ff-close">❌ Close</button>
    </div>
    <iframe 
      id="${iframeId}"
      src="${url}" 
      style="width:100%; height:90%; border:none;"
      allowfullscreen
    ></iframe>`;
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
        const url = 'http://localhost:6080';
        app.commands.addCommand(command, {
            label,
            execute: async () => {
                var _a, _b, _c;
                // Request the backend to launch Firefox
                try {
                    await requestAPI('launch');
                }
                catch (e) {
                    console.error('Failed to launch Firefox:', e);
                }
                const content = new Widget();
                content.node.style.height = '100%';
                content.node.style.width = '100%';
                content.node.style.overflow = 'hidden';
                const iframeId = 'firefox-iframe';
                content.node.innerHTML = buildFirefoxHTML(iframeId, url);
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
