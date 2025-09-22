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

def circuit(qubits, state, if_iso, ctx=None):
    circ = init_biasdelay(qubits, if_iso, ctx)
    if state==1:
        circ += [(('R',0),q) for q in qubits]*2
    if state==2:
        circ += [(('R',0),q) for q in qubits]*2
        circ += [(('R12',0),q) for q in qubits]*2
    circ += readout(qubits, if_iso, ctx)
    return circ

def characterize(qubits, state, repeat, freqst, freqed, freqpoints, biasst, biased, biaspoints, if_iso, plot):
    rcp = Recipe('SNRvsbiasnfreq', signal='iq')
    rcp.circuit = circuit
    rcp['qubits'] = tuple(qubits)
    rcp['if_iso'] = if_iso
    rcp['bias'] = np.linspace(biasst,biased,biaspoints)
    rcp['freq'] = np.linspace(freqst,freqed,freqpoints)
    rcp['state'] = state
    rcp['repeat'] = list(range(repeat))
    for q in qubits:
        rcp[f'{q}.Measure.frequency'] = rcp['freq'] + s.query(f'{q}.Measure.frequency')
        rcp[f'{q}.caliinfo.readbias'] = rcp['bias']
    thistask = s.submit(rcp.export(), block=True, preview=[], plot=plot)
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
    freqpoints = result['meta']['axis']['freq']['def'].shape[0]
    biaspoints = result['meta']['axis']['bias']['def'].shape[0]
    data = np.asarray(result['data'][signal]).reshape(biaspoints, freqpoints, 2, -1, len(qubits))
    if include == 'all':
        include = qubits
    fig, axes = universe_plot.creat_fig(include,fignum1row=fignum1row, eachfigsize=eachfigsize)
    fidx = 0
    best_info = {}
    for qidx, q in enumerate(qubits):
        if q not in include:
            continue
        ax = axes[fidx]
        fidx += 1
        thisdata = data[:,:,:,:,qidx]
        avg_g = np.mean(thisdata[:,:,0,:],axis=-1)
        std_g = np.std(thisdata[:,:,0,:],axis=-1)
        avg_e = np.mean(thisdata[:,:,1,:],axis=-1)
        std_e = np.std(thisdata[:,:,1,:],axis=-1)
        Signal = np.abs(avg_e - avg_g)
        Noise = np.mean([std_g,std_e])
        SNR = Signal/Noise
        xaxis = result['meta']['axis']['bias'][f'${q}.caliinfo.readbias']
        yaxis = result['meta']['axis']['freq'][f'${q}.Measure.frequency']
        extent = universe_plot.get_extent(xaxis, yaxis)
        ax.imshow(SNR.T,extent=extent,origin='lower',interpolation='none',aspect='auto')
        ax.set_title(q)
        max_value, max_y, max_x = find_max_coordinates(SNR, yaxis, xaxis)
        best_info[q] = {'best_SNR': max_value, 'best_readbias': max_x, 'best_freq': max_y}
    fig.suptitle(f'SNRvsbiasnfreq, rid={rid}',y=0.99)
    fig.tight_layout()
    plt.show()
    return best_info

def find_max_coordinates(data, xaxis, yaxis):
    max_value = None
    max_i = 0
    max_j = 0
    for i in range(len(data)):
        for j in range(len(data[i])):
            # 更新最大值和索引
            if max_value is None or data[i][j] > max_value:
                max_value = data[i][j]
                max_i = i
                max_j = j
    max_x = xaxis[max_j]  # 假设j对应x轴索引
    max_y = yaxis[max_i]  # 假设i对应y轴索引
    
    return max_value, max_x, max_y