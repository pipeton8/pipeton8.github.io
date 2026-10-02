'use strict';

const CACHE_VERSION = 'modernslides-shell-v2';
const RUNTIME_CACHE = 'modernslides-runtime-v2';
const APP_SHELL = [
  './index.html',
  './style-gallery.html',
  './manifest.webmanifest',
  './icon-180.png',
  './icon-512.png',
  './icon.svg'
];
const DEPENDENCY_HOSTS = new Set([
  'cdnjs.cloudflare.com',
  'cdn.jsdelivr.net',
  'fonts.googleapis.com',
  'fonts.gstatic.com'
]);

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then(cache => cache.addAll(APP_SHELL))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const keep = new Set([CACHE_VERSION, RUNTIME_CACHE]);
    const names = await caches.keys();
    await Promise.all(names.filter(name => !keep.has(name)).map(name => caches.delete(name)));
    await self.clients.claim();
  })());
});

async function cacheResponse(request, response) {
  if (!response || (!response.ok && response.type !== 'opaque')) return response;
  try {
    const cache = await caches.open(RUNTIME_CACHE);
    await cache.put(request, response.clone());
  } catch (error) {
    console.warn('ModernSlides could not cache a runtime resource.', error);
  }
  return response;
}

async function networkFirst(request, fallback = null) {
  try {
    return await cacheResponse(request, await fetch(request));
  } catch {
    const fallbackUrl = fallback ? new URL(fallback, self.registration.scope).href : null;
    return (await caches.match(request)) || (fallbackUrl ? await caches.match(fallbackUrl) : null) || Response.error();
  }
}

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  return cacheResponse(request, await fetch(request));
}

async function staleWhileRevalidate(request) {
  const cached = await caches.match(request);
  const update = fetch(request).then(response => cacheResponse(request, response)).catch(() => null);
  return cached || (await update) || Response.error();
}

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  const sameOrigin = url.origin === self.location.origin;

  if (sameOrigin && url.pathname.includes('/api/')) return;

  if (request.mode === 'navigate') {
    event.respondWith(networkFirst(request, './index.html'));
    return;
  }

  if (sameOrigin && /\.(?:json|txt)$/i.test(url.pathname)) {
    event.respondWith(networkFirst(request));
    return;
  }

  if (sameOrigin) {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }

  if (DEPENDENCY_HOSTS.has(url.hostname)) {
    event.respondWith(cacheFirst(request));
  }
});
