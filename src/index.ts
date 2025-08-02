// Copyright (c) 2025 Vantage Compute Corporation.

import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
  ILauncher
} from '@jupyterlab/launcher';

import {
  ILayoutRestorer
} from '@jupyterlab/application';

import {
  Widget
} from '@lumino/widgets';

import { Message } from '@lumino/messaging';

import { LabIcon } from '@jupyterlab/ui-components';

import { requestAPI } from './firefox-api';

// Import CSS styles
import '../style/index.css';

/**
 * A widget that hosts the Firefox browser through Xpra proxy
 */
class FirefoxWidget extends Widget {
  private _iframe: HTMLIFrameElement;
  private _loadingDiv: HTMLDivElement;
  private _xpraPort: number | null = null;
  private _processId: number | null = null;
  private _beforeUnloadHandler: () => void;
  private _isFullyInitialized: boolean = false; // Flag to prevent premature cleanup

  constructor() {
    super();
    this.addClass('jp-FirefoxWidget');
    this.title.label = 'Firefox Browser';
    this.title.closable = true;
    this.title.iconClass = 'jp-LauncherIcon jp-FirefoxIcon';

    // Create loading indicator
    this._loadingDiv = document.createElement('div');
    this._loadingDiv.className = 'jp-firefox-loading';
    this._loadingDiv.innerHTML = `
      <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 20px;">
        <div style="margin-bottom: 20px;">
          <svg width="50" height="50" viewBox="0 0 50 50">
            <circle cx="25" cy="25" r="20" fill="none" stroke="#ff6611" stroke-width="4" stroke-linecap="round" stroke-dasharray="31.416" stroke-dashoffset="31.416">
              <animate attributeName="stroke-dasharray" dur="2s" values="0 31.416;15.708 15.708;0 31.416" repeatCount="indefinite"/>
              <animate attributeName="stroke-dashoffset" dur="2s" values="0;-15.708;-31.416" repeatCount="indefinite"/>
            </svg>
          </div>
        <h3 style="color: #ff6611; margin: 10px 0;">Starting Firefox</h3>
        <p style="color: #666; text-align: center;">Please wait while Firefox is starting up through Xpra...</p>
      </div>
    `;

    // Create iframe for Firefox proxy (initially hidden)
    this._iframe = document.createElement('iframe');
    this._iframe.style.width = '100%';
    this._iframe.style.height = '100%';
    this._iframe.style.border = 'none';
    this._iframe.style.display = 'none'; // Hidden initially
    this._iframe.title = 'Firefox Browser';
    
    this.node.appendChild(this._loadingDiv);
    this.node.appendChild(this._iframe);

    // Add window beforeunload listener as safety net (for browser close, not tab close)
    this._beforeUnloadHandler = () => {
      console.log('🚨 Window beforeunload - emergency cleanup');
      if (this._processId && this._isFullyInitialized) {
        // Use navigator.sendBeacon for beforeunload as it's more reliable
        const data = JSON.stringify({
          process_id: this._processId,
          port: this._xpraPort
        });
        navigator.sendBeacon('/firefox-launcher/api/cleanup', data);
      }
    };
    window.addEventListener('beforeunload', this._beforeUnloadHandler);
  }

  /**
   * Handle before hide event - JupyterLab widget lifecycle
   * NOTE: onBeforeHide is called during widget creation, so we should NOT cleanup here
   * Only cleanup when the widget is actually being closed/disposed
   */
  protected onBeforeHide(msg: Message): void {
    console.log('🔄 Firefox Widget: onBeforeHide called - NOT performing cleanup (this is normal during widget creation)');
    // BUGFIX: Don't cleanup on hide - this gets called during normal widget lifecycle
    // Only cleanup on actual close/dispose
    super.onBeforeHide(msg);
  }

  /**
   * Handle close request - JupyterLab widget lifecycle
   * This is the correct place to perform cleanup when user actually closes the tab
   */
  protected onCloseRequest(msg: Message): void {
    console.log('🔄 Firefox Widget: onCloseRequest called - performing cleanup for tab close');
    this._performImmediateCleanup().catch(error => {
      console.error('❌ onCloseRequest cleanup failed:', error);
    });
    super.onCloseRequest(msg);
  }

