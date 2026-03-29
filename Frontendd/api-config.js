/**
 * Sets window.SKILLSWAP_API_BASE for API calls.
 * - Production (e.g. Render): same host as the site → '' (relative URLs).
 * - Local API on :8000 with pages on :8000 → ''.
 * - VS Code Live Server / other port → http://127.0.0.1:8000
 * Override before this script: <script>window.SKILLSWAP_API_BASE = 'https://api.example.com';</script>
 */
(function () {
    if (typeof window === 'undefined') return;
    if (typeof window.SKILLSWAP_API_BASE !== 'undefined') return;
    var loc = window.location;
    if (loc.protocol === 'file:') {
        window.SKILLSWAP_API_BASE = 'http://127.0.0.1:8000';
        return;
    }
    var h = loc.hostname;
    var p = String(loc.port || '');
    if (h === 'localhost' || h === '127.0.0.1') {
        window.SKILLSWAP_API_BASE = p === '8000' ? '' : 'http://127.0.0.1:8000';
        return;
    }
    window.SKILLSWAP_API_BASE = '';
})();
