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

// Import styles  
import '../src/index.css';

// Import Firefox SVG icon
import firefoxIconSvg from '../src/style/icons/firefox.svg';

// Create the Firefox icon
export const firefoxIcon = new LabIcon({
  name: 'firefox-launcher:firefox',
  svgstr: firefoxIconSvg
});

console.log('🔥 Firefox icon created:', firefoxIcon);
console.log('🔥 Firefox SVG content length:', firefoxIconSvg?.length || 'undefined');

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
    
    console.log('🔥 JupyterLab extension jupyterlab-firefox-launcher is activated!');
    console.log('🔥 Launcher available:', !!launcher);
    console.log('🔥 App commands:', app.commands);
    
    // Register the launch command first
    app.commands.addCommand('firefox-launcher:launch', {
      label: 'Firefox',
      caption: 'Launch Firefox in a new tab',
      icon: firefoxIcon,
      execute: async () => {
        console.log('🔥 Firefox launcher command executed!');
        try {
          // Lazy load the launcher module and return the widget
          const { launchFirefox } = await import('./launcher');
          return launchFirefox(app);
        } catch (error) {
          console.error('🔥 Error launching Firefox:', error);
          throw error;
        }
      }
    });
    
    console.log('🔥 Firefox command registered');
    
    // Add Firefox launcher to the "Other" category
    if (launcher) {
      const translatedCategory = trans.__('Other');
      const hardcodedCategory = 'Other';
      console.log('🔥 Translated category:', JSON.stringify(translatedCategory));
      console.log('🔥 Hardcoded category:', JSON.stringify(hardcodedCategory));
      console.log('🔥 Are they equal?', translatedCategory === hardcodedCategory);
      
      // Use translated version to match Terminal and FileEditor patterns
      launcher.add({
        command: 'firefox-launcher:launch',
        category: trans.__('Other'),
        rank: 0
      });
      console.log('🔥 Firefox launcher added with translated category');
    } else {
      console.error('🔥 Launcher not available - cannot add Firefox launcher');
    }
  }
};

// Export the plugin as the default export
const extension = plugin;
export default extension;