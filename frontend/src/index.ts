import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ILauncher } from '@jupyterlab/launcher';
import { URLExt } from '@jupyterlab/coreutils';
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
  requires: [ILauncher],
  activate: (app: JupyterFrontEnd, launcher: ILauncher) => {
    console.log('Firefox launcher frontend component loaded');
    
    // Inject Firefox icon CSS
    injectCSS(firefoxIconCSS);
    
    // Add Firefox launcher to the JupyterLab launcher
    launcher.add({
      command: 'firefox-launcher:open',
      category: 'Other',
      rank: 1
    });

    // Register the command to open Firefox
    app.commands.addCommand('firefox-launcher:open', {
      label: 'Firefox Desktop',
      caption: 'Launch Firefox in a desktop environment via Xpra',
      iconClass: 'jp-FirefoxIcon',
      execute: () => {
        // Use JupyterLab's proper URL construction for server proxy
        const baseUrl = app.serviceManager.serverSettings.baseUrl;
        const firefoxUrl = URLExt.join(baseUrl, 'firefox-desktop');
        
        console.log('Opening Firefox desktop at:', firefoxUrl);
        
        // Create iframe widget to embed Firefox desktop within JupyterLab
        const iframe = document.createElement('iframe');
        iframe.src = firefoxUrl;
        iframe.style.width = '100%';
        iframe.style.height = '100%';
        iframe.style.border = 'none';
        iframe.setAttribute('allowfullscreen', 'true');
        
        const widget = new Widget({ node: iframe });
        widget.id = 'firefox-desktop-' + Date.now();
        widget.title.label = 'Firefox Desktop';
        widget.title.iconClass = 'jp-FirefoxIcon';
        widget.title.closable = true;
        widget.addClass('jp-FirefoxDesktopWidget');
        
        // IMPORTANT: Open in a new JupyterLab tab, NOT a browser tab
        app.shell.add(widget, 'main');
        app.shell.activateById(widget.id);
      }
    });
  }
};

export default extension;