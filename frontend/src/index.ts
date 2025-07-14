// src/index.ts
import type { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ILauncher } from '@jupyterlab/launcher';
import { ICommandPalette, MainAreaWidget } from '@jupyterlab/apputils';
import { Widget } from '@lumino/widgets';

const buildFirefoxHTML = (iframeId: string, url: string): string => {
  return `
    <div style="display:flex; justify-content:end; padding:4px; gap:8px; background:#f5f5f5;">
      <button id="ff-refresh">🔄 Refresh</button>
      <button id="ff-close">❌ Close</button>
    </div>
    <iframe 
      id="${iframeId}"
      src="${url}" 
      style="width:100%; height:90%; border:none;"
      allowfullscreen
    ></iframe>`;
};

const extension: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-firefox-launcher:plugin',
  description: 'JupyterLab extension to launch Firefox in a tab',
  autoStart: true,
  requires: [ILauncher, ICommandPalette],
  activate: async (app: JupyterFrontEnd, launcher: ILauncher, palette: ICommandPalette): Promise<void> => {
    const command = 'firefox:open';
    const label = 'Firefox Browser';

    app.commands.addCommand(command, {
      label,
      execute: async () => {
        // Use jupyter-server-proxy URL - it will automatically start the service
        const baseUrl = app.serviceManager.serverSettings.baseUrl;
        const firefoxUrl = `${baseUrl}proxy/firefox/`;
        
        const content = new Widget();
        content.node.style.height = '100%';
        content.node.style.width = '100%';
        content.node.style.overflow = 'hidden';

        const iframeId = 'firefox-iframe';
        content.node.innerHTML = buildFirefoxHTML(iframeId, firefoxUrl);

        const widget = new MainAreaWidget({ content });
        widget.id = 'firefox-browser';
        widget.title.label = label;
        widget.title.closable = true;
        widget.node.style.height = '100%';

        app.shell.add(widget, 'main');
        app.shell.activateById(widget.id);

        const iframe = content.node.querySelector(`#${iframeId}`) as HTMLIFrameElement | null;
        if (!iframe) {
          console.error('Firefox iframe not found');
          return;
        }

        content.node.querySelector('#ff-refresh')?.addEventListener('click', () => {
          iframe.src = iframe.src;
        });

        content.node.querySelector('#ff-close')?.addEventListener('click', () => {
          widget.close();
        });
      }
    });

    launcher.add({
      command,
      category: 'Other',
      rank: 1
    });

    palette.addItem({
      command,
      category: 'Other'
    });
  }
};

export default extension;

export { buildFirefoxHTML };