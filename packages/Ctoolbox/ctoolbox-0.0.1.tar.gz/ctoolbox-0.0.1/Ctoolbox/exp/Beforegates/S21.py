# created by HJX, @20250826
from Ctoolbox.exp.Universe import universe_circ, universe_plot
from importlib import reload
universe_circ = reload(universe_circ)
universe_plot = reload(universe_plot)
init_biasdelay, readout = universe_circ.init_biasdelay, universe_circ.readout

from quark.app import Recipe, s, get_data_by_rid, get_config_by_rid
s.login()

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.ndimage import gaussian_filter


def circuit(qubits, if_iso, ctx=None):
    circ = init_biasdelay(qubits, if_iso, ctx)
    circ += readout(qubits, if_iso, ctx)
    return circ


def characterize(qubits, freq_st, freq_ed, freq_points, signal, if_iso, plot):
    rcp = Recipe('S21', signal=signal)
    rcp.circuit = circuit
    rcp['qubits'] = tuple(qubits)
    rcp['if_iso'] = if_iso
    rcp['freq'] = np.linspace(freq_st, freq_ed, freq_points)
    for q in qubits:
        if freq_st >= 6e9:
            rcp[f'{q}.Measure.frequency'] = rcp['freq']
        else:
            rcp[f'{q}.Measure.frequency'] = rcp['freq'] + s.query(f'{q}.Measure.frequency')
    thistask = s.submit(rcp.export(), block=True, preview=[], plot=plot)
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
    fr_info = {}
    fidx = 0
    for qidx, q in enumerate(qubits):
        if q not in include:
            continue
        ax = axes[fidx]
        fidx +=1
        ax.set_title(q)
        xaxis = result['meta']['axis']['freq'][f'${q}.Measure.frequency']
        ax.plot(xaxis, np.abs(data[:,qidx]))
        ################ linear cavity fit
        # try:
        #     para,fit_y,fit_y_abs = fit_resonator(xaxis, np.abs(data[:,qidx]))
        #     ax.plot(xaxis,fit_y_abs)
        #     fr_info[q] = xaxis[np.argmin(fit_y_abs)]
        #     ax.plot([fr_info[q]]*2,[np.min(fit_y_abs),np.max(fit_y_abs)],'r')
        # except:
        #     pass
        ################ gaussian_filter
        smoothed_signal = gaussian_filter(np.abs(data[:,qidx]), sigma=1)  # sigma为高斯核标准差
        ax.plot(xaxis,smoothed_signal)
        fr_info[q] = xaxis[np.argmin(smoothed_signal)]
        ax.plot([fr_info[q]]*2,[np.min(smoothed_signal),np.max(smoothed_signal)],'r')

    fig.suptitle(f'S21, rid={rid}',y=0.99)
    fig.tight_layout()
    return fr_info


def plot_overview(thistask, qnum1row=7,fignum1row=7, eachfigsize=(3,2.5)):
    try:
        result = thistask.result()
        rid = thistask.rid
    except:
        result = get_data_by_rid(thistask)
        rid = thistask
    signal = result['meta']['other']['signal']
    qubits = result['meta']['other']['qubits']
    data = result['data'][signal]
    qlens = len(qubits)
    thiscfg = get_config_by_rid(rid)
    fig, axes = universe_plot.creat_fig(qubits,fignum1row=fignum1row, eachfigsize=eachfigsize)
    for qidx, q in enumerate(qubits):
        ax = axes[qidx]
        xaxis = result['meta']['axis']['freq'][f'${q}.Measure.frequency']
        ax.plot(xaxis, np.abs(data[:,qidx]))
        ax.set_title(q)
        qnum = int(q[1:])
        for Q in [f'Q{i}' for i in range(qnum,qnum+qnum1row)]:
            fr = thiscfg[Q]['Measure']['frequency']
            ax.plot([fr]*2,[np.min(np.abs(data[:,qidx])),np.max(np.abs(data[:,qidx]))],'r',alpha=0.4,linewidth=0.5)
    fig.suptitle(f'S21, rid={rid}',y=0.99)
    fig.tight_layout()
    return


def linear_resonator_abs(f, f_0, Q, Q_e_real, Q_e_imag,amp,offset):
    Q_e = Q_e_real + 1j*Q_e_imag
    return np.abs(amp*(1 - (Q * Q_e**-1 / (1 + 2j * Q * (f - f_0) / f_0)))+offset)


def linear_resonator(f, f_0, Q, Q_e_real, Q_e_imag,amp,offset):
    Q_e = Q_e_real + 1j*Q_e_imag
    return amp*(1 - (Q * Q_e**-1 / (1 + 2j * Q * (f - f_0) / f_0)))+offset


def guess_resonator(f,data):
    fmin = f.min()
    fmax = f.max()
    argmin_s21 = np.abs(data).argmin()
    f_0_guess = f[argmin_s21] # guess that the resonance is the lowest point
    Q_min = 0.1 * (f_0_guess/(fmax-fmin)) # assume the user isn't trying to fit just a small part of a resonance curve
    delta_f = np.diff(f) # assume f is sorted
    min_delta_f = delta_f[delta_f > 0].min()
    Q_max = f_0_guess/min_delta_f # assume data actually samples the resonance reasonably
    Q_guess = np.sqrt(Q_min*Q_max) # geometric mean, why not?
    amp_guess = np.max(np.abs(data))-np.min(np.abs(data))
    Q_e_real_guess = Q_guess/(np.max(np.abs(data))-np.abs(data[argmin_s21]))*amp_guess
    offset_guess = np.min(np.abs(data))
    params_guess = [f_0_guess,Q_guess,Q_e_real_guess,0,amp_guess,offset_guess]
    return params_guess


def fit_resonator(x,y):
    para = curve_fit(linear_resonator_abs,x,np.abs(y),p0 =guess_resonator(x,y),maxfev=10000)[0]
    fit_y_abs = linear_resonator_abs(x,*para)
    fit_y = linear_resonator(x,*para)
    return para,fit_y,fit_y_abs
    