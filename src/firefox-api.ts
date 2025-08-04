// Copyright (c) 2025 Vantage Compute Corporation.

import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';

/**
 * Call the API extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
export async function requestAPI<T>(
  endPoint = '',
  init: RequestInit = {}
): Promise<T> {
  console.log('🌐 ========= API REQUEST START =========');
  console.log('🌐 Endpoint:', endPoint);
  console.log('🌐 Init options:', init);
  
  // Make request to Jupyter API
  const settings = ServerConnection.makeSettings();
  const requestUrl = URLExt.join(
    settings.baseUrl,
    'firefox-launcher',
    'api', 
    endPoint
  );
  
  console.log('🌐 Settings:', settings);
  console.log('🌐 Request URL:', requestUrl);
  console.log('🌐 Base URL:', settings.baseUrl);

  let response: Response;
  try {
    console.log('🌐 Making server connection request...');
    response = await ServerConnection.makeRequest(requestUrl, init, settings);
    console.log('🌐 Response received:', response);
    console.log('🌐 Response status:', response.status, response.statusText);
    console.log('🌐 Response ok:', response.ok);
  } catch (error) {
    console.error('❌ Server connection error:', error);
    console.error('❌ Error type:', typeof error);
    console.error('❌ Error details:', error);
    throw new ServerConnection.NetworkError(error as any);
  }

  let data: any = await response.text();
  console.log('📡 Response text length:', data.length);
  console.log('📡 Response text (first 500 chars):', data.substring(0, 500));

  if (data.length > 0) {
    try {
      data = JSON.parse(data);
      console.log('📡 Parsed JSON data:', data);
      console.log('📡 JSON data type:', typeof data);
      console.log('📡 JSON data keys:', Object.keys(data));
    } catch (error) {
      console.log('⚠️ Not a JSON response body.', response);
      console.log('⚠️ Parse error:', error);
    }
  }

  if (!response.ok) {
    console.error('❌ Response not ok:', response.status, response.statusText);
    console.error('❌ Error data:', data);
    throw new ServerConnection.ResponseError(response, data.message || data);
  }

  console.log('✅ ========= API REQUEST SUCCESS =========');
  console.log('✅ Returning data:', data);
  return data;
}
