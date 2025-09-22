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

all_qubits = [f"Q{q}" for q in range(112)]
all_couplers = [f"QC{c}" for c in range(195)]
all_QC = all_qubits + all_couplers

def circuit(qubits, couplers, if_iso,flux,flux0, edge=0e-9,ctx=None):
    circ = init_biasdelay(qubits, if_iso, ctx)
    circ += [('Barrier', tuple(all_QC))]
    circ += [(("setBias", 'flux', flux+flux0[k],edge), q) for k,q in enumerate(couplers)]
    circ += [(('Delay',5000e-9),q) for q in qubits]
    circ += [(('R',0),q) for q in qubits]
    circ += [(('R',0),q) for q in qubits]
    circ += [(('Delay',5000e-9),q) for q in qubits]
    circ += readout(qubits, if_iso, ctx)
    return circ

def characterize(qubits,couplers, freq_st, freq_ed, freq_points,flux_st, flux_ed, flux_points, signal, if_iso, plot, flux0=None, preview=[],edge=0e-9):
    flux0 = ([0]*len(couplers)) if flux0 is None else flux0
    rcp = Recipe('QC_anticross', signal=signal)
    rcp.circuit = circuit
    rcp['qubits'] = tuple(qubits)
    rcp['couplers'] = tuple(couplers)
    rcp['if_iso'] = if_iso
    rcp['edge'] = edge
    rcp['flux0'] = flux0
    rcp['flux'] = np.linspace(flux_st, flux_ed, flux_points)
    rcp['freq'] = np.linspace(freq_st, freq_ed, freq_points)
    for q in qubits:
        # rcp[f'{q}.R.width'] = 10e-6
        # rcp[f'{q}.R.amp'] = s.query(f'{q}.R.amp')/5
        if freq_st >= 2e9:
            rcp[f'{q}.R.frequency'] = rcp['freq']
        else:
            rcp[f'{q}.R.frequency'] = rcp['freq'] + s.query(f'{q}.R.frequency')
    thistask = s.submit(rcp.export(), block=True, preview=preview, plot=plot)
    thistask.bar(interval=0.05)
    return thistask

def analyze(thistask_rid, fignum1row=7, eachfigsize=(3,2.5), include='all'):
    try:
        result = thistask_rid.result()
        rid = thistask_rid.rid
    except:
        result = get_data_by_rid(thistask_rid)
        rid = thistask_rid
    signal = result['meta']['other']['signal']
    qubits = result['meta']['other']['qubits']
    couplers = result['meta']['other']['couplers']
    data = result['data'][signal]
    flux0=result['meta']['other']['flux0']
    qlens = len(qubits)
    cfg = get_config_by_rid(rid)
    fig, axes = universe_plot.creat_fig(qubits,fignum1row=fignum1row, eachfigsize=eachfigsize)
    sweet_info = {}
    for qidx, q in enumerate(qubits):
        ax = axes[qidx]
        yaxis = result['meta']['axis']['freq'][f'${q}.R.frequency']
        xaxis = result['meta']['axis']['flux'][f'def']+flux0[qidx]
        extent = universe_plot.get_extent(xaxis, yaxis)
        # thisamp = cfg[q]['R']['amp']
        ax.imshow(np.abs(data[:,:,qidx]).T,extent=extent,origin='lower',interpolation='none',aspect='auto')
        # para,fitdata,r_squared, offsetbias = fit_S21vsflux(np.abs(data[:,:,qidx]),xaxis,yaxis,guessperiod=1.8)
        # if r_squared < 0.6:
        #     print(q)
        #     ax.plot(xaxis,fitdata,'r')
        #     sweet_info[q] = np.round(offsetbias,4)
        # else:
        #     ax.plot(xaxis,fitdata,'w')
        #     sweet_info[q] = np.round(para[3],4)
        ax.set_title(q+'-'+couplers[qidx])# + f' {sweet_info[q]}')
    fig.suptitle(f'QC_anticross, rid={rid}',y=0.99)
    fig.tight_layout()
    return sweet_info
    
def qubit_spectrum_2D(bias,Ej,Ec,period,biasoffset,d):
    return np.sqrt(8*Ej*Ec*(np.cos(2*np.pi/period/2*(bias-biasoffset)))**2+d**2*(np.sin(2*np.pi/period/2*(bias-biasoffset)))**2)-Ec

def S21_vs_flux(bias,Ej,Ec,period,biasoffset,d,fc,g):
    fq = qubit_spectrum_2D(bias,Ej,Ec,period,biasoffset,d)
    return (fc+fq)/2+np.sqrt(4*g**2+(fq-fc)**2)/2

def fit_S21vsflux(data,biaslist,freqlist,guessperiod=2):
    Frlist = []
    for eachbias in data:
        Frlist.append(freqlist[np.argmax(eachbias)])
    try:
        maxFr = np.max(Frlist)
        offsetbias = biaslist[int(np.mean(np.where(Frlist==maxFr)[0]))]
        p0 = [50*200e6,200e6,guessperiod,offsetbias,0.3,np.mean(Frlist),70e6]
        para = curve_fit(S21_vs_flux,biaslist,Frlist,p0=p0,maxfev=1000000)[0]
        fitdata = S21_vs_flux(biaslist,*para)
        sse = np.sum((Frlist - fitdata) **2)
        sst = np.sum((Frlist - np.mean(Frlist))** 2)
        r_squared = 1 - (sse / sst)
    except:
        para = np.zeros(8)
        fitdata = np.mean(Frlist)*np.ones(len(Frlist))
    return para,fitdata, r_squared, offsetbias
