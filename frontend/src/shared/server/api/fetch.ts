import { FrappeApp } from 'frappe-js-sdk';
import { useServerUrl } from '../composables/useServerUrl';
let frappeApp: FrappeApp | null = null;



function createFrappeApp(url: string): FrappeApp {
  const app = new FrappeApp(url);

  // attachRawAuthorizationHeaderInterceptor(app.axios);
  // attachFrappeUnauthorizedInterceptor(app.axios);

  return app;
}

export function resetFrappeApp(): void {
  frappeApp = null;
}

export function getFrappeApp(): FrappeApp | null {
  const url = useServerUrl().serverUrl;
  if (!url) return null;
  if (!frappeApp || frappeApp.url !== url.value) {
    frappeApp = createFrappeApp(url.value);
  }
  return frappeApp;
}

export function getFrappeCall() {
  return getFrappeApp()?.call() ?? null;
}

export function getFrappeDb() {
  return getFrappeApp()?.db() ?? null;
}

export function getFrappeAuth() {
  return getFrappeApp()?.auth() ?? null;
}

export function getFrappeFileUpload() {
  return getFrappeApp()?.file() ?? null;
}
