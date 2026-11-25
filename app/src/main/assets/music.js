'use strict';
(() => {
    const button = document.getElementById('music');
    let context, buffer, source;
    let enabled = localStorage.getItem('music') === 'on';
    let interaction = false;
    function show() {
        button.textContent = enabled ? '♫ Music on' : '♫ Music off';
        button.setAttribute('aria-pressed', String(enabled));
    }
    async function play() {
        if (!enabled || document.hidden || !interaction) return;
        try {
            context ||= new AudioContext();
            await context.resume();
            buffer ||= fetch('music.ogg').then(response => response.arrayBuffer()).then(bytes => context.decodeAudioData(bytes));
            const clip = await buffer;
            if (!enabled || document.hidden || source) return;
            source = context.createBufferSource();
            source.buffer = clip;
            source.loop = true;
            const gain = context.createGain();
            gain.gain.value = 0.42;
            source.connect(gain).connect(context.destination);
            source.onended = () => gain.disconnect();
            source.start();
        } catch {
            buffer = null;
            enabled = false;
            localStorage.setItem('music','off');
            show();
            button.textContent = 'Retry music';
        }
    }
    function stop() {
        if (source) { source.stop(); source.disconnect(); source = null; }
    }
    button.addEventListener('click', () => {
        interaction = true;
        enabled = !enabled;
        localStorage.setItem('music',enabled ? 'on' : 'off');
        show();
        if (enabled) play(); else stop();
    });
    document.addEventListener('click',event => {
        interaction = true;
        if (event.target !== button && !source) play();
    });
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) { if (context) context.suspend(); }
        else if (enabled && interaction) play();
    });
    show();
})();
