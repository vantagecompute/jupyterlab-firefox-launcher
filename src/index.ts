// src/index.ts
import type { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ILauncher } from '@jupyterlab/launcher';
import { ICommandPalette, MainAreaWidget } from '@jupyterlab/apputils';
import { requestAPI } from './handler.js';
import { Widget } from '@lumino/widgets';

const buildFirefoxHTML = (iframeId: string, url: string): string => {
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

const requestFullscreen = (element: HTMLElement) => {
  if (element.requestFullscreen) {
    element.requestFullscreen();
  } else if ((element as any).webkitRequestFullscreen) {
    (element as any).webkitRequestFullscreen();
  } else if ((element as any).mozRequestFullScreen) {
    (element as any).mozRequestFullScreen();
  } else if ((element as any).msRequestFullscreen) {
    (element as any).msRequestFullscreen();
  }
};

const handleFullscreenChange = () => {
  if (!document.fullscreenElement &&
      !(document as any).webkitFullscreenElement &&
      !(document as any).mozFullScreenElement &&
      !(document as any).msFullscreenElement) {
    console.log('Exited fullscreen mode');
  }
};

const extension: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-firefox-launcher:plugin',
  description: 'JupyterLab extension to launch Firefox in a tab',
  autoStart: true,
  requires: [ILauncher, ICommandPalette],
  activate: async (app: JupyterFrontEnd, launcher: ILauncher, palette: ICommandPalette) => {
    const command = 'firefox:open';
    const label = 'Firefox Browser';
    const url = 'http://localhost:6080';

    app.commands.addCommand(command, {
      label,
      execute: async () => {
        // Request the backend to launch Firefox
        try {
          await requestAPI<any>('launch');
        } catch (e) {
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

        content.node.querySelector('#ff-fullscreen')?.addEventListener('click', () => {
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

