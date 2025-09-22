from Ctoolbox.exp.Universe import universe_circ, universe_plot
from importlib import reload
universe_circ = reload(universe_circ)
universe_plot = reload(universe_plot)
init_biasdelay, readout = universe_circ.init_biasdelay, universe_circ.readout

from quark.app import Recipe, s, get_data_by_rid
s.login()

import numpy as np
import matplotlib.pyplot as plt

def circuit(qubits, if_iso, ctx=None):
    circ = init_biasdelay(qubits, if_iso, ctx)
    circ += readout(qubits, if_iso, ctx)
    return circ

def characterize(qubits, if_iso, repeat):
    rcp = Recipe('s21', signal='trace')
    rcp.circuit = circuit
    rcp['qubits'] = tuple(qubits)
    rcp['if_iso'] = if_iso
    rcp['repeat'] = list(range(repeat))
    for q in qubits:
        rcp[f'{q}.Measure.frequency'] = 7e9
        rcp[f'{q}.Measure.duration'] = 1.8e-6
        rcp[f'{q}.Measure.amp'] = 0.8
        rcp[f'{q}.Measure.ring_up_amp'] = 0.8
        rcp[f'{q}.Measure.weight'] = 'square(1800e-9)>>900e-9'
    thistask = s.submit(rcp.export(), block=True, preview=[], plot=False)
    thistask.bar(interval=0.05)
    return thistask

def plot(thistask, ADCsr, eachfigsize=(3,2.5)):
    if thistask is not None:
        result = thistask.result()
        rid = thistask.rid
    else:
        result = get_data_by_rid(thistask)
        rid = thistask
    signal = result['meta']['other']['signal']
    traces = result['data'][signal]
    qubits = result['meta']['other']['qubits']
    qlens = len(qubits)
    fig, axes = universe_plot.creat_fig(qubits,fignum1row=4, eachfigsize=eachfigsize)
    for qidx, q in enumerate(qubits):
        thistrace = np.mean(np.mean(traces[:,:,:,qidx],axis=-1),axis=0)
        points = np.array(list(range(thistrace.shape[0])))
        timeaxis = 1 / ADCsr * points
        ax = axes[qidx]
        ax.plot(timeaxis, thistrace)
        ax.set_title(q)
    fig.suptitle(f'GetTrace, rid={rid}')
    fig.tight_layout()
    return

def analyze(thistask, ADCsr, eachfigsize=(3,2.5)):
    if thistask is not None:
        result = thistask.result()
        rid = thistask.rid
    else:
        result = get_data_by_rid(thistask)
        rid = thistask
    signal = result['meta']['other']['signal']
    traces = result['data'][signal]
    qubits = result['meta']['other']['qubits']
    TrigDinfo = {}
    for qidx, q in enumerate(qubits):
        fig = plt.figure()
        thistrace = np.mean(np.mean(traces[:,:,:,qidx],axis=-1),axis=0)
        points = np.array(list(range(thistrace.shape[0])))
        timeaxis = 1 / ADCsr * points
        plt.plot(timeaxis, thistrace)
        #############
        Amp_threshold = np.max(np.abs(thistrace))*0.5
        index = np.where((np.abs(thistrace)-Amp_threshold) > 0)[0][0]
        this_TrigD = np.round(timeaxis[index],9)
        plt.plot([this_TrigD]*2,[-np.max(np.abs(thistrace)),np.max(np.abs(thistrace))])
        TrigDinfo[q] = this_TrigD
        plt.title(q + f' {this_TrigD*1e9}')
    return TrigDinfo

