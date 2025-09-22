from Ctoolbox.exp.Universe import universe_circ, universe_plot
from importlib import reload
universe_circ = reload(universe_circ)
universe_plot = reload(universe_plot)
init_biasdelay, readout = universe_circ.init_biasdelay, universe_circ.readout

from quark.app import Recipe, s, get_data_by_rid, get_config_by_rid
s.login()

import numpy as np
import matplotlib.pyplot as plt

def circuit(qubits, if_iso, ctx=None):
    print(qubits)
    circ = init_biasdelay(qubits, if_iso, ctx)
    circ += readout(qubits, if_iso, ctx)
    return circ

def characterize(qubits, freq_st, freq_ed, freq_points, amp_st, amp_ed, amp_points, signal, if_iso):
    rcp = Recipe('S21vsPower', signal=signal)
    rcp.circuit = circuit
    rcp['qubits'] = tuple(qubits)
    rcp['if_iso'] = if_iso
    rcp['freq'] = np.linspace(freq_st, freq_ed, freq_points)
    rcp['power'] = np.linspace(amp_st, amp_ed, amp_points)
    for q in qubits:
        if freq_st >= 6e9:
            rcp[f'{q}.Measure.frequency'] = rcp['freq']
        else:
            rcp[f'{q}.Measure.frequency'] = rcp['freq'] + s.query(f'{q}.Measure.frequency')
        if amp_ed <= 0.2:
            rcp[f'{q}.Measure.amp'] = rcp['power']
        else:
            rcp[f'{q}.Measure.amp'] = rcp['power']*s.query(f'{q}.Measure.amp')
    thistask = s.submit(rcp.export(), block=True, preview=[], plot=False)
    thistask.bar(interval=0.05)
    return thistask

def analyze(thistask, fignum1row=7, eachfigsize=(3,2.5)):
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
    cfg = get_config_by_rid(rid)
    fig, axes = universe_plot.creat_fig(qubits,fignum1row=fignum1row, eachfigsize=eachfigsize)
    for qidx, q in enumerate(qubits):
        ax = axes[qidx]
        xaxis = result['meta']['axis']['freq'][f'${q}.Measure.frequency']
        yaxis = result['meta']['axis']['power'][f'${q}.Measure.amp']
        extent = universe_plot.get_extent(xaxis, yaxis)
        thisamp = cfg[q]['Measure']['amp']
        ax.imshow(np.abs(data[:,:,qidx]).T,extent=extent,origin='lower',interpolation='none',aspect='auto')
        ax.set_title(q)
        ax.plot([xaxis[0],xaxis[-1]],[thisamp]*2,'r',linewidth=0.5)
    fig.tight_layout()
    fig.suptitle(f'S21, rid={rid}',y=0.99)
    return
    






