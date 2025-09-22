from Ctoolbox.exp.Universe import universe_circ, universe_plot
from importlib import reload
universe_circ = reload(universe_circ)
universe_plot = reload(universe_plot)
init_biasdelay, readout = universe_circ.init_biasdelay, universe_circ.readout

from quark.app import Recipe, s, get_data_by_rid, get_config_by_rid
s.login()

import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy.fftpack import fft
from scipy.optimize import curve_fit


def circuit(qubits, if_iso, rotate, delay, echonum, ctx=None):
    phase = rotate * delay * 2 * np.pi
    circ = init_biasdelay(qubits, if_iso, ctx)
    circ += [(('R',0),q) for q in qubits]
    if echonum == 0:
        subcirc = [(('Delay',delay),q) for q in qubits]
    else:
        subcirc = [(('Delay',delay/(echonum*2)),q) for q in qubits]
        subcirc += [(('R',np.pi/2),q) for q in qubits]*2
        subcirc += [(('Delay',delay/(echonum*2)),q) for q in qubits]
        subcirc = subcirc * echonum
    circ += subcirc
    circ += [(('R',phase),q) for q in qubits]
    circ += readout(qubits, if_iso, ctx)
    return circ

def characterize(qubits,delayst,delayed,delaypoints,rotate,echonum,signal,if_iso, preview, plot):
    rcp = Recipe('Ramsey', signal=signal)
    rcp.circuit = circuit
    rcp['qubits'] = tuple(qubits)
    rcp['if_iso'] = if_iso
    rcp['rotate'] = rotate
    rcp['delay'] = np.linspace(delayst,delayed,delaypoints)
    rcp['echonum'] = echonum
    thistask = s.submit(rcp.export(), block=True, preview=preview, plot=plot)
    thistask.bar(interval=0.05)
    return thistask

def analyze(thistask, fignum1row=7, eachfigsize=(3,2.5), include='all', realT1=False):
    try:
        result = thistask.result()
        rid = thistask.rid
    except:
        result = get_data_by_rid(thistask)
        rid = thistask
    cfg = get_config_by_rid(rid)
    signal = result['meta']['other']['signal']
    qubits = result['meta']['other']['qubits']
    echonum = result['meta']['other']['echonum']
    data = result['data'][signal]
    if include == 'all':
        include = qubits
    fig, axes = universe_plot.creat_fig(include,fignum1row=fignum1row, eachfigsize=eachfigsize)
    freq_info = {}
    Delta_info = {}
    T2_info = {}
    fidx = 0
    for qidx, q in enumerate(qubits):
        if q not in include:
            continue
        ax = axes[fidx]
        fidx += 1
        xaxis = result['meta']['axis']['delay'][f'def']
        rotate = result['meta']['other'][f'rotate']
        thisdata = np.abs(data[:,qidx])
        ax.plot(xaxis, thisdata)
        try:
            if realT1:
                T1 = cfg[q]['params']['T1']
                popt,x,y_fit = fit_Ramsey(xaxis, thisdata, T1=T1)
            else:
                popt,x,y_fit = fit_Ramsey(xaxis, thisdata)
            ax.plot(x,y_fit,alpha=0.6)
            Delta_info[q] = popt[2]
            ori_freq = cfg[q]['R']['frequency']
            set_freq = ori_freq+(popt[2]-rotate)
            freq_info[q] = set_freq
            T2_info[q] = np.round(popt[1]*1e6,2)
            # ax.set_title(q + ' ' + str(np.round(popt[1]*1e6,2))) #T2R
            ax.set_title(q + ' ' + str(np.round((popt[2]-rotate)/1e6,3))) #freq
        except:
            print(f'failed to fitting {q}')
    fig.suptitle(f'Ramsey {echonum=}, rid={rid}',y=0.99)
    fig.tight_layout()
    return freq_info,Delta_info,T2_info

def Ramsey_func(t,A,T2r,Delta,phi,B,T1):
    return A*np.exp(-t/2/T1-t**2/T2r**2)*np.cos(2*np.pi*Delta*t+phi)+B

def fit_Ramsey(xdata,ydata,T1=500e-6):
    fftnum = 10001
    x = np.linspace(xdata[0],xdata[-1],fftnum)
    f = interpolate.interp1d(xdata,ydata)
    y = f(x)
    yf = np.abs(fft(y))/len(y)
    xf = np.linspace(0,1/(x[1]-x[0]),fftnum)
    freq = xf[np.argmax(yf[1:int(len(xf)/2)])+1]
    phi0 = 0 if y[0]>np.mean(y) else np.pi
    p0 = [(np.max(y)-np.min(y))/2.0,10e-6,freq,phi0,(np.max(y)+np.max(y))/2.0]
    popt = curve_fit(lambda t,A,T2r,Delta,phi,B,:Ramsey_func(t,A,T2r,Delta,phi,B,T1),x,y,p0,maxfev=100000)[0]
    A, T2star, Delta, phi, B = popt
    y_fit = Ramsey_func(x, A, T2star, Delta, phi, B, T1)
    return popt,x,y_fit
