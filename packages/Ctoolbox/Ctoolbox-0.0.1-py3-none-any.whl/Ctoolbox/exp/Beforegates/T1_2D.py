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

def circuit(qubits, if_iso,flux, delay, ctx=None):
    circ = init_biasdelay(qubits, if_iso, ctx)
    circ.extend([(('R',0),q) for q in qubits])
    circ.extend([(('R',0),q) for q in qubits])

    circ.extend([(("setBias", 'flux', flux), q) for q in qubits])
    circ.extend([(('Delay',delay),q) for q in qubits])
    circ.extend([(("setBias", 'flux', ctx.query(f'{q}.caliinfo.idlebias')), q) for q in qubits])
    
    circ += readout(qubits, if_iso, ctx)
    return circ

def characterize(qubits, flux_st, flux_ed, flux_points, delay_st, delay_ed, delay_points, signal, if_iso):
    rcp = Recipe('rabivstime', signal=signal)
    rcp.circuit = circuit
    rcp['qubits'] = tuple(qubits)
    rcp['if_iso'] = if_iso
    rcp['flux'] = np.linspace(flux_st, flux_ed, flux_points)
    rcp['delay'] = np.linspace(delay_st, delay_ed, delay_points)

    thistask = s.submit(rcp.export(), block=True, preview=[], plot=False)
    thistask.bar(interval=0.05)
    return thistask

def analyze(thistask_rid, rid=None, fignum1row=7, eachfigsize=(3,2.5), include='all'):
    try:
        result = thistask_rid.result()
        rid = thistask_rid.rid
    except:
        result = get_data_by_rid(thistask_rid)
        rid = thistask_rid
    signal = result['meta']['other']['signal']
    qubits = result['meta']['other']['qubits']
    data = result['data'][signal]
    if include == 'all':
        include = qubits
    fig, axes = universe_plot.creat_fig(include,fignum1row=fignum1row, eachfigsize=eachfigsize)
    fr_info = {}
    fidx = 0
    for qidx, q in enumerate(qubits):
        if q not in include:
            continue
        
        ax = axes[fidx]
        fidx += 1
        ax.set_title(q)
        xaxis = result['meta']['axis']['delay'][f'def']*1e6
        yaxis = result['meta']['axis']['flux'][f'def']
        extent = universe_plot.get_extent(yaxis, xaxis)
        ax.imshow(np.abs(data[:,:,qidx]).T,extent=extent,origin='lower',interpolation='none',aspect='auto')
        T1_List = fit_t1_2D(xaxis,data[:,:,qidx],axis=0,signal='population')
        # print(yaxis,T1_List)
        ax.plot(yaxis,T1_List,'or',markersize=2)
        ax.set_ylim(0,150)
        ax.set_title(f'{q}')

    fig.suptitle(f'T1, rid={rid}',y=0.99)
    fig.tight_layout()
    return fr_info

# 定义T1拟合模型
def t1_model_iq(ti, t1, s0, b):
    return s0 * np.exp(-ti / t1) + b

def t1_model_pop(ti, t1, s0):
    return s0 * np.exp(-ti / t1)

def fit_t1(ti, y, signal='iq_avg'):
    t1_guess = -1/np.polyfit(ti, y-np.min(y),1)[0]
    s0_guess = np.max(abs(y))
    b_guess = np.min(abs(y))
    if t1_guess<0:
        t1_guess = 20

    if signal=='iq_avg':
        initial_guess = [t1_guess, s0_guess, b_guess]
        popt, pcov = curve_fit(t1_model_iq, ti, y, p0=initial_guess, 
                                bounds=([0, -np.inf,-np.inf], [np.inf, np.inf,np.inf]))  # 确保参数为正值
        return popt, t1_model_iq
    else:
        initial_guess = [t1_guess,s0_guess]
        popt, pcov = curve_fit(t1_model_pop, ti, y, p0=initial_guess, 
                                bounds=([0, -np.inf], [np.inf, np.inf]))  # 确保参数为正值
        return popt, t1_model_pop
    
def fit_t1_2D(t,data,axis=0,signal='population'):
    # print(data.shape)
    num = data.shape[axis]
    T1_List = []
    for i in range(num):
        if axis==0:
            y = data[i,:]
        else:
            y = data[:,i]
        # print(t.shape,y.shape)
        para,func = fit_t1(t, np.abs(y), signal)
        T1_List.append(para[0])

    return T1_List