  /**
   * Perform immediate cleanup when widget is being closed
   */
  private async _performImmediateCleanup(): Promise<void> {
    console.log('🔥 Performing immediate cleanup...');
    
    if (!this._isFullyInitialized) {
      console.log('⏭️ Widget not fully initialized yet, skipping cleanup');
      return;
    }
    
    if (!this._processId) {
      console.log('⚠️ No process ID for immediate cleanup');
      return;
    }

    console.log(`🧹 Cleaning up Firefox session: process=${this._processId}, port=${this._xpraPort}`);

    // Use proper API function with XSRF token
    try {
      const result = await requestAPI('cleanup', {
        method: 'POST',
        body: JSON.stringify({
          process_id: this._processId,
          port: this._xpraPort
        })
      });
      console.log('✅ Immediate cleanup result:', result);
    } catch (error) {
      console.error('❌ Immediate cleanup failed:', error);
    }
  }

  /**
   * Set the Xpra port and refresh the Firefox connection
   */
  setPortAndRefresh(port: number): void {
    this._xpraPort = port;
    // Use absolute URL to prevent path duplication issues in JupyterHub
    const proxyPath = `/user/bdx/proxy/${port}/`;
    const absoluteUrl = `${window.location.origin}${proxyPath}`;
    this._iframe.src = absoluteUrl;
    // Hide loading indicator and show iframe
    this._loadingDiv.style.display = 'none';
    this._iframe.style.display = 'block';
  }

  /**
   * Set the proxy path and refresh the Firefox connection
   */
  setProxyPathAndRefresh(proxyPath: string): void {
    // Use absolute URL to prevent path duplication issues in JupyterHub
    const absoluteUrl = proxyPath.startsWith('/') ? 
      `${window.location.origin}${proxyPath}` : proxyPath;
    this._iframe.src = absoluteUrl;
    // Hide loading indicator and show iframe
    this._loadingDiv.style.display = 'none';
    this._iframe.style.display = 'block';
  }

  /**
   * Refresh the Firefox connection and show the iframe
   */
  refresh(): void {
    if (this._xpraPort) {
      this.setPortAndRefresh(this._xpraPort);
    } else {
      // Fallback for compatibility - use direct proxy route
      this._iframe.src = `/firefox-launcher/firefox`;
      this._loadingDiv.style.display = 'none';
      this._iframe.style.display = 'block';
    }
  }

  /**
   * Set the process ID for cleanup when widget is disposed
   */
  setProcessId(processId: number): void {
    this._processId = processId;
    this._isFullyInitialized = true; // Mark as fully initialized after process ID is set
    console.log(`✅ Firefox widget fully initialized with process ID: ${processId}`);
  }

  /**
   * Clean up the Xpra process when widget is disposed
   */
  dispose(): void {
    console.log('🧹 FirefoxWidget.dispose() called');
    console.log(`   Process ID: ${this._processId}`);
    console.log(`   Port: ${this._xpraPort}`);
    
    // Remove beforeunload listener
    if (this._beforeUnloadHandler) {
      window.removeEventListener('beforeunload', this._beforeUnloadHandler);
      console.log('🗑️ Removed beforeunload listener');
    }
    
    if (this._processId && this._isFullyInitialized) {
      console.log(`🔥 Calling cleanup for process ${this._processId}...`);
      
      // Try async cleanup first, but also do synchronous fallback
      this._cleanupXpraProcess().catch(error => {
        console.error('Async cleanup failed, trying synchronous fallback:', error);
      });
      
      // Synchronous fallback using sendBeacon for dispose as it's more reliable
      try {
        const data = JSON.stringify({
          process_id: this._processId,
          port: this._xpraPort
        });
        navigator.sendBeacon('/firefox-launcher/api/cleanup', data);
        console.log('🔄 Synchronous cleanup request sent via sendBeacon');
      } catch (syncError) {
        console.error('Synchronous cleanup also failed:', syncError);
      }
    } else {
      if (!this._processId) {
        console.log('⚠️ No process ID to cleanup');
      } else {
        console.log('⚠️ Widget not fully initialized, skipping cleanup');
      }
    }
    
    super.dispose();
    console.log('✅ FirefoxWidget.dispose() completed');
  }

