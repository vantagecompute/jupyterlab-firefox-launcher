import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
  ILauncher
} from '@jupyterlab/launcher';

import {
  LabIcon
} from '@jupyterlab/ui-components';

import {
  ServerConnection
} from '@jupyterlab/services';

import {
  URLExt
} from '@jupyterlab/coreutils';

// Import styles  
import './index.css';

// Import Firefox SVG icon
import firefoxIconSvg from './style/icons/firefox.svg';

// Create the Firefox icon
export const firefoxIcon = new LabIcon({
  name: 'firefox-launcher:firefox',
  svgstr: firefoxIconSvg
});

/**
 * Make API request to the server
 */
async function requestAPI<T>(endPoint = '', init: RequestInit = {}): Promise<T> {
  const settings = ServerConnection.makeSettings();
  const requestUrl = URLExt.join(
    settings.baseUrl,
    'firefox-launcher',
    endPoint
  );

  let response: Response;
  try {
    response = await ServerConnection.makeRequest(requestUrl, init, settings);
  } catch (error) {
    throw new ServerConnection.NetworkError(error as any);
  }

  let data: any = await response.text();
  if (data.length > 0) {
    try {
      data = JSON.parse(data);
    } catch (error) {
      console.log('Not a JSON response body.', response);
    }
  }

  if (!response.ok) {
    throw new ServerConnection.ResponseError(response, data.message || data);
  }

  return data;
}

/**
 * Launch Firefox by making API call to start xpra
 */
async function launchFirefox(app: JupyterFrontEnd): Promise<void> {
  try {
    console.log('Launching Firefox...');
    
    // Make API call to start Firefox
    const result = await requestAPI<any>('launch', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    console.log('Firefox launch result:', result);
    
    if (result.status === 'success') {
      // Open Firefox in a new browser tab/window
      // The server will provide the proxy URL
      const baseUrl = ServerConnection.makeSettings().baseUrl;
      const firefoxUrl = URLExt.join(baseUrl, 'proxy', 'firefox-desktop');
      
      console.log('Opening Firefox at:', firefoxUrl);
      window.open(firefoxUrl, '_blank');
    } else {
      console.error('Failed to launch Firefox:', result.message);
      alert(`Failed to launch Firefox: ${result.message}`);
    }
  } catch (error) {
    console.error('Error launching Firefox:', error);
    const errorMsg = error instanceof Error ? error.message : String(error);
    alert(`Error launching Firefox: ${errorMsg}`);
  }
}

/**
 * Initialization data for the firefox-launcher extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-firefox-launcher:plugin',
  description: 'A JupyterLab extension to launch Firefox in a tab',
  autoStart: true,
  requires: [ILauncher],
  activate: (app: JupyterFrontEnd, launcher: ILauncher) => {
    console.log('JupyterLab extension jupyterlab-firefox-launcher is activated!');
    
    // Add Firefox launcher to the "Other" category
    launcher.add({
      command: 'firefox-launcher:launch',
      category: 'Other',
      rank: 1
    });
    
    // Register the launch command
    app.commands.addCommand('firefox-launcher:launch', {
      label: 'Firefox',
      caption: 'Launch Firefox in a new tab',
      icon: firefoxIcon,
      execute: () => {
        return launchFirefox(app);
      }
    });
  }
};

export default plugin;