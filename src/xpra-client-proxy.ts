// Copyright (c) 2025 Vantage Compute Corporation.

/**
 * Proxy-Compatible Xpra Client for JupyterLab Firefox Launcher
 * 
 * This module provides a WebSocket-based client for connecting to Xpra servers
 * running Firefox instances through JupyterHub proxy URLs.
 */

import { XpraClient, XpraConnectionOptions } from 'xpra-html5-client';

// Custom WebSocket class that can handle proxy URLs
class ProxyCompatibleWebSocket {
  private ws?: WebSocket;
  private wsUrl: string;
  private protocols?: string | string[];
  
  public onopen?: (event: Event) => void;
  public onclose?: (event: CloseEvent) => void;
  public onerror?: (event: Event) => void;
  public onmessage?: (event: MessageEvent) => void;
  
  constructor(url: string, protocols?: string | string[]) {
    this.wsUrl = url;
    this.protocols = protocols;
    console.log(`🔧 ProxyCompatibleWebSocket: Creating WebSocket for ${url} with protocols:`, protocols);
    
    // Create the actual WebSocket connection with proper subprotocol
    this.ws = new WebSocket(url, protocols || ['binary']);
    
    // Forward all events
    this.ws.onopen = (event) => {
      console.log('🎉 ProxyCompatibleWebSocket: Connection opened');
      if (this.onopen) this.onopen(event);
    };
    
    this.ws.onclose = (event) => {
      console.log(`🔌 ProxyCompatibleWebSocket: Connection closed: code=${event.code}, reason=${event.reason}`);
      if (this.onclose) this.onclose(event);
    };
    
    this.ws.onerror = (event) => {
      console.error('❌ ProxyCompatibleWebSocket: Error:', event);
      if (this.onerror) this.onerror(event);
    };
    
    this.ws.onmessage = (event) => {
      console.log('📨 ProxyCompatibleWebSocket: Message received:', event.data);
      if (this.onmessage) this.onmessage(event);
    };
  }
  
  send(data: string | ArrayBufferLike | Blob | ArrayBufferView): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(data);
    }
  }
  
  close(code?: number, reason?: string): void {
    if (this.ws) {
      this.ws.close(code, reason);
    }
  }
  
  get readyState(): number {
    return this.ws ? this.ws.readyState : WebSocket.CLOSED;
  }
  
  get protocol(): string {
    return this.ws ? this.ws.protocol : '';
  }
  
  get url(): string {
    return this.ws ? this.ws.url : this.wsUrl;
  }
}

export interface ProxyXpraClientOptions {
  container: HTMLElement;
  wsUrl: string;
  httpUrl?: string;
  autoConnect?: boolean;
  debug?: boolean;
}

export class ProxyXpraClient {
  private client: XpraClient;
  private container: HTMLElement;
  private wsUrl: string;
  private httpUrl?: string;
  private debug: boolean;
  private isConnected: boolean = false;
  private originalWebSocket?: typeof WebSocket;

  constructor(options: ProxyXpraClientOptions) {
    this.container = options.container;
    this.wsUrl = options.wsUrl;
    this.httpUrl = options.httpUrl;
    this.debug = options.debug || false;

    // Store original WebSocket and replace with our proxy-compatible version
    this.originalWebSocket = (globalThis as any).WebSocket;
    (globalThis as any).WebSocket = ProxyCompatibleWebSocket as any;

    // Initialize the Xpra client
    this.client = new XpraClient({
      worker: undefined,
      decoder: undefined
    });

    this.setupEventHandlers();
  }

  private setupEventHandlers(): void {
    // Handle connection events
    this.client.on('connect', (status) => {
      console.log(`🔗 Xpra connected with status: ${status}`);
      this.isConnected = status === 'connected';
    });

    this.client.on('disconnect', (status) => {
      console.log(`🔌 Xpra disconnected with status: ${status}`);
      this.isConnected = false;
    });

    this.client.on('sessionStarted', () => {
      console.log('🚀 Xpra session started successfully');
    });

    // Handle server capabilities
    this.client.on('hello', (capabilities) => {
      console.log('👋 Xpra server capabilities received:', capabilities);
    });

    // Handle window creation
    this.client.on('newWindow', (window) => {
      console.log('🪟 New Xpra window created:', window);
      this.createWindowElement(window);
    });

    // Handle draw events
    this.client.on('draw', (draw) => {
      console.log('🖼️ Draw event received:', draw);
      this.handleDraw(draw);
    });

    // Handle draw events with buffer
    this.client.on('drawBuffer', (draw, buffer) => {
      console.log('🖼️ Draw buffer event received:', draw, buffer);
      this.handleDrawBuffer(draw, buffer);
    });

    // Handle errors
    this.client.on('error', (message) => {
      console.error('❌ Xpra client error:', message);
    });
  }

