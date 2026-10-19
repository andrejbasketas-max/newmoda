// Lordicon animated icons (https://lordicon.com — free icons, attribution in the footer), played by lottie-web.
// Each icon lives in icons/<name>.js and is injected as a script when the icon first scrolls into view,
// which keeps the page light and also works when index.html is opened straight from disk.
import lottie from 'lottie-web/build/player/lottie_light';
import { defineElement, Element } from '@lordicon/element';

const pending = {};
Element.setIconLoader((name) => {
  const cache = (window.__lordicons ||= {});
  if (cache[name]) return Promise.resolve(cache[name]);
  pending[name] ||= new Promise((resolve, reject) => {
    const s = document.createElement('script');
    s.src = `icons/${name}.js`;
    s.onload = () => resolve(cache[name]);
    s.onerror = reject;
    document.head.appendChild(s);
  });
  return pending[name];
});

defineElement(lottie.loadAnimation);
