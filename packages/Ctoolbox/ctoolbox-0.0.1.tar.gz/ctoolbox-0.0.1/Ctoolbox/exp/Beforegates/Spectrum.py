from Ctoolbox.exp.Universe import universe_circ, universe_plot
from importlib import reload
from scipy.signal import find_peaks
universe_circ = reload(universe_circ)
universe_plot = reload(universe_plot)
init_biasdelay, readout = universe_circ.init_biasdelay, universe_circ.readout

from quark.app import Recipe, s, get_data_by_rid, get_config_by_rid
s.login()

import numpy as np
import matplotlib.pyplot as plt

def circuit(qubits, if_iso, ctx=None):
    circ = init_biasdelay(qubits, if_iso, ctx)
    circ += [(('R',0),q) for q in qubits]
    circ += readout(qubits, if_iso, ctx)
    return circ

def characterize(qubits, freq_st, freq_ed, freq_points, amp, width, signal, if_iso, preview, plot):
    rcp = Recipe('spectrum', signal=signal)
    rcp.circuit = circuit
    rcp['qubits'] = tuple(qubits)
    rcp['if_iso'] = if_iso
    rcp['freq'] = np.linspace(freq_st, freq_ed, freq_points)
    for q in qubits:
        rcp[f'{q}.R.width'] = width
        rcp[f'{q}.R.amp'] = amp
        if freq_st >= 2e9:
            rcp[f'{q}.R.frequency'] = rcp['freq']
        else:
            rcp[f'{q}.R.frequency'] = rcp['freq'] + s.query(f'{q}.R.frequency')
    thistask = s.submit(rcp.export(), block=True, preview=preview, plot=plot)
    thistask.bar(interval=0.05)
    return thistask

def analyze(thistask, fignum1row=7, eachfigsize=(3,2.5), include='all', mode='max'):
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
    fig, axes = universe_plot.creat_fig(include, fignum1row=fignum1row, eachfigsize=eachfigsize)
    spectrum_info = {}
    fidx = 0
    freq_dict = {}
    for qidx, q in enumerate(qubits):
        if q not in include:
            continue
        ax = axes[fidx]
        fidx += 1        
        xaxis = result['meta']['axis']['freq'][f'${q}.R.frequency']
        intensity = np.abs(data[:,qidx]) #imag,real
        ax.plot(xaxis, intensity)
        if mode is 'max':
            qubit_freq = xaxis[np.argmax(intensity)]
            intensity_peak = np.max(intensity)
        else:
            qubit_freq = xaxis[np.argmin(intensity)]
            intensity_peak = np.min(intensity)
        freq_dict[q] = qubit_freq
        ax.plot(qubit_freq, intensity_peak, 'ro')
        # ax.legend()
        ax.set_title(q+f', {qubit_freq/1e9:.3f}GHz')  # 标题设置为qubit名称，如'Q0' 

    fig.suptitle(f'spectrum, rid={rid}', y=0.99)
    fig.tight_layout()
    # 添加点击处理器
    spectrum_info = universe_plot.add_click_handler(fig)
    # 显示图形
    plt.show()
    # 返回选中的点
    return spectrum_info, freq_dict
