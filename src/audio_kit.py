# Copia del kit de síntesis de ANIMACION-2D (src/audio/kit.py); en el 3D se usa sin tocar el original.
"""Kit de síntesis compartido (instrumentos, voces de ave, foley). Lo usan audio_episodio.py (EP001) y
audio_director.py (capítulos generados). rng es compartido: el orden de las llamadas define el resultado."""
import numpy as np
from scipy.signal import butter, lfilter, fftconvolve
SR=44100
rng=np.random.default_rng(21)
def db(x):return 10**(x/20)
def lp(x,f,o=2):b,a=butter(o,min(f,SR/2-100)/(SR/2),'low');return lfilter(b,a,x)
def hp(x,f,o=2):b,a=butter(o,f/(SR/2),'high');return lfilter(b,a,x)
def bp(x,f1,f2,o=2):b,a=butter(o,[f1/(SR/2),min(f2,SR/2-200)/(SR/2)],'band');return lfilter(b,a,x)
def tt(d):return np.arange(int(SR*d))/SR
def white(d):return rng.standard_normal(int(SR*d)) if np.isscalar(d) else rng.standard_normal(d)
def pink(n):
    w=rng.standard_normal(n)
    b=[0.049922035,-0.095993537,0.050612699,-0.004408786];a=[1,-2.494956002,2.017265875,-0.522189400]
    p=lfilter(b,a,w);return p/np.std(p)
def brown(n):
    x=np.cumsum(rng.standard_normal(n));x-=lp(x,20,1);return x/np.std(x)
def NS(d,kind='pink'):
    n=int(SR*d);return pink(n) if kind=='pink' else brown(n)
def hann(n):return np.hanning(n)
def fade(x,a=.01,r=.03):
    n=len(x);e=np.ones(n);na=int(a*SR);nr=int(r*SR)
    if na>0:e[:na]=np.linspace(0,1,na)
    if nr>0:e[-nr:]=np.linspace(1,0,nr)
    return x*e
