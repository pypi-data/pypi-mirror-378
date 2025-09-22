from Ctoolbox.exp.Universe import universe_circ, universe_plot
from importlib import reload
universe_circ = reload(universe_circ)
universe_plot = reload(universe_plot)
init_biasdelay, readout = universe_circ.init_biasdelay, universe_circ.readout

from quark.app import Recipe, s, get_data_by_rid, get_config_by_rid
s.login()

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from scipy.optimize import curve_fit
from scipy.fft import fft, fftfreq

def circuit(qubits,if_iso, delay, ctx=None):
    circ = init_biasdelay(qubits, if_iso, ctx)
    circ += [(('R',0),q) for q in qubits]*2
    circ += [(('Delay',delay),q) for q in qubits]
    circ += readout(qubits, if_iso, ctx)
    return circ

def characterize(qubits, delay_st, delay_ed, delay_points, signal, if_iso):
    rcp = Recipe('T1', signal=signal)
    rcp.circuit = circuit
    rcp['qubits'] = tuple(qubits)
    rcp['if_iso'] = if_iso
    rcp['delay'] = np.linspace(delay_st, delay_ed, delay_points)
    thistask = s.submit(rcp.export(), block=True, preview=[], plot=False)
    thistask.bar(interval=0.05)
    return thistask

def analyze(thistask, fignum1row=7, eachfigsize=(3,2.5), include='all'):
    try:
        result = thistask.result()
        rid = thistask.rid
    except:
        result = get_data_by_rid(thistask)
        rid = thistask
    signal = result['meta']['other']['signal']
    qubits = result['meta']['other']['qubits']
    data = result['data'][signal]
    if include == 'all':
        include = qubits
    fig, axes = universe_plot.creat_fig(include,fignum1row=fignum1row, eachfigsize=eachfigsize)
    T1_info = {}
    fidx = 0
    for qidx, q in enumerate(qubits):
        if q not in include:
            continue
        ax = axes[fidx]
        fidx += 1
        ax.set_title(q)
        xaxis = result['meta']['axis']['delay'][f'def']
        thisdata = np.abs(data[:,qidx])
        ax.plot(xaxis, thisdata)
        para, y_fit = fit_T1(xaxis,thisdata)
        ax.plot(xaxis, y_fit)
        T1_info[q] = np.round(para[0]*1e6,2)
        ax.set_title(q + f' {T1_info[q]}')
    fig.suptitle(f'T1, rid={rid}',y=0.99)
    fig.tight_layout()
    return T1_info

def T1_func(t,T1):
    return np.exp(-t/T1)

def fit_T1(xdata,ydata):
    p0= [40e-6]
    para = curve_fit(T1_func,xdata,ydata,p0=p0,maxfev=10000)[0]
    y_fit = T1_func(xdata,*para)
    return para, y_fit
