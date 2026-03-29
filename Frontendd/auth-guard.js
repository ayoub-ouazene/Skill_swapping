(function () {
    var TOKEN_KEY = 'skillswap_token';
    var path = (window.location.pathname.split('/').pop() || '').toLowerCase();
    var needAuth = ['home.html', 'profile.html', 'messages.html', 'chatbot.html'];
    if (needAuth.indexOf(path) === -1) return;
    if (!localStorage.getItem(TOKEN_KEY)) {
        window.location.replace('login.html');
    }
})();
