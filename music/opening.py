"""Render Quiet Opening, an original piano-led menu piece. Run from repo root."""
import ctypes as c
import random
import subprocess
import wave
import numpy as np
from pathlib import Path

RATE = 32000
BEAT = 60 / 82
rng = random.Random(193)
lib = c.CDLL("libfluidsynth.so.3")
P, I = c.c_void_p, c.c_int
def bind(name, ret, *args):
    f = getattr(lib, name); f.restype = ret; f.argtypes = args
    return f
settings = bind("new_fluid_settings", P)()
bind("fluid_settings_setnum", I, P, c.c_char_p, c.c_double)(settings, b"synth.sample-rate", RATE)
synth = bind("new_fluid_synth", P, P)(settings)
font = bind("fluid_synth_sfload", I, P, c.c_char_p, I)(synth, b"/usr/share/sounds/sf2/TimGM6mb.sf2", 1)
assert font >= 0
program = bind("fluid_synth_program_select", I, P, I, I, I, I)
for channel, patch in enumerate([0, 0, 48, 8]):
    program(synth, channel, font, 0, patch)
on = bind("fluid_synth_noteon", I, P, I, I, I)
off = bind("fluid_synth_noteoff", I, P, I, I)
write = bind("fluid_synth_write_s16", I, P, I, P, I, I, P, I, I)
events = []
def note(t, duration, channel, pitch, velocity):
    events.extend([(t, channel, pitch, velocity), (t+duration, channel, pitch, 0)])

# D minor, with a contrasting major-key middle; 48 bars in 4/4.
A = [(38,[57,60,64,65]),(34,[53,57,60,62]),(41,[57,60,64,67]),(36,[55,60,62,64]),
     (43,[55,58,62,65]),(34,[53,57,62,65]),(33,[55,61,64,67]),(38,[53,57,60,64])]
B = [(41,[57,60,64,67]),(36,[55,60,64,67]),(38,[57,60,64,65]),(33,[55,60,64,69]),
     (34,[57,60,62,65]),(43,[55,58,62,65]),(40,[55,58,62,64]),(33,[55,61,64,67])]
melody = [
    [(0,69,1.4),(1.75,72,.7),(2.75,76,1.1)],[(.25,74,1.5),(2.25,69,1.4)],
    [(0,72,1.0),(1.5,67,.6),(2.5,69,1.3)],[(.25,64,2.5)],
    [(0,67,.8),(1.25,70,.8),(2.5,74,1.3)],[(0,72,1.7),(2.5,69,1.3)],
    [(0,67,.75),(1,64,.8),(2.25,73,1.5)],[(.25,69,2.8)]]
for bar in range(48):
    t = bar*4
    section = "intro" if bar<4 else "theme" if bar<20 else "bridge" if bar<28 else "return" if bar<44 else "outro"
    chart = B if section=="bridge" else A
    root, chord = chart[(bar-4)%8] if section not in ("intro","outro") else A[bar%4 if section=="intro" else [4,5,6,0][bar-44]]
    final = bar==47
    strength = 46 if section in ("intro","outro") else 58
    note(t, 3.75 if final else 1.85, 0, root, strength)
    if not final:
        note(t+2,1.75,0,root+12,strength-11)
    if final:
        for p in chord: note(t+.12,3.7,0,p,46)
    else:
        pattern = [0,1,2,3,2,1,3,2] if section in ("bridge","return") else [0,1,2,3,1,2]
        for j,k in enumerate(pattern):
            note(t+j*4/len(pattern)+rng.uniform(0,.018),.43,0,chord[k],strength-10+rng.randrange(9))
    if section=="intro": phrase = [] if bar<2 else [(2.5,chord[2]+12,1.25)]
    elif section=="bridge": phrase = [(0,chord[1]+12,1.6),(2,chord[3]+12,.8),(3,chord[2]+12,.85)]
    elif section=="outro": phrase = [(0,chord[2]+12,2.9)] if not final else [(0,69,3.6)]
    else: phrase = melody[(bar-4)%8]
    for j,(offset,p,duration) in enumerate(phrase):
        note(t+offset+.025,duration,1,p,64+rng.randrange(12))
        if section=="return" and j==0 and bar%4==0: note(t+offset+.035,duration,3,p+12,27)
    if section in ("bridge","return"):
        for p in chord[:3]: note(t+.06,3.78,2,p,26 if section=="return" else 32)
frames = round((48*4*BEAT+2.8)*RATE)
audio = np.zeros((frames,2),dtype=np.int16)
cursor=0
def render(end):
    global cursor
    if end>cursor:
        address=audio.ctypes.data+cursor*4
        write(synth,end-cursor,address,0,2,address,1,2)
        cursor=end
for t,ch,p,v in sorted(events):
    render(round(t*BEAT*RATE))
    if v: on(synth,ch,p,v)
    else: off(synth,ch,p)
render(frames)
audio[-RATE:] = (audio[-RATE:]*np.linspace(1,0,RATE)[:,None]).astype(np.int16)
wav=Path("/tmp/chess-quiet-opening.wav")
with wave.open(str(wav),"wb") as out:
    out.setparams((2,2,RATE,0,"NONE","")); out.writeframes(audio.tobytes())
subprocess.run(["ffmpeg","-loglevel","error","-y","-i",str(wav),"-af","loudnorm=I=-21:TP=-2:LRA=10","-ar","48000","-c:a","libopus","-b:a","80k","-metadata","title=Quiet Opening","app/src/main/assets/opening.ogg"],check=True)
