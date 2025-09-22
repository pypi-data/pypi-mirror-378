from Ctoolbox.exp.Universe import universe_circ, universe_plot
from importlib import reload
universe_circ = reload(universe_circ)
universe_plot = reload(universe_plot)
init_biasdelay, readout = universe_circ.init_biasdelay, universe_circ.readout

from quark.app import Recipe, s, get_data_by_rid
from qulab.visualization import plotDistribution

s.login()

import numpy as np
import matplotlib.pyplot as plt

def circuit(qubits,state,if_iso,ctx=None):
    circ = init_biasdelay(qubits, if_iso, ctx)
    if state==1:
        circ += [(('R',0),q) for q in qubits]*2
    if state==2:
        circ += [(('R',0),q) for q in qubits]*2
        circ += [(('R12',0),q) for q in qubits]*2
    circ += readout(qubits, if_iso, ctx)
    return circ

def characterize(qubits,state,repeat,if_iso):
    rcp = Recipe('singleshot', signal='iq')
    rcp.circuit = circuit
    rcp['qubits'] = tuple(qubits)
    rcp['if_iso'] = if_iso
    rcp['state'] = state
    rcp['repeat'] = list(range(repeat))
    thistask = s.submit(rcp.export(), block=True, preview=[], plot=False)
    thistask.bar(interval=0.05)
    return thistask

def analyze(thistask,fignum1row=6, eachfigsize=(3,2.5), include='all'):
    try:
        result = thistask.result()
        rid = thistask.rid
    except:
        result = get_data_by_rid(thistask)
        rid = thistask
    qubits = result['meta']['other']['qubits']
    signal = result['meta']['other']['signal']
    data = np.asarray(result['data'][signal]).reshape(2,-1,len(qubits))

    if include == 'all':
        include = qubits*2
    else:
        include = include*2
    fig, axes = universe_plot.creat_fig(include,fignum1row=fignum1row, eachfigsize=eachfigsize)
    readout_info = {}
    fidx = 0
    for qidx, q in enumerate(qubits):
        if q not in include:
            continue
        ax1,ax2 = axes[fidx],axes[fidx+1]
        fidx += 2
        info = plotDistribution(data[0,:,qidx],data[1,:,qidx],fig=fig,axes=(ax1,ax2))
        ground = info['visibility'][1]
        excited = 1-info['visibility'][2]
        visibility = info['visibility'][0]
        ax1.set_title(f'{q}_ground={np.round(ground,2)}_excited={np.round(excited,2)}',fontsize=8)
        threshold = info['threshold']
        phi = info['phi']
        readout_info[q]={}
        readout_info[q]['threshold']=threshold
        readout_info[q]['phi']=phi
        readout_info[q]['PgPe']=[1-ground,excited]
    fig.suptitle(f'Scatter, rid={rid}',y=0.99)
    fig.tight_layout()
    return readout_info






# threshold_dict = {}
# phi_dict = {}
# pgpe_dict = {}
# fig, ax = plt.subplots((len(qubits)+2)//3, 6, figsize=[10, (len(qubits)+2)//3*1.6])
# ax = ax.flatten()
# fig.suptitle(Scatter.name.split('/')[1]+f' id={rid}',y=0.995)
# for i, q in enumerate(qubits):
#     info = plotDistribution(values[0,:,i],values[1,:,i],fig=fig,axes=(ax[2*i],ax[2*i+1]))
#     ground = info['visibility'][1]
#     excited = 1-info['visibility'][2]
#     visibility = info['visibility'][0]
#     ax[2*i].set_title(f'{q}_ground={np.round(ground,2)}_excited={np.round(excited,2)}',fontsize=5)
#     threshold = info['threshold']
#     phi = info['phi']
#     threshold_dict[q] = threshold
#     phi_dict[q] = phi
#     pgpe_dict[q] = [1-ground,excited]
# fig.tight_layout()