NOTE={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
def fq(n):return 440*2**((NOTE[n[0]]-9)/12+(int(n[-1])-4))
# ---------- instrumentos ----------
def piano(f,d=1.6,g=.2):
    t=tt(d);s=0
    for k,a in enumerate([1,.5,.25,.12,.06,.03],1):
        fk=k*f*np.sqrt(1+.0004*k*k);s=s+a*np.sin(2*np.pi*fk*t)*np.exp(-t/(1.8/k))
    ham=lp(white(.02),800)*np.exp(-tt(.02)*200)*.15
    s[:len(ham)]+=ham
    s=lp(s,2500,1)*np.minimum(1,t/.006);return s*g*np.exp(-t*.3)
def mbox(f,d=1.8,g=.1):
    t=tt(d);s=np.sin(2*np.pi*f*t)*np.exp(-t/.9)+.22*np.sin(2*np.pi*3.2*f*t)*np.exp(-t/.5)+.07*np.sin(2*np.pi*5.4*f*t)*np.exp(-t/.25)
    return lp(s,4000)*np.minimum(1,t/.008)*g
def pluckn(f,d=.5,g=.1):
    t=tt(d);s=np.sin(2*np.pi*f*t)+.25*np.sin(2*np.pi*2*f*t)*np.exp(-t*14)
    return lp(s,1300)*np.exp(-t*8)*np.minimum(1,t/.008)*g
def padn(freqs,d,g=.05):
    t=tt(d);s=0
    for f in freqs:
        for c in(-4,0,4):s=s+np.sin(2*np.pi*f*2**(c/1200)*t+rng.random()*6)
    s=lp(s,900)/(len(freqs)*3)
    return s*np.minimum(1,t/1.2)*np.minimum(1,(d-t)/(d*.4))*g
# ---------- voces de ave ----------
def resonate(x,f0,bw=.15):return bp(x,f0*(1-bw),f0*(1+bw),2)
def syl(f0,d,seed=0):
    r=np.random.default_rng(seed);t=tt(d)
    semi=3*(1-np.exp(-t/.02))-2*(t/d)**1.6+r.uniform(-.6,.6)
    jit=lp(rng.standard_normal(len(t)),30,1);jit=jit/np.std(jit)*.003
    vib=.004*np.sin(2*np.pi*6*t)*np.clip((t-.06)/.05,0,1)
    f=f0*2**(semi/12)*(1+jit+vib);ph=2*np.pi*np.cumsum(f)/SR
    s=np.sin(ph)+.12*np.sin(2*ph)+.03*np.sin(3*ph)
    s=.55*s+.45*resonate(s,f0*1.1)
    breath=bp(pink(len(t)),1000,3000,2)*.1
    env=np.minimum(1,.5-.5*np.cos(np.pi*np.minimum(1,t/.02)))*np.exp(-t/(.1+.0*d))
    env=env*np.minimum(1,(d-t)/.02)
    out=(s+breath)*env;return out/ (np.max(np.abs(out))+1e-9)
def phrase(f0,n=2,g=.1,seed=0):
    parts=[];r=np.random.default_rng(seed)
    for k in range(n):
        d=r.uniform(.09,.16);parts.append(syl(f0*2**(r.uniform(-1,1)/12),d,seed+k)*g);parts.append(np.zeros(int(SR*r.uniform(.06,.12))))
    return np.concatenate(parts)
# ---------- foley ----------
def step(g=.1):
    d=.25;t=tt(d);s=sum(a*np.sin(2*np.pi*f*t)*np.exp(-t/tau) for f,tau,a in((180,.06,1),(410,.035,.5),(760,.02,.25)))
    n=lp(white(d),1200)*np.exp(-t/.008)*.5;return (s+n)*np.minimum(1,t/.002)*g
def flapf(g=.05):
    d=.07;n=bp(pink(int(SR*d)),120,700)*np.sin(np.pi*np.arange(int(SR*d))/(SR*d))**2;return n*g*3
def splash(g=.2,big=1.0):
    d=1.0;t=tt(d);n=bp(brown(len(t)),200,2500)*np.minimum(1,t/.015)*np.exp(-t/(.25*big))
    out=n*g
    for k in range(int(6+4*big)):
        t0=rng.uniform(.03,.45);dd=.05;tt2=tt(dd);f=rng.uniform(800,1800)*(1-.5*tt2/dd)
        drop=np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*tt2/dd)*g*.12;i=int(t0*SR);out[i:i+len(drop)]+=drop
    out+=lp(brown(len(t)),400)*np.exp(-t/.4)*g*.5;return out
def mud(g=.2):
    d=.5;t=tt(d);n=lp(brown(len(t)),500)*np.minimum(1,t/.02)*np.exp(-t/.12)*g
    for t0 in(.15,.27,.4):
        dd=.03;t2=tt(dd);p=np.sin(2*np.pi*np.cumsum(150-60*t2/dd)/SR)*np.sin(np.pi*t2/dd)*g*.25;i=int(t0*SR);n[i:i+len(p)]+=p
    return n
def rubf(d,g=.03):
    n=bp(pink(int(SR*d)),300,2500)*hann(int(SR*d));return n*g
def creakm(d,g=.03,f0=150,f1=240):
    t=tt(d);f=f0+(f1-f0)*(t/d);ph=2*np.pi*np.cumsum(f)/SR
    s=sum(a*np.sin(k*ph+rng.random()*6) for k,a in((1,1),(2,.5),(3,.3)))
    return lp(s,700)*(.6+.4*np.sin(2*np.pi*7*t))*np.minimum(1,t/.2)*np.minimum(1,(d-t)/.15)*g
def whoosh(d,g=.05,f1=200,f2=1200):
    n=bp(pink(int(SR*d)),f1,f2)*hann(int(SR*d))**1.6;return n*g*3
def dropb(g=.03):
    d=.07;t=tt(d);f=450+700*t/d;return np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*t/d)*g
