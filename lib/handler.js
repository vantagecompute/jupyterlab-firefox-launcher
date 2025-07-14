// src/handler.ts
import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';
/**
 * Make a request to the backend of the JupyterLab Firefox launcher extension.
 *
 * This helper wraps a `fetch` call to a Jupyter server extension API endpoint.
 *
 * @param endpoint - The endpoint to call (e.g., 'launch')
 * @param init - The fetch initialization parameters
 * @returns A promise resolving to the response JSON
 */
export async function requestAPI(endpoint = '', init = {}) {
    // Use JupyterLab's built-in utilities to construct the correct URL
    const settings = ServerConnection.makeSettings();
    const requestUrl = URLExt.join(settings.baseUrl, 'jupyterlab-firefox-launcher', endpoint);
    console.log(`[Firefox Launcher] Making API request to: ${requestUrl}`);
    console.log(`[Firefox Launcher] Base URL: ${settings.baseUrl}`);
    console.log(`[Firefox Launcher] Request init:`, init);
    const response = await ServerConnection.makeRequest(requestUrl, {
        method: 'POST',
        ...init
    }, settings);
    console.log(`[Firefox Launcher] Response status: ${response.status}`);
    console.log(`[Firefox Launcher] Response headers:`, response.headers);
    if (!response.ok) {
        const message = await response.text();
        console.error(`[Firefox Launcher] API request failed with status ${response.status}: ${message}`);
        throw new Error(`API request failed with status ${response.status}: ${message}`);
    }
    const result = response.json();
    console.log(`[Firefox Launcher] Response data:`, result);
    return result;
}
