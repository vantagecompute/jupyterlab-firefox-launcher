// Copyright (c) 2025 Vantage Compute Corporation.

/**
 * Xpra Client Integration for JupyterLab Firefox Launcher
 * 
 * This module provides a TypeScript wrapper around the xpra-html5-client
 * library             }
      
      // Initialize the client first
      await this.client.init();      
      // Initialize the client firstonsole.log(`🎯 Direct Xpra WebSocket URL: ${finalXpraUrl}`);
      }
      
      // Initialize the client firstamless integration with our JupyterLab extension.
 */

import { XpraClient, XpraConnectionOptions } from 'xpra-html5-client';

export interface FirefoxXpraClientOptions {
  container: HTMLElement;
  wsUrl: string;
  httpUrl?: string;
  autoConnect?: boolean;
  debug?: boolean;
}

export class FirefoxXpraClient {
  private client: XpraClient;
  private container: HTMLElement;
  private wsUrl: string;
  private httpUrl?: string;
  private debug: boolean;
  private isConnected: boolean = false;

  constructor(options: FirefoxXpraClientOptions) {
    this.container = options.container;
    this.wsUrl = options.wsUrl;
    this.httpUrl = options.httpUrl;
    this.debug = options.debug || false;

    // Initialize the Xpra client with better configuration
    this.client = new XpraClient({
      // Configure workers for better performance
      worker: undefined, // Let the library handle worker creation
      decoder: undefined // Let the library handle decoder creation
    });

    this.setupEventHandlers();

    if (options.autoConnect !== false) {
      this.connect();
    }
  }

  private setupEventHandlers(): void {
    // Connection events
    this.client.on('connect', (status) => {
      console.log(`🔗 Xpra connected with status: ${status}`);
      this.isConnected = status === 'connected';
    });

    this.client.on('disconnect', (status) => {
      console.log(`🔌 Xpra disconnected with status: ${status}`);
      this.isConnected = false;
    });

    this.client.on('error', (message) => {
      console.error(`❌ Xpra error: ${message}`);
    });

    this.client.on('sessionStarted', () => {
      console.log(`🚀 Xpra session started successfully`);
    });

    // Window management events
    this.client.on('newWindow', (win) => {
      console.log(`🪟 New Xpra window created:`, win);
      this.createWindowElement(win);
    });

    this.client.on('removeWindow', (wid) => {
      console.log(`🗑️ Xpra window removed: ${wid}`);
      this.removeWindowElement(wid);
    });

    // Drawing events
    this.client.on('draw', (draw) => {
      console.log(`🎨 Xpra draw event:`, draw);
      this.handleDraw(draw);
    });

    this.client.on('drawBuffer', (draw, buffer) => {
      console.log(`🖼️ Xpra draw buffer event:`, draw, buffer);
      this.handleDrawBuffer(draw, buffer);
    });

    // Server capabilities
    this.client.on('hello', (capabilities) => {
      console.log(`👋 Xpra server capabilities received:`, capabilities);
    });

    // Additional useful events
    this.client.on('cursor', (cursor) => {
      console.log(`🖱️ Xpra cursor update:`, cursor);
    });

    this.client.on('showNotification', (notification) => {
      console.log(`📢 Xpra notification:`, notification);
    });
  }

  private createWindowElement(win: any): void {
    // Create DOM element for the Xpra window
    const windowDiv = document.createElement('div');
    windowDiv.id = `xpra-window-${win.wid}`;
    windowDiv.className = 'xpra-window';
    windowDiv.style.cssText = `
      position: absolute;
      left: ${win.x}px;
      top: ${win.y}px;
      width: ${win.w}px;
      height: ${win.h}px;
      border: 1px solid #ccc;
      background: #fff;
    `;

    // Create canvas for window content
    const canvas = document.createElement('canvas');
    canvas.width = win.w;
    canvas.height = win.h;
    canvas.style.cssText = `
      width: 100%;
      height: 100%;
      display: block;
    `;

    windowDiv.appendChild(canvas);
    this.container.appendChild(windowDiv);
  }

  private removeWindowElement(wid: number): void {
    const windowElement = document.getElementById(`xpra-window-${wid}`);
    if (windowElement) {
      windowElement.remove();
    }
  }

