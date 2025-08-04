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
import { ProxyXpraClient } from './xpra-client-proxy';

// Import CSS styles
import '../style/index.css';

/**
 * A widget that hosts the Firefox browser through Xpra proxy
 */
class FirefoxWidget extends Widget {
  private _loadingDiv: HTMLDivElement;
  private _xpraContainer: HTMLDivElement;
  private _xpraClient: ProxyXpraClient | null = null;
  private _xpraPort: number | null = null;
  private _processId: number | null = null;
  private _beforeUnloadHandler: () => void;
  private _isFullyInitialized: boolean = false; // Flag to prevent premature cleanup

  constructor() {
    super();
    console.log('🔧 ========= FIREFOX WIDGET CONSTRUCTOR START =========');
    
    this.addClass('jp-FirefoxWidget');
    this.title.label = 'Firefox Browser';
    this.title.closable = true;
    this.title.iconClass = 'jp-LauncherIcon jp-FirefoxIcon';
    
    console.log('🔧 Widget classes:', this.node.className);
    console.log('🔧 Widget title:', this.title.label);
    console.log('🔧 Widget icon class:', this.title.iconClass);

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

    // Create container for TypeScript Xpra client
    this._xpraContainer = document.createElement('div');
    this._xpraContainer.className = 'jp-firefox-xpra-container';
    this._xpraContainer.style.width = '100%';
    this._xpraContainer.style.height = '100%';
    this._xpraContainer.style.display = 'none'; // Hidden initially

    this.node.appendChild(this._loadingDiv);
    this.node.appendChild(this._xpraContainer);

    console.log('🔧 Widget DOM structure created');
    console.log('🔧 Loading div:', this._loadingDiv);
    console.log('🔧 Xpra container:', this._xpraContainer);

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
    
    console.log('✅ ========= FIREFOX WIDGET CONSTRUCTOR COMPLETE =========');
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
   * Refresh the Firefox connection using Xpra client
   */
  refresh(): void {
    console.log('🔄 Refresh called - using pure Xpra client approach');
    // Pure Xpra client approach - no iframe fallback
    if (this._xpraClient) {
      console.log('✅ Xpra client already exists and connected');
    } else {
      console.log('⚠️ No Xpra client - widget needs to be properly initialized via setXpraClientAndConnect');
    }
  }

  /**
   * Use TypeScript Xpra client with WebSocket connection
   */
  setXpraClientAndConnect(websocketUrl: string, httpUrl?: string): void {
    console.log('🔗 Using TypeScript Xpra client with proxy compatibility', { websocketUrl, httpUrl });
    
    try {
      // Test with proxy-compatible client first
      console.log('🔧 Testing proxy-compatible WebSocket client');
      this._xpraClient = new ProxyXpraClient({
        container: this._xpraContainer,
        wsUrl: websocketUrl,
        httpUrl: httpUrl,
        autoConnect: false,  // We'll call connect manually
        debug: true
      });

      // Hide loading indicator and show Xpra container
      this._loadingDiv.style.display = 'none';
      this._xpraContainer.style.display = 'block';

      // Manually initiate connection
      this._xpraClient.connect();

      console.log('✅ Proxy-compatible Xpra client initialized successfully');
    } catch (error) {
      console.error('❌ Failed to initialize TypeScript Xpra client:', error);
      // Show error in loading div instead of iframe fallback
      this._loadingDiv.innerHTML = `
        <div style="color: red; text-align: center; padding: 20px;">
          <h3>Connection Error</h3>
          <p>Failed to initialize Xpra client: ${error}</p>
          <p>Please try refreshing the page.</p>
        </div>
      `;
      this._loadingDiv.style.display = 'block';
    }
  }

  /**
   * Show an error message in the widget
   */
  showError(title: string, message: string): void {
    this._loadingDiv.innerHTML = `
      <div style="color: red; text-align: center; padding: 20px;">
        <h3>${title}</h3>
        <p>${message}</p>
      </div>
    `;
    this._loadingDiv.style.display = 'block';
    this._xpraContainer.style.display = 'none';
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
    
    // Clean up TypeScript Xpra client if it exists
    if (this._xpraClient) {
      console.log('🧹 Cleaning up TypeScript Xpra client');
      this._xpraClient.cleanup();
      this._xpraClient = null;
    }
    
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
    console.log('🚀 ========= FIREFOX LAUNCHER EXTENSION ACTIVATION START =========');
    console.log('🔧 JupyterLab extension jupyterlab-firefox-launcher is activated!');
    console.log('🔧 Plugin ID:', 'jupyterlab-firefox-launcher:plugin');
    console.log('🔧 App object:', app);
    console.log('🔧 Launcher object:', launcher);
    console.log('🔧 Layout restorer object:', restorer);
    console.log('🔧 JupyterLab version:', (app as any).version || 'unknown');

    const namespace = 'firefox-browser';
    let widgetCounter = 0;

    // Create a command to launch Firefox
    const command = 'firefox-launcher:open';
    console.log('🔧 Creating command:', command);
    
    app.commands.addCommand(command, {
      label: 'Firefox Browser',
      iconClass: 'jp-LauncherIcon jp-FirefoxIcon',
      execute: async () => {
        console.log('🚀 ========= FIREFOX COMMAND EXECUTION START =========');
        console.log('🔧 Firefox launcher command executed!');
        console.log('🔧 Widget counter:', widgetCounter);
        
        try {
          // Create and show Firefox widget immediately
          console.log('🔧 Creating FirefoxWidget...');
          const widget = new FirefoxWidget();
          const widgetId = `firefox-browser-${++widgetCounter}`;
          widget.id = widgetId;
          console.log('🔧 Created widget with ID:', widgetId);
          
          // Add widget to main area
          console.log('🔧 Adding widget to main area...');
          app.shell.add(widget, 'main');
          console.log('🔧 Widget added to main area');
          
          console.log('🔧 Activating widget...');
          app.shell.activateById(widgetId);
          console.log('🔧 Widget activated');
          
          // Register with layout restorer
          console.log('🔧 Registering with layout restorer...');
          restorer.add(widget, widgetId);
          console.log('🔧 Widget registered with layout restorer');
          
          // Start Firefox server process and wait for proxy to become available
          console.log('🔧 Starting Firefox server process...');
          await startFirefoxWithRetry(widget);
          console.log('✅ Firefox server process started successfully');
          
        } catch (error) {
          console.error('❌ ========= FIREFOX COMMAND EXECUTION ERROR =========');
          console.error('❌ Error launching Firefox:', error);
          console.error('❌ Error stack:', error instanceof Error ? error.stack : 'No stack trace');
          alert('Failed to start Firefox browser. Check console for details.');
        }
      }
    });
    
    console.log('✅ Command created successfully:', command);

    /**
     * Start Firefox and wait for Xpra proxy to become available with retry logic
     */
    async function startFirefoxWithRetry(widget: FirefoxWidget): Promise<void> {
      console.log('🚀 ========= START FIREFOX WITH RETRY =========');
      
      const maxRetries = 30; // 30 retries with 2-second intervals = 1 minute timeout
      const retryInterval = 2000; // 2 seconds
      
      console.log('🔧 Max retries:', maxRetries);
      console.log('🔧 Retry interval:', retryInterval, 'ms');
      
      try {
        // Start Firefox server process
        console.log('🌐 Starting Firefox process via API...');
        console.log('🌐 Making POST request to /firefox-launcher/api/firefox');
        
        const response = await requestAPI('firefox', {
          method: 'POST'
        }) as any;
        
        console.log('📡 API Response received:', response);
        console.log('📡 Response type:', typeof response);
        console.log('📡 Response keys:', Object.keys(response));
        
        if (response.status === 'error') {
          console.error('❌ Server returned error status:', response.message);
          throw new Error(response.message || 'Failed to start Firefox');
        }
        
        // Extract port, proxy path, process ID, and client URL from response if available
        const xpraPort = response.port;
        const proxyPath = response.proxy_path;
        const processId = response.process_id;
        const clientUrl = response.client_url;
        const websocketUrl = response.websocket_url;
        const httpUrl = response.http_url;
        
        console.log('📡 Extracted response data:');
        console.log('   🔌 Xpra Port:', xpraPort);
        console.log('   🛤️  Proxy Path:', proxyPath);
        console.log('   🆔 Process ID:', processId);
        console.log('   🌐 Client URL:', clientUrl);
        console.log('   🔗 WebSocket URL:', websocketUrl);
        console.log('   🌍 HTTP URL:', httpUrl);
        
        console.log(`✅ Firefox process started on port ${xpraPort}, process ID: ${processId}`);
        if (clientUrl) {
          console.log(`📱 Custom client URL: ${clientUrl}`);
        }
        if (websocketUrl) {
          console.log(`🔗 Direct WebSocket URL: ${websocketUrl}`);
        }
        if (httpUrl) {
          console.log(`🌍 Direct HTTP URL: ${httpUrl}`);
        }
        console.log(`🛤️ Proxy path: ${proxyPath}, waiting for connection...`);
        
        // Store process ID in widget for cleanup
        if (processId) {
          console.log('🔧 Setting process ID in widget:', processId);
          widget.setProcessId(processId);
        } else {
          console.warn('⚠️ No process ID received from server');
        }
        
        // Wait for connection to be available
        console.log('🔄 Starting connection retry loop...');
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
          console.log(`🔄 Connection attempt ${attempt}/${maxRetries}`);
          
          try {
            // Determine the URL to test based on what's available
            let testUrl: string;
            
            console.log('🔧 Determining test URL...');
            
            // PRIORITY: For TypeScript Xpra client, test the actual Xpra server directly
            if (websocketUrl && httpUrl) {
              // Test the HTTP URL directly since WebSocket test is more complex
              const httpUrlObj = new URL(httpUrl);
              testUrl = `http://${httpUrlObj.hostname}:${httpUrlObj.port}/`;
              console.log('🔧 Using direct HTTP URL for testing:', testUrl);
            } else if (clientUrl) {
              // Use custom client URL (best option)
              testUrl = clientUrl;
              console.log('🔧 Using custom client URL for testing:', testUrl);
            } else if (proxyPath) {
              // Use the proxy path provided by the backend
              testUrl = proxyPath;
              console.log('🔧 Using proxy path for testing:', testUrl);
            } else if (xpraPort) {
              // Dynamic fallback: Detect JupyterHub vs JupyterLab
              const currentPath = window.location.pathname;
              const userMatch = currentPath.match(/^\/user\/[^\/]+\//);
              const basePath = userMatch ? userMatch[0] : '/';
              testUrl = `${basePath}proxy/${xpraPort}/`;
              console.log('🔧 Using dynamic port URL for testing:', testUrl);
              console.log('🔧 Current path:', currentPath);
              console.log('🔧 User match:', userMatch);
              console.log('🔧 Base path:', basePath);
            } else {
              // Fallback to direct proxy route
              testUrl = '/firefox-launcher/firefox';
              console.log('🔧 Using fallback direct proxy route for testing:', testUrl);
            }
            
            console.log(`🌐 Testing connection to: ${testUrl}`);
            
            // Test if the connection is ready
            // For custom client, we just need to verify the endpoint exists
            const testResponse = await fetch(testUrl, {
              method: 'HEAD',
              cache: 'no-cache'
            });
            
            console.log(`📡 Test response status: ${testResponse.status}`);
            console.log(`📡 Test response ok: ${testResponse.ok}`);
            console.log(`📡 Test response status text: ${testResponse.statusText}`);
            
                          // Accept various status codes that indicate readiness
            if (testResponse.ok || testResponse.status === 302 || testResponse.status === 400) {
              console.log(`✅ Connection ready after ${attempt} attempts`);
              console.log(`✅ Final test response: ${testResponse.status} ${testResponse.statusText}`);
              
              // PRIORITY: Use TypeScript Xpra client with WebSocket URL
              if (websocketUrl) {
                console.log(`🎯 Using TypeScript Xpra client with WebSocket: ${websocketUrl}`);
                console.log(`🎯 HTTP URL for fallback: ${httpUrl}`);
                widget.setXpraClientAndConnect(websocketUrl, httpUrl);
              } else {
                console.error(`❌ No WebSocket URL available - cannot connect to Xpra`);
                console.log('Available URLs:', { httpUrl, clientUrl, proxyPath, xpraPort });
                // Show error in widget
                widget.showError(
                  'Configuration Error',
                  'No WebSocket URL provided for Xpra connection. Pure Xpra client requires WebSocket connectivity.'
                );
              }
              
              console.log('✅ ========= START FIREFOX WITH RETRY COMPLETE =========');
              return;
            } else if (testResponse.status === 503) {
              // Service unavailable - not ready yet
              console.log(`⏳ Attempt ${attempt}/${maxRetries}: Connection not ready (503) - service unavailable`);
            } else {
              console.log(`⚠️ Attempt ${attempt}/${maxRetries}: Unexpected response status ${testResponse.status} ${testResponse.statusText}`);
            }
          } catch (proxyError) {
            // Network error - proxy not yet available
            const errorMessage = proxyError instanceof Error ? proxyError.message : 'Xpra proxy not yet available';
            console.log(`🔄 Attempt ${attempt}/${maxRetries}: Network error - ${errorMessage}`);
            console.log(`🔄 Error details:`, proxyError);
          }
          
          // Wait before next attempt
          if (attempt < maxRetries) {
            console.log(`⏱️ Waiting ${retryInterval}ms before next attempt...`);
            await new Promise(resolve => setTimeout(resolve, retryInterval));
          }
        }
        
        // If we reach here, the proxy didn't become available within timeout
        console.error(`❌ Timeout: Xpra proxy did not become available within ${maxRetries * retryInterval / 1000} seconds`);
        throw new Error(`Xpra proxy did not become available within ${maxRetries * retryInterval / 1000} seconds`);
        
      } catch (error) {
        console.error('❌ ========= START FIREFOX WITH RETRY ERROR =========');
        console.error('❌ Failed to start Firefox with Xpra proxy:', error);
        console.error('❌ Error type:', typeof error);
        console.error('❌ Error constructor:', error?.constructor?.name);
        if (error instanceof Error) {
          console.error('❌ Error message:', error.message);
          console.error('❌ Error stack:', error.stack);
        }
        
        // Update widget to show error message
        console.log('🔧 Updating widget to show error message...');
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
        console.log('🔧 Error message displayed in widget');
        
        throw error;
      }
    }

    // Add command to launcher in Tools category
    console.log('🔧 Adding command to launcher...');
    console.log('🔧 Command:', command);
    console.log('🔧 Category: Tools');
    console.log('🔧 Rank: 1');
    
    const launcherItem = {
      command,
      category: 'Tools',
      rank: 1
    };
    console.log('🔧 Launcher item:', launcherItem);
    
    try {
      launcher.add(launcherItem);
      console.log('✅ Successfully added Firefox launcher to Tools category');
      console.log('✅ Launcher should now show Firefox Browser option in Tools category');
    } catch (error) {
      console.error('❌ Failed to add launcher item:', error);
      console.error('❌ Error details:', error instanceof Error ? error.stack : 'No stack trace');
    }

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
    
    // Add debugging functions to window for troubleshooting
    (window as any).debugFirefoxExtension = () => {
      console.log('🔧 ========= FIREFOX EXTENSION DEBUG INFO =========');
      console.log('🔧 Extension ID:', plugin.id);
      console.log('🔧 Command registered:', command);
      console.log('🔧 Available commands:', app.commands.listCommands());
      console.log('🔧 Command exists:', app.commands.listCommands().includes(command) ? 'REGISTERED' : 'NOT REGISTERED');
      console.log('🔧 Launcher items count:', (launcher as any)._items?.length || 'Unknown');
      console.log('🔧 Shell mode:', (app.shell as any).mode || 'Unknown');
      console.log('🔧 Current widgets:', Array.from(app.shell.widgets('main')).map((w: any) => ({ id: w.id, title: w.title.label })));
      
      // Try to list launcher items
      try {
        const items = (launcher as any)._items || [];
        console.log('🔧 Launcher items:', items.map((item: any) => ({
          command: item.command,
          category: item.category,
          rank: item.rank
        })));
      } catch (error) {
        console.log('🔧 Could not access launcher items:', error);
      }
      
      console.log('🔧 ========= END DEBUG INFO =========');
    };
    
    (window as any).testFirefoxLaunch = async () => {
      console.log('🚀 ========= TESTING FIREFOX LAUNCH =========');
      try {
        await app.commands.execute(command);
        console.log('✅ Firefox launch command executed successfully');
      } catch (error) {
        console.error('❌ Firefox launch command failed:', error);
      }
    };
    
    console.log('💡 Debug functions available:');
    console.log('   window.debugFirefoxExtension() - Show extension debug info');
    console.log('   window.testFirefoxLaunch() - Test Firefox launch directly');
    
    console.log('🎉 ========= FIREFOX LAUNCHER EXTENSION ACTIVATION COMPLETE =========');
    console.log('🎉 Extension should be fully functional now');
    console.log('🎉 Look for "Firefox Browser" in the Tools category of the launcher');
  }
};

export default plugin;
