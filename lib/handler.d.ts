/**
 * Make a request to the backend of the JupyterLab Firefox launcher extension.
 *
 * This helper wraps a `fetch` call to a Jupyter server extension API endpoint.
 *
 * @param endpoint - The endpoint to call (e.g., 'launch')
 * @param init - The fetch initialization parameters
 * @returns A promise resolving to the response JSON
 */
export declare function requestAPI<T>(endpoint?: string, init?: RequestInit): Promise<T>;