  /**
   * Send cleanup request to backend to kill Xpra process
   */
  private async _cleanupXpraProcess(): Promise<void> {
    try {
      console.log(`🌐 Sending cleanup request to backend for process ${this._processId}`);
      
      const response = await requestAPI('cleanup', {
        method: 'POST',
        body: JSON.stringify({ 
          process_id: this._processId,
          port: this._xpraPort 
        })
      });
      
      console.log(`✅ Cleanup response:`, response);
      console.log(`✅ Successfully cleaned up Xpra process ${this._processId}`);
    } catch (error) {
      console.error(`❌ Failed to cleanup Xpra process ${this._processId}:`, error);
      console.error(`   Error details:`, error);
    }
  }
}

/**
 * The command IDs used by the firefox launcher plugin.
 */
namespace CommandIDs {
  export const launch = 'firefox-launcher:launch';
}

/**
 * Initialization data for the jupyterlab-firefox-launcher extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-firefox-launcher:plugin',
  description: 'Firefox browser launcher for JupyterLab',
  autoStart: true,
  requires: [ILauncher, ILayoutRestorer],
  activate: (app: JupyterFrontEnd, launcher: ILauncher, restorer: ILayoutRestorer) => {
    console.log('JupyterLab extension jupyterlab-firefox-launcher is activated!');

    const namespace = 'firefox-browser';
    let widgetCounter = 0;

    // Create a command to launch Firefox
    const command = 'firefox-launcher:open';
    app.commands.addCommand(command, {
      label: 'Firefox Browser',
      iconClass: 'jp-LauncherIcon jp-FirefoxIcon',
      execute: async () => {
        try {
          // Create and show Firefox widget immediately
          const widget = new FirefoxWidget();
          const widgetId = `firefox-browser-${++widgetCounter}`;
          widget.id = widgetId;
          
          // Add widget to main area
          app.shell.add(widget, 'main');
          app.shell.activateById(widgetId);
          
          // Register with layout restorer
          restorer.add(widget, widgetId);
          
          // Start Firefox server process and wait for proxy to become available
          await startFirefoxWithRetry(widget);
          
        } catch (error) {
          console.error('Error launching Firefox:', error);
          alert('Failed to start Firefox browser. Check console for details.');
        }
      }
    });

    /**
     * Start Firefox and wait for Xpra proxy to become available with retry logic
     */
    async function startFirefoxWithRetry(widget: FirefoxWidget): Promise<void> {
      const maxRetries = 30; // 30 retries with 2-second intervals = 1 minute timeout
      const retryInterval = 2000; // 2 seconds
      
      try {
        // Start Firefox server process
        console.log('Starting Firefox process...');
        const response = await requestAPI('firefox', {
          method: 'POST'
        }) as any;
        
        if (response.status === 'error') {
          throw new Error(response.message || 'Failed to start Firefox');
        }
        
        // Extract port, proxy path, and process ID from response if available
        const xpraPort = response.port;
        const proxyPath = response.proxy_path;
        const processId = response.process_id;
        console.log(`Firefox process started on port ${xpraPort}, proxy path: ${proxyPath}, process ID: ${processId}, waiting for Xpra proxy...`);
        
        // Store process ID in widget for cleanup
        if (processId) {
          widget.setProcessId(processId);
        }
        
        // Wait for Xpra proxy to become available
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
          try {
            // Determine the proxy URL to test based on whether we have proxy path info
            let testUrl: string;
            if (proxyPath) {
              // Use the proxy path provided by the backend
              testUrl = proxyPath;
            } else if (xpraPort) {
              // Fallback: Try JupyterHub proxy route
              testUrl = `/user/bdx/proxy/${xpraPort}/`;
            } else {
              // Fallback to direct proxy route
              testUrl = '/firefox-launcher/firefox';
            }
            
            // Test if the proxy is responding
            const proxyResponse = await fetch(testUrl, {
              method: 'HEAD',
              cache: 'no-cache'
            });
            
            // Accept both 200 (ready) and 302 (redirect, which means Xpra is ready)
            if (proxyResponse.ok || proxyResponse.status === 302) {
              console.log(`Xpra proxy is available after ${attempt} attempts`);
              if (proxyPath) {
                // Use the proxy path from backend response
                widget.setProxyPathAndRefresh(proxyPath);
              } else if (xpraPort) {
                widget.setPortAndRefresh(xpraPort); // Use dynamic port
              } else {
                widget.refresh(); // Use fallback route
              }
              return;
            } else if (proxyResponse.status === 503) {
              // Service unavailable - Xpra not ready yet
              console.log(`Attempt ${attempt}/${maxRetries}: Xpra proxy not ready (503)`);
            } else {
              console.log(`Attempt ${attempt}/${maxRetries}: Unexpected response status ${proxyResponse.status}`);
            }
          } catch (proxyError) {
            // Network error - proxy not yet available
            const errorMessage = proxyError instanceof Error ? proxyError.message : 'Xpra proxy not yet available';
            console.log(`Attempt ${attempt}/${maxRetries}: Network error - ${errorMessage}`);
          }
          
          // Wait before next attempt
          await new Promise(resolve => setTimeout(resolve, retryInterval));
        }
        
        // If we reach here, the proxy didn't become available within timeout
        throw new Error(`Xpra proxy did not become available within ${maxRetries * retryInterval / 1000} seconds`);
        
      } catch (error) {
        console.error('Failed to start Firefox with Xpra proxy:', error);
        
        // Update widget to show error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'jp-firefox-error';
        errorDiv.innerHTML = `
          <div style="padding: 20px; text-align: center; color: #f44336;">
            <h3>Firefox Launch Failed</h3>
            <p>${error instanceof Error ? error.message : 'Unknown error occurred'}</p>
            <button onclick="location.reload()">Retry</button>
          </div>
        `;
        widget.node.innerHTML = '';
        widget.node.appendChild(errorDiv);
        
        throw error;
      }
    }

    // Add command to launcher in Tools category
    launcher.add({
      command,
      category: 'Tools',
      rank: 1
    });

    // Add global cleanup functions for debugging that use proper XSRF tokens
    // Conservative cleanup (default) - only managed sessions
    (window as any).cleanupFirefox = async () => {
      console.log('🔧 Manual Firefox cleanup triggered (conservative)');
      try {
        const result = await requestAPI('cleanup', {
          method: 'POST',
          body: JSON.stringify({
            process_id: 'all', // Special value to kill managed Firefox/Xpra processes
            port: null
          })
        });
        console.log('🧹 Conservative cleanup result:', result);
        return result;
      } catch (error) {
        console.error('❌ Conservative cleanup failed:', error);
        return error;
      }
    };

    // Cleanup with directory removal
    (window as any).cleanupFirefoxWithDirs = async () => {
      console.log('🔧 Manual Firefox cleanup with directory removal triggered');
      console.warn('⚠️ This will remove session directories for terminated sessions');
      try {
        const result = await requestAPI('cleanup?cleanup_dirs=true', {
          method: 'POST',
          body: JSON.stringify({
            process_id: 'all',
            port: null
          })
        });
        console.log('🧹 Cleanup with directories result:', result);
        return result;
      } catch (error) {
        console.error('❌ Cleanup with directories failed:', error);
        return error;
      }
    };

    // Nuclear cleanup (dangerous) - kills ALL Firefox/Xpra processes on system
    (window as any).nuclearCleanupFirefox = async () => {
      console.error('💥 NUCLEAR CLEANUP REQUESTED - THIS IS DANGEROUS!');
      console.warn('⚠️ This will kill ALL Firefox and Xpra processes on the system, not just managed ones');
      console.warn('⚠️ This may affect other users or applications using Firefox/Xpra');
      console.warn('⚠️ Use only as a last resort for debugging');
      
      const confirmed = confirm(
        'NUCLEAR CLEANUP WARNING!\n\n' +
        'This will kill ALL Firefox and Xpra processes on the system.\n' +
        'This may affect other users and applications.\n\n' +
        'Are you sure you want to proceed?'
      );
      
      if (!confirmed) {
        console.log('Nuclear cleanup cancelled by user');
        return { status: 'cancelled', message: 'User cancelled nuclear cleanup' };
      }
      
      try {
        const result = await requestAPI('cleanup?nuclear=true&confirm_nuclear=true&cleanup_dirs=true', {
          method: 'POST',
          body: JSON.stringify({
            process_id: 'all',
            port: null
          })
        });
        console.log('💀 Nuclear cleanup result:', result);
        return result;
      } catch (error) {
        console.error('❌ Nuclear cleanup failed:', error);
        return error;
      }
    };

    console.log('💡 Manual cleanup options available:');
    console.log('   window.cleanupFirefox() - Conservative cleanup (managed sessions only)');
    console.log('   window.cleanupFirefoxWithDirs() - Cleanup + remove session directories');
    console.log('   window.nuclearCleanupFirefox() - Nuclear cleanup (ALL processes - DANGEROUS!)');
  }
};

export default plugin;
