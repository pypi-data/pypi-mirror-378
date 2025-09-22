from Ctoolbox.exp.Universe import universe_circ, universe_plot
from importlib import reload
universe_circ = reload(universe_circ)
universe_plot = reload(universe_plot)
init_biasdelay, readout = universe_circ.init_biasdelay, universe_circ.readout

from quark.app import Recipe, s, get_data_by_rid, get_config_by_rid
s.login()

import numpy as np
import matplotlib.pyplot as plt

def circuit(qubits, couplers, flux, if_iso, width=7e-6,ctx=None):
    all_QC = list(qubits) +list(couplers)
    circ = init_biasdelay(qubits, if_iso, ctx)
    circ += [(('R',0),q) for q in qubits]
    circ += [(('R',0),q) for q in qubits]
    circ += [(('Delay',300e-9),q) for q in qubits]
    circ += [('Barrier', tuple(all_QC))]
    circ += [(("setBias", 'flux', flux), q) for q in couplers]
    circ += [(('Delay',width),q) for q in qubits]
    circ += [('Barrier', tuple(all_QC))]
    circ += [(("setBias", 'flux', ctx.query(f'{q}.caliinfo.idlebias')), q) for q in couplers]
    circ += [(('Delay',300e-9),q) for q in qubits]
    circ += readout(qubits, if_iso, ctx)
    return circ

def characterize(qubits, couplers, flux_st, flux_ed, flux_points, signal, if_iso, plot, preview=[],width=7e-6):
    rcp = Recipe('qc_coupling', signal=signal)
    rcp.circuit = circuit
    rcp['qubits'] = tuple(qubits)
    rcp['couplers'] = tuple(couplers)
    rcp['if_iso'] = if_iso
    rcp['width'] = width
    rcp['flux'] = np.linspace(flux_st, flux_ed, flux_points)
    thistask = s.submit(rcp.export(), block=True, preview=preview, plot=plot)
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
    couplers = result['meta']['other']['couplers']
    cfg = get_config_by_rid(rid)

    data = result['data'][signal]
    if include == 'all':
        include = couplers
    fig, axes = universe_plot.creat_fig(include, fignum1row=fignum1row, eachfigsize=eachfigsize)
    qc_info = {}
    fidx = 0
    for cidx, c in enumerate(couplers):
        if c not in include:
            continue
        try:
            qc = [q for q in cfg[c]['topoinfo']['qubits'] if q in qubits][0]
        except:
            continue
        qidx = qubits.index(qc)
        ax = axes[fidx]
        fidx += 1
        ax.set_title(f'{c}-{qc}')  # 标题设置为qubit名称，如'Q0'
        xaxis = result['meta']['axis']['flux']['def']
        ax.plot(xaxis, np.abs(data[:,qidx]))    
    fig.suptitle(f'QC coupling, rid={rid}', y=0.99)
    fig.tight_layout()
    # 添加点击处理器
    qc_info = universe_plot.add_click_handler(fig)
    # 显示图形
    plt.show()
    # 返回选中的点
    return qc_info