// Cache the game shell after the first successful online visit.
const CACHE = "manoj-arcade-v1";
const SHELL = ["./", "./index.html", "./style.css", "./app.mjs", "./engine.mjs", "./level.json"];
self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL)));
});
self.addEventListener("activate", event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys
    .filter(key => key.startsWith("manoj-arcade-") && key !== CACHE).map(key => caches.delete(key))))
    .then(() => self.clients.claim()));
});
self.addEventListener("fetch", event => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.origin !== self.location.origin ||
      !url.href.startsWith(self.registration.scope)) return;
  event.respondWith(fetch(event.request).then(response => {
    if (response.ok) {
      const backup = response.clone();
      event.waitUntil(caches.open(CACHE).then(cache => cache.put(event.request, backup)));
    }
    return response;
  }).catch(async () => (await caches.match(event.request)) ||
    (event.request.mode === "navigate" ? await caches.match("./") : Response.error())));
});