  private handleDraw(draw: any): void {
    // Handle drawing operations on the canvas
    const windowElement = document.getElementById(`xpra-window-${draw.wid}`);
    if (!windowElement) return;

    const canvas = windowElement.querySelector('canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Apply the drawing data to the canvas
    // This is a simplified implementation - the actual drawing logic
    // would depend on the specific draw data format
    if (draw.buffer) {
      ctx.drawImage(draw.buffer, draw.x, draw.y);
    }
  }

  private handleDrawBuffer(draw: any, buffer: ImageBitmap | null): void {
    // Handle drawing operations with provided buffer
    const windowElement = document.getElementById(`xpra-window-${draw.wid}`);
    if (!windowElement) return;

    const canvas = windowElement.querySelector('canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Use the provided buffer for drawing
    if (buffer) {
      ctx.drawImage(buffer, draw.x || 0, draw.y || 0);
    }
  }

  async connect(): Promise<void> {
    try {
      console.log(`🔗 Direct Xpra Connection - Starting connection to: ${this.wsUrl}`);
      
      // Determine if this is a direct connection or JupyterHub proxy connection
      let finalXpraUrl: string;
      
      if (this.wsUrl.includes('/user/') && this.wsUrl.includes('/proxy/')) {
        // This is a JupyterHub proxy connection - use the URL as-is
        finalXpraUrl = this.wsUrl;
        console.log(`🛤️ Using JupyterHub proxy connection: ${finalXpraUrl}`);
      } else {
        // This is a direct connection - extract host and port from query params
        // The wsUrl might be coming from the backend like: ws://192.168.7.10:8889/user/bdx/firefox-launcher/ws?host=192.168.7.10&port=42159
        let xpraHost = '192.168.7.10';
        let xpraPort = 42159;
        
        if (this.wsUrl.includes('?')) {
          const urlParts = this.wsUrl.split('?');
          const params = new URLSearchParams(urlParts[1]);
          xpraHost = params.get('host') || xpraHost;
          xpraPort = parseInt(params.get('port') || '42159');
        }
        
        console.log(`🔧 Extracted Xpra server details - Host: ${xpraHost}, Port: ${xpraPort}`);
        
        // For direct Xpra HTML5 client connection
        finalXpraUrl = `ws://${xpraHost}:${xpraPort}/`;
        console.log(`🎯 Direct Xpra WebSocket URL: ${finalXpraUrl}`);
      }
      
      console.log(`� Direct Xpra WebSocket URL: ${directXpraUrl}`);
      
      // Initialize the client first
      await this.client.init();
      console.log(`✅ Xpra client initialized successfully`);

      // Connection options for Xpra HTML5 client
      const options: Partial<XpraConnectionOptions> = {
        ssl: false, // We're using ws:// not wss://
        reconnect: true,
        reconnectAttempts: 5,
        reconnectInterval: 3000,
        connectionTimeout: 15000,
        // Xpra client options
        clipboard: true,
        keyboard: true,
        mouse: true,
        cursor: true,
        notifications: false,
        tray: false,
        bell: false,
        audio: false,
        video: false,
        encoder: 'bencode',
        debugPackets: this.debug ? ['*'] : [],
      };

      console.log(`🔗 Connecting to Xpra server with options:`, options);
      
      // Connect to either the direct Xpra server or through JupyterHub proxy
      this.client.connect(finalXpraUrl, options);
      
      console.log(`🔗 Connection attempt initiated to: ${finalXpraUrl}`);

    } catch (error) {
      console.error('❌ Failed to connect to Xpra server:', error);
      throw error;
    }
  }

  disconnect(): void {
    if (this.isConnected) {
      this.client.disconnect();
    }
  }

  isClientConnected(): boolean {
    return this.isConnected;
  }

  getClient(): XpraClient {
    return this.client;
  }

  // Cleanup method
  destroy(): void {
    this.disconnect();
    
    // Remove all window elements
    const windows = this.container.querySelectorAll('.xpra-window');
    windows.forEach(window => window.remove());
  }
}

export default FirefoxXpraClient;
