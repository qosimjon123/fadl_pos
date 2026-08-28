import { getFrappeCall } from './fetch'

export const ping = () =>
  getFrappeCall()?.get<string>('ping') ?? Promise.reject(new Error('offline'))
