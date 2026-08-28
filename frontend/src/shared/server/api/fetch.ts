import { FrappeApp } from 'frappe-js-sdk'

import {
  attachFrappeUnauthorizedInterceptor,
  attachRawAuthorizationHeaderInterceptor,
} from './interceptor'
import { useServerUrl } from '../composables/useServerUrl'
let frappeApp: FrappeApp | null = null;


export function resetFrappeApp(): void {
  frappeApp = null;
}

export function getFrappeApp(): FrappeApp | null {
  const url = useServerUrl().serverUrl;
  if (!url) return null;
  if (!frappeApp || frappeApp.url !== url.value) {
    frappeApp = new FrappeApp(url.value);
    attachRawAuthorizationHeaderInterceptor(frappeApp.axios)
    attachFrappeUnauthorizedInterceptor(frappeApp.axios)
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