  private createWindowElement(window: any): void {
    const windowId = window.wid || window.id;
    const x = window.x || 0;
    const y = window.y || 0;
    const width = window.w || window.width || 800;
    const height = window.h || window.height || 600;

    console.log(`🪟 Creating window element for window ID ${windowId}: {windowId: ${windowId}, x: ${x}, y: ${y}, width: ${width}, height: ${height}}`);

    // Parse window data
    console.log(`📏 Parsed window data: ID=${windowId}, position=[${x},${y}], dimensions=[${width},${height}]`);

    // Create window container
    const windowElement = document.createElement('div');
    windowElement.id = String(windowId);
    windowElement.className = 'xpra-window';
    windowElement.style.position = 'absolute';
    windowElement.style.left = `${x}px`;
    windowElement.style.top = `${y}px`;
    windowElement.style.width = `${width}px`;
    windowElement.style.height = `${height}px`;
    windowElement.style.border = '1px solid #ccc';
    windowElement.style.backgroundColor = '#fff';

    console.log(`🎯 Window container created: <div id="${windowId}" class="xpra-window" style="..."></div>`);

    // Create canvas for rendering
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    console.log(`🎨 Canvas created: ${width}x${height} pixels`);

    // Add canvas to window element
    windowElement.appendChild(canvas);

    // Add window element to container
    this.container.appendChild(windowElement);

    console.log(`✅ Window element created successfully for ID ${windowId} with canvas`);

    // Request initial refresh for the window
    console.log(`🔄 Requesting refresh for window ${windowId}`);
    this.client.sendDamageSequence(0, windowId, [width, height], 0, 'initial');
    console.log(`📡 Sent damage-sequence request for window ${windowId}`);
  }

  private handleDraw(draw: any): void {
    console.log('🖼️ Draw event received:', draw);
    
    const windowId = draw.id !== undefined ? draw.id : draw.wid;
    const windowElement = document.getElementById(String(windowId));
    if (!windowElement) {
      console.log(`⚠️ No window element found for window ID: ${windowId}`);
      return;
    }

    const canvas = windowElement.querySelector('canvas');
    if (!canvas) {
      console.log(`⚠️ No canvas found in window element for window ID: ${windowId}`);
      console.log(`🔍 Window element children:`, windowElement.children);
      return;
    }
    
    console.log(`✅ Found canvas for window ${windowId}, processing draw event`);
    console.log(`🖼️ Canvas ready for drawing: ${canvas.width}x${canvas.height}`);
  }

  private handleDrawBuffer(draw: any, buffer: ImageBitmap | null): void {
    console.log('🖼️ Draw buffer event received:', draw, buffer);
    
    const windowId = draw.id !== undefined ? draw.id : draw.wid;
    const windowElement = document.getElementById(String(windowId));
    if (!windowElement) {
      console.log(`⚠️ No window element found for window ID: ${windowId}`);
      return;
    }

    const canvas = windowElement.querySelector('canvas');
    if (!canvas) {
      console.log(`⚠️ No canvas found in window element for window ID: ${windowId}`);
      return;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) {
      console.log(`⚠️ Could not get 2D context for canvas in window ID: ${windowId}`);
      return;
    }

    console.log(`🖼️ Drawing buffer to canvas for window ${windowId}`, buffer);

    if (buffer) {
      ctx.drawImage(buffer, draw.x || 0, draw.y || 0);
    }
  }

  async connect(): Promise<void> {
    try {
      console.log(`🔗 Proxy Xpra Connection - Using proxy-compatible WebSocket: ${this.wsUrl}`);
      
      // Initialize the client first  
      await this.client.init();
      console.log(`✅ Xpra client initialized successfully`);

      // Connection options for Xpra HTML5 client through proxy
      const options: Partial<XpraConnectionOptions> = {
        ssl: this.wsUrl.startsWith('wss://'),
        reconnect: true,
        reconnectAttempts: 5,
        reconnectInterval: 3000,
        connectionTimeout: 15000,
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

      console.log(`🔗 Connecting through proxy-compatible client with options:`, options);
      
      // The xpra client will now use our ProxyCompatibleWebSocket class
      // which can handle the proxy URL format properly
      this.client.connect(this.wsUrl, options);
      
      console.log(`🔗 Proxy connection attempt initiated to: ${this.wsUrl}`);

    } catch (error) {
      console.error('❌ Failed to connect through proxy-compatible WebSocket:', error);
      throw error;
    }
  }

  disconnect(): void {
    if (this.isConnected) {
      this.client.disconnect();
    }
    
    // Restore original WebSocket
    if (this.originalWebSocket) {
      (globalThis as any).WebSocket = this.originalWebSocket;
    }
  }

  isClientConnected(): boolean {
    return this.isConnected;
  }

  getClient(): XpraClient {
    return this.client;
  }

  // Cleanup method
  cleanup(): void {
    this.disconnect();
    
    // Clean up all window elements
    const windowElements = this.container.querySelectorAll('.xpra-window');
    windowElements.forEach(element => element.remove());
  }
}
