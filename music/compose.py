"""Render Between Moves with FluidSynth and the TimGM6mb General MIDI bank."""
import ctypes as ct
import random
import wave
from pathlib import Path
import numpy as np

rate = 32000
beat = 60 / 76
bar = 4 * beat
rng = random.Random(28)
lib = ct.CDLL("libfluidsynth.so.3")
ptr, integer = ct.c_void_p, ct.c_int
def bind(name, result, *args):
    function = getattr(lib, name)
    function.argtypes = args
    function.restype = result
    return function

settings = bind("new_fluid_settings", ptr)()
bind("fluid_settings_setnum", integer, ptr, ct.c_char_p, ct.c_double)(settings, b"synth.sample-rate", rate)
synth = bind("new_fluid_synth", ptr, ptr)(settings)
font = bind("fluid_synth_sfload", integer, ptr, ct.c_char_p, integer)(synth, b"/usr/share/sounds/sf2/TimGM6mb.sf2", 1)
assert font >= 0
program = bind("fluid_synth_program_select", integer, ptr, integer, integer, integer, integer)
for chan, patch in enumerate([0, 32, 11]):
    program(synth, chan, font, 0, patch)
on = bind("fluid_synth_noteon", integer, ptr, integer, integer, integer)
off = bind("fluid_synth_noteoff", integer, ptr, integer, integer)
write = bind("fluid_synth_write_s16", integer, ptr, integer, ptr, integer, integer, ptr, integer, integer)
# Two eight-bar phrases. Piano answers the sparse upper melody off the beat.
changes = [
 (41,[57,60,64,67]),(38,[53,60,64,69]),(43,[58,62,65,69]),(36,[58,62,64,69]),
 (45,[55,60,64,71]),(38,[54,60,64,69]),(43,[58,62,65,69]),(36,[58,61,64,67]),
 (41,[57,62,64,67]),(46,[57,60,62,65]),(40,[55,58,62,65]),(45,[55,61,65,70]),
 (38,[53,57,60,64]),(43,[53,59,62,69]),(43,[58,62,65,69]),(36,[58,62,64,69])]
motifs = [
 [(0.67,72,1),(2,69,0.6),(2.67,67,1)],[(0,64,1.6)],[(1,65,.55),(1.67,69,.8),(3,74,.65)],[(0,72,2)],
 [(0.67,71,.8),(2,67,1.5)],[(0,66,1),(1.67,69,.9)],[(0,70,1.4),(2.67,65,.65)],[],
 [(0.67,72,.9),(2,69,.55),(2.67,74,1)],[(0,77,1.6),(2.67,74,.8)],[(1,70,.6),(1.67,67,1.3)],[(0,69,2)],
 [(0.67,65,.8),(2,64,1.5)],[(0,62,.9),(1.67,59,1)],[(0,62,1.5),(2.67,65,.75)],[(0,64,1.6)]]
events = []
def note(at, length, chan, pitch, velocity):
    events.append((at, chan, pitch, velocity))
    events.append((at+length, chan, pitch, 0))
for i, (root, chord) in enumerate(changes):
    pos=i*4
    note(pos,.95,1,root,80)
    note(pos+2,.78,1,root+7,70)
    if i%2: note(pos+3.33,.52,1,changes[(i+1)%16][0]-1,59)
    for offset, length in [(0.03,1.12),(2.67 if i%2==0 else 1.67,.75)]:
        for j,p in enumerate(chord):
            note(pos+offset+j*.012,length,0,p,rng.randint(43,54))
    for offset,p,length in motifs[i]:
        note(pos+offset+.018,length,2,p,rng.randint(61,72))
    for offset in [1.02,3.02]: note(pos+offset,.10,9,42,rng.randint(28,37))
    if i%4==3: note(pos+3.67,.08,9,42,23)
frames = round(16*bar*rate)
audio = np.zeros((frames*3,2),dtype=np.int16)
cursor=0
def render(end):
    global cursor
    if end>cursor:
        address=audio.ctypes.data+cursor*4
        write(synth,end-cursor,address,0,2,address,1,2)
        cursor=end
for repeat in range(3):
    for time,chan,pitch,vel in sorted(events):
        render(repeat*frames+round(time*beat*rate))
        if vel: on(synth,chan,pitch,vel)
        else: off(synth,chan,pitch)
render(frames*3)
loop=audio[2*frames:].astype(float)
loop*=22000/max(1,np.max(np.abs(loop)))
with wave.open(str(Path('/tmp/between-moves.wav')),'wb') as out:
    out.setparams((2,2,rate,0,'NONE',''))
    out.writeframes(loop.astype('<i2').tobytes())
