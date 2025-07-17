import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { URLExt } from '@jupyterlab/coreutils';
import { ITranslator, nullTranslator } from '@jupyterlab/translation';
import { Widget } from '@lumino/widgets';

/**
 * Firefox Launcher Extension - Frontend Component
 * 
 * Adds a Firefox launcher icon to JupyterLab that opens the server-proxy Firefox desktop.
 */

// Add Firefox icon CSS styles
const firefoxIconCSS = `
.jp-FirefoxIcon {
  background-image: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJDNi40OCAyIDIgNi40OCAyIDEyUzYuNDggMjIgMTIgMjJTMjIgMTcuNTIgMjIgMTJTMTcuNTIgMiAxMiAyWk0xMi43NSA2LjVDMTMuMzggNi41IDE0IDYuODggMTQgNy41VjkuNUMxNCA5Ljc4IDE0LjIyIDEwIDE0LjUgMTBIMTYuNUMxNy4xMiAxMCAxNy41IDEwLjYyIDE3LjUgMTEuMjVTMTcuMTIgMTIuNSAxNi41IDEyLjVIMTQuNUMxNC4yMiAxMi41IDE0IDEyLjcyIDE0IDEzVjE1QzE0IDE1LjYyIDEzLjM4IDE2IDEyLjc1IDE2UzExLjUgMTUuNjIgMTEuNSAxNVYxM0MxMS41IDEyLjcyIDExLjI4IDEyLjUgMTEgMTIuNUg5QzguMzggMTIuNSA4IDExLjg4IDggMTEuMjVTOC4zOCAxMCA5IDEwSDExQzExLjI4IDEwIDExLjUgOS43OCAxMS41IDkuNVY3LjVDMTEuNSA2Ljg4IDEyLjEyIDYuNSAxMi43NSA2LjVaIiBmaWxsPSIjRkY1NzIyIi8+Cjwvc3ZnPgo=');
  background-size: 16px 16px;
  background-repeat: no-repeat;
  background-position: center;
}
`;

// Inject CSS into document head
function injectCSS(css: string): void {
  const style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);
}
const extension: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-firefox-launcher:plugin',
  autoStart: true,
  requires: [],
  optional: [ITranslator],
  activate: (app: JupyterFrontEnd, translator?: ITranslator) => {
    console.log('Firefox launcher extension loaded');
    
    const trans = (translator ?? nullTranslator).load('jupyterlab');
    
    // Inject Firefox icon CSS for the launcher
    injectCSS(firefoxIconCSS);
    
    // NO LONGER CREATING LAUNCHER HERE - the server proxy handles launcher placement
    // This matches the jupyter-remote-desktop-proxy pattern more closely
    
    // Register command to open Firefox Desktop in JupyterLab tab (for potential future use)
    app.commands.addCommand('firefox-desktop:open', {
      label: 'Firefox Browser',
      caption: 'Launch Firefox Desktop Browser in JupyterLab',
      iconClass: 'jp-FirefoxIcon',
      execute: () => {
        // Open Firefox Desktop via server proxy in a JupyterLab tab
        const url = URLExt.join(app.serviceManager.serverSettings.baseUrl, 'firefox-desktop');
        const widget = new Widget();
        widget.title.label = 'Firefox Desktop';
        widget.title.iconClass = 'jp-FirefoxIcon';
        widget.title.closable = true;
        
        // Create iframe to load the server proxy
        const iframe = document.createElement('iframe');
        iframe.src = url;
        iframe.style.width = '100%';
        iframe.style.height = '100%';
        iframe.style.border = 'none';
        
        widget.node.appendChild(iframe);
        
        // Add to main area
        if (!widget.isAttached) {
          app.shell.add(widget, 'main');
        }
        app.shell.activateById(widget.id);
      }
    });
  }
};

export default extension;