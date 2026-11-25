"""Run python3 music/compose.py between|window|amber from the repository root."""
import sys
import subprocess
import ctypes as ct
import random
import wave
from pathlib import Path
import numpy as np

rate = 32000
song = sys.argv[1]
bpm, meter, lead, answer, title = {
    "between": (76,4,11,0,"Between Moves"),
    "window": (108,3,0,24,"Window Seat"),
    "amber": (84,4,26,11,"Amber After Dark"),
}[song]
beat = 60 / bpm
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
for chan, patch in enumerate([0, 32, lead, answer]):
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
# Eight-bar themes in concert pitch. Window Seat is a waltz in Eb;
# Amber is a guitar-led cool-jazz quartet in A. Each has its own middle eight.
if song == 'window':
    changes = [(39,[55,58,62,65]),(36,[55,58,62,63]),(41,[56,60,63,67]),(46,[56,60,62,67]),
               (43,[53,58,62,65]),(36,[52,58,62,67]),(41,[56,60,63,67]),(46,[56,59,62,65])]
    pitches = [[67,70,72],[74,70],[68,67,65],[62],[65,70,74],[76,72],[68,65,63],[62,65]]
elif song == 'amber':
    changes = [(45,[56,59,61,64]),(42,[52,57,61,68]),(47,[54,57,61,62]),(40,[56,59,62,66]),
               (37,[52,56,59,63]),(42,[52,58,61,65]),(47,[54,57,61,62]),(40,[56,59,62,65])]
    pitches = [[64,61,59],[57,61],[66,69,68],[64,62],[63,64,68],[70,66],[62,61,57],[59]]
if song != 'between':
    motifs = []
    for i, phrase in enumerate(pitches):
        offsets = ([.5,1.5,2.25] if i%2==0 else [0,1.75,2.4]) if meter==3 else ([.67,2,2.67] if i%2==0 else [0,2.67,3.33])
        motifs.append([(t,p,min((offsets[k+1] if k+1<len(phrase) else meter)-t-.09,1.8)) for k,(t,p) in enumerate(zip(offsets,phrase))])
bridge_charts = {
    'between': [(46,[57,62,65,69]),(39,[55,61,65,68]),(44,[55,60,63,67]),(37,[53,59,63,66]),
                (43,[53,58,62,69]),(38,[54,60,64,69]),(43,[58,62,65,69]),(36,[58,61,64,67])],
    'window': [(44,[55,60,63,67]),(37,[53,59,63,68]),(42,[53,58,61,65]),(47,[51,57,61,66]),
               (40,[56,59,63,66]),(45,[55,61,64,69]),(41,[56,60,63,67]),(46,[56,62,65,69])],
    'amber': [(38,[54,57,61,64]),(43,[53,59,62,67]),(36,[52,55,59,62]),(41,[51,57,60,65]),
              (46,[53,57,62,65]),(39,[55,61,65,68]),(47,[54,57,61,62]),(40,[56,59,62,65])]
}
events = []
def note(at,length,chan,pitch,velocity):
    events.extend([(at,chan,pitch,velocity),(at+length,chan,pitch,0)])

sections = [('intro',4),('theme',16),('bridge',8),('solo',16),('return',16),('coda',4)]
if song=='window': sections.insert(4,('bridge',8))
start = 0
for section, bars in sections:
    for i in range(bars):
        pos=(start+i)*meter
        chart=bridge_charts[song] if section=='bridge' else changes
        root,chord=chart[i%len(chart)]
        if section=='coda':
            root,chord=changes[[0, min(2,len(changes)-1),len(changes)-1,0][i]]
        last=section=='coda' and i==bars-1
        voice=3 if section=='solo' else 2
        note(pos,meter-.15 if last else 1.12,1,root,67 if section=='intro' else 79)
        if not last and section!='intro':
            note(pos+meter-1,.76,1,root+7,65)
            if section=='solo' and meter==4: note(pos+1,.8,1,root+4,57)
        accents=[.03] if section in ('intro','coda') else ([1.04,2.18] if meter==3 else [.035,2.66])
        for offbeat in accents:
            for j,p in enumerate(chord):
                note(pos+offbeat+j*.016,meter-.3 if last else min(1.18,meter-offbeat-.1),0,p,rng.randint(40,54))
        phrase=motifs[i%len(motifs)]
        if section in ('bridge','solo'):
            offsets=([.04,1.55,2.28] if meter==3 else [.66,1.66,2.98])
            contour=([3,2,0],[1,3,2],[0,1,3],[2,0,1])[i%4]
            phrase=[(t,chord[k]+(12 if section=='bridge' or i%4==2 else 0),.55 if j<2 else meter-t-.12) for j,(t,k) in enumerate(zip(offsets,contour))]
            if i%4==3: phrase=phrase[:1]
        if section=='intro': phrase=[] if i<2 else [(meter-1,chord[2]+12,.83)]
        if section=='return' and i%4==3: phrase=phrase+[(meter-.47,chord[1]+12,.36)]
        if section=='coda': phrase=[(.12,chord[-1]+(0 if last else 12),meter-.4)]
        for t,p,d in phrase: note(pos+t,d,voice,p,rng.randint(61,74))
        if section not in ('intro','coda'):
            for t in ([1,2] if meter==3 else [1,3]): note(pos+t+.025,.08,9,42,rng.randint(22,36))
    start+=bars
frames=round((start*meter*beat+2.8)*rate)
audio=np.zeros((frames,2),dtype=np.int16)
cursor=0
def render(end):
    global cursor
    if end>cursor:
        address=audio.ctypes.data+cursor*4
        write(synth,end-cursor,address,0,2,address,1,2)
        cursor=end
for t,c,p,v in sorted(events):
    render(round(t*beat*rate))
    if v: on(synth,c,p,v)
    else: off(synth,c,p)
render(frames)
audio[-rate:]=(audio[-rate:]*np.linspace(1,0,rate)[:,None]).astype(np.int16)
wav=Path('/tmp')/(song+'.wav')
with wave.open(str(wav),'wb') as out:
    out.setparams((2,2,rate,0,'NONE',''))
    out.writeframes(audio.tobytes())
subprocess.run(['ffmpeg','-loglevel','error','-y','-i',str(wav),'-af','loudnorm=I=-20:TP=-2:LRA=10','-ar','48000','-c:a','libopus','-b:a','40k','-metadata','title='+title,'app/src/main/assets/'+song+'.ogg'],check=True)
