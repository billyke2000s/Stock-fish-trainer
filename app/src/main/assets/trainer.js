'use strict';
const el = id => document.getElementById(id);
const game = new Chess();
const glyph = {k:'♚',q:'♛',r:'♜',b:'♝',n:'♞',p:'♟'};
const openings = [['e4','e5'],['e4','c5'],['d4','d5'],['e4','c6'],['Nf3','d5'],['c4','e5'],['d4','Nf6'],['e4','e6']];
let mode;
let worker, generation = 0, human, selected, pending, best, ready, previousOpening;
function message(title, note='') {
    el('status').textContent = title;
    el('note').textContent = note;
    el('message-body').scrollTop = 0;
}
function draw() {
    const board = el('board');
    board.innerHTML = '';
    el('ranks').textContent = '';
    el('files').textContent = '';
    const targets = new Map();
    if (selected) {
        for (const move of game.moves({square:selected, verbose:true})) {
            targets.set(move.to, move.captured ? 'capture' : 'legal');
        }
    }
    for (let i=0;i<64;i++) {
        const n = human==='b' ? 63-i : i;
        const file=n%8, row=Math.floor(n/8);
        const square='abcdefgh'[file]+(8-row), piece=game.get(square);
        if (i % 8 === 0) {
            const rank = document.createElement('span');
            rank.textContent = square[1];
            el('ranks').appendChild(rank);
        }
        if (i >= 56) {
            const fileLabel = document.createElement('span');
            fileLabel.textContent = square[0];
            el('files').appendChild(fileLabel);
        }
        const button=document.createElement('button');
        button.className=['sq',(file+row)%2?'dark':'',piece?.color==='w'?'white':'',square===selected?'selected':'',targets.get(square) || ''].join(' ');
        button.textContent=piece?glyph[piece.type]+'\uFE0E':'';
        button.setAttribute('aria-label',square+(piece?' '+(piece.color==='w'?'white ':'black ')+({k:'king',q:'queen',r:'rook',b:'bishop',n:'knight',p:'pawn'})[piece.type]:'')+(targets.get(square)==='capture'?' (capture)':''));
        button.onclick=()=>tap(square);
        board.appendChild(button);
    }
    el('hint').disabled=!ready;
    el('keep').hidden=!pending || !ready;
    el('moves').textContent=game.history().map((m,i)=>i%2?m:(1+i/2)+'. '+m).join(' ');
}
function uci(m) { return m.from+m.to+(m.promotion||''); }
function object(move) {return {from:move.slice(0,2),to:move.slice(2,4),promotion:move[4]};}
function search(limit='') {
    const engine=worker;
    return new Promise(resolve=>{
        let score;
        engine.onmessage=({data})=>{
            const match=String(data).match(/ score (cp|mate) (-?\d+)/);
            if(match) score=match[1]==='cp'?Number(match[2]):Math.sign(Number(match[2]))*(30000-Math.abs(Number(match[2])));
            if(String(data).startsWith('bestmove ')) resolve({move:data.split(' ')[1],score});
        };
        engine.postMessage('position startpos moves '+game.history({verbose:true}).map(uci).join(' '));
        engine.postMessage('go depth 8'+(limit?' searchmoves '+limit:''));
    });
}
function ended() {
    if (!game.game_over()) return false;
    ready=false;
    message(game.in_checkmate()?(mode==='local'?(game.turn()==='w'?'Black wins by checkmate':'White wins by checkmate'):game.turn()===human?'Stockfish wins by checkmate':'You won by checkmate'):'Draw',
        game.in_threefold_repetition()?'The position repeated three times.':game.in_stalemate()?'Stalemate.':game.insufficient_material()?'Insufficient material.':'Start a new game to train again.');
    draw(); return true;
}
async function turn() {
    const token=generation;
    ready=false; selected=null; pending=null; draw();
    if(ended()) return;
    if(mode==='local') human=game.turn();
    if(game.turn()!==human) {
        message('Stockfish is thinking…');
        const reply=await search();
        if(token!==generation) return;
        game.move(object(reply.move)); draw();
        if(ended()) return;
    }
    if(mode==='train') {
        message('Checking the position…');
        best=await search();
    }
    if(token!==generation) return;
    ready=true;
    if(mode==='local') message((human==='w'?'White':'Black')+' to move',game.in_check()?'Your king is in check.':'Pass the phone to the next player.');
    else message(game.in_check()?'You’re in check':'Your move', 'You play '+(human==='w'?'White':'Black')+'. Tap a piece, then its destination.');
    draw();
}
async function tap(square) {
    if(!ready)return;
    if(game.get(square)?.color===human){selected=selected===square?null:square;draw();return;}
    if(!selected)return;
    const m=game.moves({square:selected,verbose:true}).find(m=>m.to===square && (!m.promotion||m.promotion===el('promo').value));
    if(!m)return;
    if(mode!=='train'){game.move(m);turn();return;}
    selected=null; pending=null;ready=false;draw();
    const token=generation;
    message('Checking your move…');
    const result=uci(m)===best.move?best:await search(uci(m));
    if(token!==generation)return;
    if(best.score-result.score>=100){
        pending=m; ready=true;
        message('Try another move',m.san+' gives up about '+(Math.abs(best.score)>20000||Math.abs(result.score)>20000?'a forced mate sequence.':((best.score-result.score)/100).toFixed(1)+' pawns of evaluation.')+' Try again or play it to see the reply.');
        draw();return;
    }
    game.move(m);turn();
}
function start(){
    generation++; worker?.terminate(); worker=null;
    game.reset(); ready=false;pending=null;selected=null;
    human=mode==='train' && Math.random()<0.5?'b':'w';
    el('hint').hidden=mode!=='train';
    if(mode==='local'){turn();return;}
    worker=new Worker('stockfish.js');
    if(mode==='train'){
    const choices=openings.filter(o=>o!==previousOpening);
    previousOpening=choices[Math.floor(Math.random()*choices.length)];
    previousOpening.forEach(m=>game.move(m));
    }
    draw();message('Starting engine…');
    worker.onerror=()=>{ready=false;message('Engine unavailable','Tap New game to restart.');draw();};
    worker.onmessage=({data})=>{if(data==='uciok'){worker.postMessage('setoption name Hash value 8');worker.postMessage('isready');}if(data==='readyok')turn();};
    worker.postMessage('uci');
}
el('keep').onclick=()=>{if(ready&&pending){game.move(pending);turn();}};
el('hint').onclick=()=>{if(ready){selected=best.move.slice(0,2);message('Look at '+selected,'Try moving this piece to '+best.move.slice(2,4)+'.');draw();}};
el('fresh').onclick=start;
function screen(menu) {
    el('lobby').hidden=!menu;
    el('match').hidden=menu;
    el('resume').hidden=!mode || game.game_over();
    document.dispatchEvent(new Event('screenchange'));
    window.scrollTo(0,0);
}
document.querySelectorAll('[data-mode]').forEach(button=>{
    button.onclick=()=>{
        mode=button.dataset.mode;
        el('mode-title').textContent=button.querySelector('b').textContent;
        document.querySelector('.sender').textContent=mode==='local'?'Game': 'Stockfish';
        screen(false);
        start();
    };
});
el('resume').onclick=()=>screen(false);
el('menu').onclick=()=>screen(true);
