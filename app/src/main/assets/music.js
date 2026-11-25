'use strict';
(() => {
    const button = document.getElementById('music');
    const themeButton = document.getElementById('theme');
    const theme = new Audio('opening.ogg');
    theme.loop = true;
    theme.volume = 0.48;
    let themeEnabled = localStorage.getItem('menuMusic') !== 'off';
    const inMenu = () => !document.getElementById('lobby').hidden;
    function themeLabel() {
        themeButton.textContent = theme.paused ? '♪' : 'Ⅱ';
        themeButton.setAttribute('aria-label', theme.paused ? 'Play menu music' : 'Pause menu music');
        themeButton.title = theme.paused ? 'Play Quiet Opening' : 'Pause Quiet Opening';
        themeButton.setAttribute('aria-pressed', String(!theme.paused));
    }
    theme.onplaying = themeLabel;
    theme.onpause = themeLabel;
    function menuAudio() {
        if (inMenu() && themeEnabled && !document.hidden) theme.play().catch(themeLabel);
        else theme.pause();
    }
    themeButton.onclick = () => {
        themeEnabled = theme.paused;
        localStorage.setItem('menuMusic',themeEnabled?'on':'off');
        menuAudio();
    };
    const picker = document.getElementById('song');
    const player = new Audio();
    player.volume = 0.42;
    player.preload = 'none';
    let enabled = localStorage.getItem('music') === 'on';
    let interacted = false;
    let generation = 0;
    const saved = localStorage.getItem('song');
    if (Array.from(picker.options).some(item => item.value === saved)) picker.value = saved;
    function select() {
        generation++;
        player.src = picker.value + '.ogg';
        localStorage.setItem('song',picker.value);
    }
    function show() {
        button.textContent = enabled ? '♫ Music on' : '♫ Music off';
        button.setAttribute('aria-pressed', String(enabled));
    }
    function play() {
        if (inMenu() || !enabled || document.hidden || !interacted) return;
        const attempt = ++generation;
        player.play().catch(() => {
            if (attempt !== generation) return;
            enabled = false;
            localStorage.setItem('music','off');
            show();
            button.textContent = 'Retry music';
        });
    }
    player.addEventListener('ended', () => {
        picker.selectedIndex = (picker.selectedIndex + 1) % picker.length;
        select();
        play();
    });
    picker.onchange = () => {
        interacted = true;
        select();
        enabled = true;
        localStorage.setItem('music','on');
        show();
        play();
    };
    button.onclick = () => {
        interacted = true;
        enabled = !enabled;
        localStorage.setItem('music',enabled ? 'on' : 'off');
        show();
        if (enabled) play();
        else { generation++; player.pause(); }
    };
    document.addEventListener('click', event => {
        interacted = true;
        if (event.target !== button && player.paused) play();
        if (inMenu() && event.target !== themeButton && themeEnabled && theme.paused) menuAudio();
    });
    document.addEventListener('screenchange', () => {
        interacted = true;
        generation++;
        player.pause();
        menuAudio();
        if (!inMenu()) play();
    });
    document.addEventListener('visibilitychange', () => {
        menuAudio();
        if (document.hidden) { generation++; player.pause(); }
        else play();
    });
    select();
    show();
    menuAudio();
})();
