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
  ITranslator,
  nullTranslator
} from '@jupyterlab/translation';

// Import Firefox SVG icon
import firefoxIconSvg from '../style/icons/firefox-icon.svg';

// Create the Firefox icon
export const firefoxIcon = new LabIcon({
  name: 'firefox-launcher:firefox',
  svgstr: firefoxIconSvg
});

/**
 * Initialization data for the firefox-launcher extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-firefox-launcher:plugin',
  description: 'A JupyterLab extension to launch Firefox in a tab',
  autoStart: true,
  requires: [ILauncher],
  optional: [ITranslator],
  activate: (app: JupyterFrontEnd, launcher: ILauncher, translator?: ITranslator) => {
    const trans = (translator ?? nullTranslator).load('jupyterlab');
    
    console.log('JupyterLab Firefox Launcher: Extension activated');
    
    // Register the launch command
    app.commands.addCommand('firefox-launcher:launch', {
      label: 'Firefox Browser',
      caption: 'Launch Firefox browser in a new tab',
      icon: firefoxIcon,
      execute: async () => {
        console.log('Firefox launcher: Executing command');
        try {
          const { launchFirefox } = await import('./launcher');
          return launchFirefox(app);
        } catch (error) {
          console.error('Firefox launcher: Error executing command', error);
          throw error;
        }
      }
    });
    
    // Add Firefox launcher to the launcher panel
    if (launcher) {
      launcher.add({
        command: 'firefox-launcher:launch',
        category: trans.__('Other'),
        rank: 100, // Use higher rank to avoid being first in category
      });
      console.log('Firefox launcher: Added to launcher panel');
    } else {
      console.error('Firefox launcher: Launcher service not available');
    }
  }
};

// Export the plugin as the default export
const extension = plugin;
export default extension;