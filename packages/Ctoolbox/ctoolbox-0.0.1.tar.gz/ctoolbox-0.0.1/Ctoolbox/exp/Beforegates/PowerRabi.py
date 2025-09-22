from Ctoolbox.exp.Universe import universe_circ, universe_plot
from importlib import reload
universe_circ = reload(universe_circ)
universe_plot = reload(universe_plot)
init_biasdelay, readout = universe_circ.init_biasdelay, universe_circ.readout

from quark.app import Recipe, s, get_data_by_rid, get_config_by_rid
s.login()

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema


def circuit(qubits, if_iso, ctx=None):
    circ = init_biasdelay(qubits, if_iso, ctx)
    circ += [(('R',0),q) for q in qubits]*2
    circ += readout(qubits, if_iso, ctx)
    return circ

def characterize(qubits, amp_st, amp_ed, amp_points, signal, if_iso, plot):
    rcp = Recipe('PowerRabi', signal=signal)
    rcp.circuit = circuit
    rcp['qubits'] = tuple(qubits)
    rcp['if_iso'] = if_iso
    rcp['amp'] = np.linspace(amp_st, amp_ed, amp_points,)
    for q in qubits:
        if amp_ed > 1:
            rcp[f'{q}.R.amp'] = rcp['amp'] * s.query(f'{q}.R.amp')
        else:
            rcp[f'{q}.R.amp'] = rcp['amp'] 
    thistask = s.submit(rcp.export(), block=True, preview=[], plot=plot)
    thistask.bar(interval=0.05)
    return thistask

def analyze(thistask, fignum1row=7, eachfigsize=(3,2.5), include='all', g_or_l='greater', order=25, deg=9):
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
    amp_info = {}
    fidx = 0
    for qidx, q in enumerate(qubits):
        if q not in include:
            continue
        ax = axes[fidx]
        fidx += 1
        ax.set_title(q)
        xaxis = result['meta']['axis']['amp'][f'${q}.R.amp']
        thisdata = np.abs(data[:,qidx])
        if xaxis[-1] > 1:
            cutidx = np.argmin(np.abs(xaxis-1))
            xaxis = xaxis[:cutidx]
            thisdata = thisdata[:cutidx]
        ax.plot(xaxis, thisdata)
        try:
            pulse_amp, pipulse_value, x, y_fit = fit_Rabi(xaxis, thisdata,g_or_l,order=order,deg=deg)
            ax.plot(x,y_fit)
            ax.plot(pulse_amp,pipulse_value,'ro',ms=4)
            amp_info[q] = pulse_amp
        except:
            print(f'failed to fitting {q}')
    fig.suptitle(f'PowerRabi, rid={rid}', y=0.99)
    fig.tight_layout()
    click_info = universe_plot.add_click_handler(fig)
    plt.show()
    return amp_info, click_info
        
def fit_Rabi(x,y,g_or_l,order=10,deg=15):
    popt = np.polyfit(x,y,deg=deg)
    x_fit = np.linspace(x[0],x[-1],1001)
    y_fit = np.polyval(popt,x_fit)
    if g_or_l == 'greater':
        index = argrelextrema(y_fit, np.greater,order = order)[0][0]
    else:
        index = argrelextrema(y_fit, np.less,order = order)[0][0]
    pulse_amp = x_fit[index]
    pipulse_value = y_fit[index]
    return pulse_amp, pipulse_value, x_fit, y_fit
