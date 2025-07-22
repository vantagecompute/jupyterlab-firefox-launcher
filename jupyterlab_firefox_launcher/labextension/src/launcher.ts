import {
  JupyterFrontEnd
} from '@jupyterlab/application';

import {
  IFrame,
  MainAreaWidget
} from '@jupyterlab/apputils';

import {
  ServerConnection
} from '@jupyterlab/services';

import {
  URLExt
} from '@jupyterlab/coreutils';

import {
  Widget
} from '@lumino/widgets';

/**
 * Create a new Firefox iframe widget for the main area
 */
function createFirefoxWidget(url: string): MainAreaWidget<IFrame> {
  const content = new IFrame({
    // Provide sandbox exceptions for Firefox to function properly
    sandbox: [
      'allow-same-origin',
      'allow-scripts', 
      'allow-popups',
      'allow-forms',
      'allow-downloads',
      'allow-modals'
    ]
  });
  
  content.title.label = 'Firefox Desktop';
  content.title.closable = true;
  content.url = url;
  content.addClass('jp-Firefox-iframe');
  content.id = `firefox-desktop-${Date.now()}`;
  
  // Add error handling for the iframe
  content.node.addEventListener('load', () => {
    console.log('Firefox launcher: IFrame loaded successfully');
  });
  
  content.node.addEventListener('error', (event) => {
    console.error('Firefox launcher: IFrame load error:', event);
  });
  
  const widget = new MainAreaWidget({ content });
  widget.addClass('jp-Firefox-widget');
  
  return widget;
}

/**
 * Launch Firefox in a JupyterLab tab using iframe widget
 */
export async function launchFirefox(app: JupyterFrontEnd): Promise<Widget> {
  try {
    console.log('Firefox launcher: Starting Firefox session...');
    
    // Get the Firefox proxy URL with authentication
    const settings = ServerConnection.makeSettings();
    let firefoxUrl = URLExt.join(settings.baseUrl, 'proxy', 'firefox-desktop/');
    
    // Add token authentication to the URL for the iframe
    if (settings.token) {
      firefoxUrl = `${firefoxUrl}?token=${settings.token}`;
    }
    
    console.log('Firefox launcher: Target URL:', firefoxUrl);
    
    // Create the iframe widget immediately - no pre-flight check needed
    const widget = createFirefoxWidget(firefoxUrl);
    
    // Add to the main area as a new tab
    app.shell.add(widget, 'main');
    
    // Activate the new tab
    app.shell.activateById(widget.id);
    
    console.log('Firefox launcher: Widget created and activated');
    
    return widget;
  } catch (error) {
    console.error('Firefox launcher: Failed to launch', error);
    const errorMsg = error instanceof Error ? error.message : String(error);
    throw new Error(`Failed to launch Firefox: ${errorMsg}`);
  }
}
