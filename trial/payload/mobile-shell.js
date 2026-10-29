/* Display-only browser integration. No game state, saves or input rules live here. */
(() => {
  let probe;
  window.SCP_SAFE_AREA = () => {
    if (!probe) {
      probe = document.createElement('div');
      probe.setAttribute('aria-hidden', 'true');
      probe.style.cssText = 'position:fixed;visibility:hidden;pointer-events:none;padding:env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left)';
      document.body.appendChild(probe);
    }
    const css = getComputedStyle(probe);
    return {width: innerWidth, height: innerHeight,
      top: parseFloat(css.paddingTop) || 0, right: parseFloat(css.paddingRight) || 0,
      bottom: parseFloat(css.paddingBottom) || 0, left: parseFloat(css.paddingLeft) || 0};
  };
  document.addEventListener('DOMContentLoaded', () => {
    const hint = document.createElement('div');
    hint.id = 'orientation-hint';
    hint.setAttribute('role', 'status');
    const language = navigator.language || 'en';
    hint.textContent = /^zh-(CN|Hans)/i.test(language) ? '横向握持可获得更大视野与操作区' : language.startsWith('zh') ? '橫向握持可獲得較大視野與操作區' : 'Turn landscape for a wider view and larger controls';
    document.body.appendChild(hint);
    const css = document.createElement('style');
    css.textContent = '#orientation-hint{display:none;pointer-events:none;position:fixed;bottom:calc(env(safe-area-inset-bottom) + 20px);left:12px;right:12px;text-align:center;color:#d6d5c6;font:14px system-ui;background:#101b24cc;padding:10px;z-index:3}@media(orientation:portrait) and (pointer:coarse){#orientation-hint{display:block}}';
    document.head.appendChild(css);
  });
})();
