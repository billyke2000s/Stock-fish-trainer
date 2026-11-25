'use strict';
(() => {
    const button = document.getElementById('music');
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
        if (!enabled || document.hidden || !interacted) return;
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
    });
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) { generation++; player.pause(); }
        else play();
    });
    select();
    show();
})();
