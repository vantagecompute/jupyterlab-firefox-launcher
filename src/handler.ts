// src/handler.ts

/**
 * Make a request to the backend of the JupyterLab Firefox launcher extension.
 *
 * This helper wraps a `fetch` call to a Jupyter server extension API endpoint.
 *
 * @param endpoint - The endpoint to call (e.g., 'launch')
 * @param init - The fetch initialization parameters
 * @returns A promise resolving to the response JSON
 */
export async function requestAPI<T>(
  endpoint = '',
  init: RequestInit = {}
): Promise<T> {
  const url = `/jupyterhub-firefox-launcher/${endpoint}`;

  const response = await fetch(url, {
    method: 'GET',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json'
    },
    ...init
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(`API request failed with status ${response.status}: ${message}`);
  }

  return response.json();
}

