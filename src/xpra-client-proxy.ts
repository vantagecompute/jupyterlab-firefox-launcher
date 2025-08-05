// Copyright (c) 2025 Vantage Compute Corporation.

/**
 * Proxy-Compatible Xpra Client for JupyterLab Firefox Launcher
 * 
 * This module overrides the WebSocket class to allow xpra-html5-client
 * to work with JupyterHub proxy URLs that include paths.
 */

import { XpraClient, XpraConnectionOptions } from 'xpra-html5-client';

// Store reference to original WebSocket before we override it
// Use a more robust storage mechanism to prevent bypassing
const OriginalWebSocket = globalThis.WebSocket;
if (!(globalThis as any)._OriginalWebSocket) {
  (globalThis as any)._OriginalWebSocket = OriginalWebSocket;
}

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
    
    // Fix for Xpra WebSocket protocol compatibility
    // Xpra servers ALWAYS require the 'binary' subprotocol, regardless of proxy routing
    let effectiveProtocols: string[] | undefined;
    
    if (protocols && Array.isArray(protocols) && protocols.includes('binary')) {
      // Use 'binary' protocol as requested - this is what Xpra expects
      console.log('🔧 Using binary protocol for Xpra compatibility');
      effectiveProtocols = ['binary'];
    } else if (protocols === 'binary' || (typeof protocols === 'string' && protocols === 'binary')) {
      // Handle string protocol
      console.log('🔧 Using binary protocol for Xpra compatibility');
      effectiveProtocols = ['binary'];
    } else {
      // Default to binary protocol for all Xpra connections
      console.log('🔧 Defaulting to binary protocol for Xpra compatibility');
      effectiveProtocols = ['binary'];
    }    // Create the actual WebSocket connection using the ORIGINAL WebSocket class
    this.ws = new OriginalWebSocket(url, effectiveProtocols);
    
    console.log(`🔧 ProxyCompatibleWebSocket: Using protocols:`, effectiveProtocols);
    
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
  private pendingRedraws: Set<HTMLElement> = new Set();
  private drawPending: number = 0;

  constructor(options: ProxyXpraClientOptions) {
    this.container = options.container;
    this.wsUrl = options.wsUrl;
    this.httpUrl = options.httpUrl;
    this.debug = options.debug || false;

    // Store original WebSocket and replace with our proxy-compatible version
    // Use more robust storage to prevent xpra-html5-client from bypassing
    this.originalWebSocket = (globalThis as any).WebSocket;
    if (!(globalThis as any)._OriginalWebSocket) {
      (globalThis as any)._OriginalWebSocket = this.originalWebSocket;
    }
    
    // Apply override - this must happen before XpraClient initialization
    (globalThis as any).WebSocket = ProxyCompatibleWebSocket as any;
    
    console.log('🔧 WebSocket override applied for xpra-html5-client');

    // Initialize the Xpra client AFTER WebSocket override
    this.client = new XpraClient({
      worker: undefined,
      decoder: undefined
    });

    this.setupEventHandlers();

    // Handle autoConnect option
    if (options.autoConnect) {
      console.log('🚀 Auto-connecting Xpra client...');
      this.connect().catch(error => {
        console.error('❌ Auto-connect failed:', error);
      });
    }
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

    // Create visible canvas for rendering (same as official Xpra client)
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.className = 'xpra-canvas';
    console.log(`🎨 Visible canvas created: ${width}x${height} pixels`);

    // Create offscreen canvas for double buffering (same as official Xpra client)
    const offscreenCanvas = document.createElement('canvas');
    offscreenCanvas.width = width;
    offscreenCanvas.height = height;
    offscreenCanvas.className = 'xpra-offscreen-canvas';
    console.log(`🎨 Offscreen canvas created: ${width}x${height} pixels`);

    // Get canvas contexts
    const ctx = canvas.getContext('2d');
    const offscreenCtx = offscreenCanvas.getContext('2d');
    
    if (!ctx || !offscreenCtx) {
      console.error(`❌ Failed to get canvas contexts for window ${windowId}`);
      return;
    }

    // Configure contexts (same as official Xpra client)
    ctx.imageSmoothingEnabled = false;
    offscreenCtx.imageSmoothingEnabled = false;

    // Store canvas references on the window element
    (windowElement as any)._canvas = canvas;
    (windowElement as any)._offscreenCanvas = offscreenCanvas;
    (windowElement as any)._ctx = ctx;
    (windowElement as any)._offscreenCtx = offscreenCtx;
    (windowElement as any)._width = width;
    (windowElement as any)._height = height;
    (windowElement as any)._wid = windowId;

    // Add visible canvas to window element
    windowElement.appendChild(canvas);

    // Add window element to container
    this.container.appendChild(windowElement);

    console.log(`✅ Window element created successfully for ID ${windowId} with visible and offscreen canvas`);

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
    
    // Process the draw data like the official Xpra client
    this.processPaintData(windowElement, draw);
  }

  private handleDrawBuffer(draw: any, buffer: ImageBitmap | null): void {
    console.log('🖼️ Draw buffer event received:', draw, buffer);
    
    const windowId = draw.id !== undefined ? draw.id : draw.wid;
    const windowElement = document.getElementById(String(windowId));
    if (!windowElement) {
      console.log(`⚠️ No window element found for window ID: ${windowId}`);
      return;
    }

    const offscreenCtx = (windowElement as any)._offscreenCtx;
    if (!offscreenCtx) {
      console.log(`⚠️ No offscreen canvas context found for window ID: ${windowId}`);
      return;
    }

    console.log(`🖼️ Drawing buffer to offscreen canvas for window ${windowId}`, buffer);

    if (buffer) {
      // Draw to offscreen canvas first (like official Xpra client)
      const x = draw.x || 0;
      const y = draw.y || 0;
      offscreenCtx.drawImage(buffer, x, y);
      
      // Request redraw to copy offscreen to visible canvas
      this.requestRedraw(windowElement);
    }
  }

  // Main paint processing method (based on official Xpra client)
  private processPaintData(windowElement: HTMLElement, paintData: any): void {
    const offscreenCtx = (windowElement as any)._offscreenCtx;
    if (!offscreenCtx) {
      console.log(`⚠️ No offscreen canvas context found`);
      return;
    }

    console.log('🎨 Processing paint data:', paintData);

    // Extract paint parameters
    const x = paintData.x || 0;
    const y = paintData.y || 0;
    const width = paintData.width || paintData.w || 0;
    const height = paintData.height || paintData.h || 0;
    const imgData = paintData.img_data || paintData.data;
    const coding = paintData.coding || paintData.encoding || 'rgb24';

    console.log(`🎨 Paint parameters: x=${x}, y=${y}, size=${width}x${height}, coding=${coding}`);

    // Handle different image encodings (similar to official Xpra client)
    if (coding === 'rgb24' || coding === 'rgb32') {
      this.paintRgb(offscreenCtx, x, y, width, height, imgData);
    } else if (coding === 'jpeg' || coding === 'png' || coding === 'webp') {
      this.paintImage(offscreenCtx, x, y, width, height, imgData, coding);
    } else {
      console.log(`🚧 Unsupported coding: ${coding}`);
    }

    // Request redraw to copy offscreen to visible canvas
    this.requestRedraw(windowElement);
  }

  // Paint RGB data to canvas (like official Xpra client)
  private paintRgb(ctx: CanvasRenderingContext2D, x: number, y: number, width: number, height: number, rgbData: any): void {
    console.log(`🎨 Painting RGB data: ${width}x${height} at (${x},${y})`);
    
    if (!rgbData) {
      console.log(`⚠️ No RGB data provided`);
      return;
    }

    try {
      // Create ImageData from RGB data
      const imageData = ctx.createImageData(width, height);
      
      // Convert RGB data to RGBA format
      if (rgbData instanceof Uint8Array || Array.isArray(rgbData)) {
        for (let i = 0; i < width * height; i++) {
          const srcOffset = i * 3; // RGB = 3 bytes per pixel
          const dstOffset = i * 4; // RGBA = 4 bytes per pixel
          
          imageData.data[dstOffset] = rgbData[srcOffset];     // R
          imageData.data[dstOffset + 1] = rgbData[srcOffset + 1]; // G
          imageData.data[dstOffset + 2] = rgbData[srcOffset + 2]; // B
          imageData.data[dstOffset + 3] = 255; // A (fully opaque)
        }
      }
      
      // Draw to offscreen canvas
      ctx.putImageData(imageData, x, y);
      console.log(`✅ RGB data painted successfully`);
    } catch (error) {
      console.error(`❌ Failed to paint RGB data:`, error);
    }
  }

  // Paint image data to canvas (like official Xpra client)
  private paintImage(ctx: CanvasRenderingContext2D, x: number, y: number, width: number, height: number, imgData: any, coding: string): void {
    console.log(`🎨 Painting ${coding} image: ${width}x${height} at (${x},${y})`);
    
    if (!imgData) {
      console.log(`⚠️ No image data provided`);
      return;
    }

    try {
      const image = new Image();
      image.addEventListener('load', () => {
        if (image.width === 0 || image.height === 0) {
          console.log(`❌ Invalid image size: ${image.width}x${image.height}`);
          return;
        }
        
        // Clear the area and draw the image
        ctx.clearRect(x, y, width, height);
        ctx.drawImage(image, x, y, width, height);
        console.log(`✅ ${coding} image painted successfully`);
      });
      
      image.onerror = () => {
        console.error(`❌ Failed to load ${coding} image`);
      };
      
      // Create data URL for the image
      const dataUrl = this.constructBase64ImageUrl(coding, imgData);
      image.src = dataUrl;
    } catch (error) {
      console.error(`❌ Failed to paint ${coding} image:`, error);
    }
  }

  // Construct base64 data URL (based on official Xpra client)
  private constructBase64ImageUrl(coding: string, imgData: any): string {
    let base64Data = '';
    
    if (typeof imgData === 'string') {
      base64Data = imgData;
    } else if (imgData instanceof Uint8Array) {
      // Convert Uint8Array to base64
      const binary = Array.from(imgData, byte => String.fromCharCode(byte)).join('');
      base64Data = btoa(binary);
    } else {
      console.log(`🚧 Unknown image data format for ${coding}`);
      return '';
    }
    
    return `data:image/${coding};base64,${base64Data}`;
  }

  // Request redraw (like official Xpra client)
  private requestRedraw(windowElement: HTMLElement): void {
    console.log('🔄 Requesting redraw for window');
    
    if (this.pendingRedraws.has(windowElement)) {
      console.log('🔄 Redraw already pending for this window');
      return;
    }
    
    this.pendingRedraws.add(windowElement);
    
    if (this.drawPending) {
      console.log('� Draw already scheduled');
      return;
    }
    
    // Schedule draw using requestAnimationFrame (like official Xpra client)
    this.drawPending = performance.now();
    window.requestAnimationFrame(() => {
      this.drawPendingList();
    });
  }

  // Draw all pending windows (like official Xpra client)
  private drawPendingList(): void {
    const elapsed = performance.now() - this.drawPending;
    console.log(`🎨 Animation frame: ${this.pendingRedraws.size} windows to paint, processing delay ${elapsed}ms`);
    
    this.drawPending = 0;
    
    // Draw all pending windows
    for (const windowElement of this.pendingRedraws) {
      this.drawWindow(windowElement);
    }
    
    this.pendingRedraws.clear();
  }

  // Draw window (copy offscreen to visible canvas - like official Xpra client)
  private drawWindow(windowElement: HTMLElement): void {
    const canvas = (windowElement as any)._canvas;
    const offscreenCanvas = (windowElement as any)._offscreenCanvas;
    const ctx = (windowElement as any)._ctx;
    
    if (!canvas || !offscreenCanvas || !ctx) {
      console.log(`⚠️ Missing canvas elements for draw`);
      return;
    }
    
    console.log('🎨 Drawing window: copying offscreen to visible canvas');
    
    // Clear visible canvas and copy from offscreen (same as official Xpra client draw() method)
    ctx.clearRect(0, 0, offscreenCanvas.width, offscreenCanvas.height);
    ctx.drawImage(offscreenCanvas, 0, 0);
    
    console.log('✅ Window draw completed');
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
    
    // Restore original WebSocket using robust storage
    if ((globalThis as any)._OriginalWebSocket) {
      (globalThis as any).WebSocket = (globalThis as any)._OriginalWebSocket;
    } else if (this.originalWebSocket) {
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
