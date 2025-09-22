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

def circuit(qubits, if_iso, ctx=None):
    circ = init_biasdelay(qubits, if_iso, ctx)
    circ += readout(qubits, if_iso, ctx)
    return circ

def characterize(qubits, freq_st, freq_ed, freq_points, flux_st, flux_ed, flux_points, signal, if_iso):
    rcp = Recipe('s21', signal=signal)
    rcp.circuit = circuit
    rcp['qubits'] = tuple(qubits)
    rcp['if_iso'] = if_iso
    rcp['flux'] = np.linspace(flux_st, flux_ed, flux_points)
    rcp['freq'] = np.linspace(freq_st, freq_ed, freq_points)
    for q in qubits:
        if freq_st >= 6e9:
            rcp[f'{q}.Measure.frequency'] = rcp['freq']
        else:
            rcp[f'{q}.Measure.frequency'] = rcp['freq'] + s.query(f'{q}.Measure.frequency')
        rcp[f'{q}.caliinfo.readbias'] = rcp['flux']
    thistask = s.submit(rcp.export(), block=True, preview=[], plot=False)
    thistask.bar(interval=0.05)
    return thistask

def analyze(thistask_rid, rid=None, fignum1row=7, eachfigsize=(3,2.5)):
    try:
        result = thistask_rid.result()
        rid = thistask_rid.rid
    except:
        result = get_data_by_rid(thistask_rid)
        rid = thistask_rid
    signal = result['meta']['other']['signal']
    qubits = result['meta']['other']['qubits']
    data = result['data'][signal]
    qlens = len(qubits)
    cfg = get_config_by_rid(rid)
    fig, axes = universe_plot.creat_fig(qubits,fignum1row=fignum1row, eachfigsize=eachfigsize)
    sweet_info = {}
    for qidx, q in enumerate(qubits):
        ax = axes[qidx]
        yaxis = result['meta']['axis']['freq'][f'${q}.Measure.frequency']
        xaxis = result['meta']['axis']['flux'][f'${q}.caliinfo.readbias']
        extent = universe_plot.get_extent(xaxis, yaxis)
        thisamp = cfg[q]['Measure']['amp']
        ax.imshow(np.abs(data[:,:,qidx]).T,extent=extent,origin='lower',interpolation='none',aspect='auto')
        para,fitdata,r_squared, offsetbias = fit_S21vsflux(np.abs(data[:,:,qidx]),xaxis,yaxis,guessperiod=1.8)
        if r_squared < 0.6:
            print(q)
            ax.plot(xaxis,fitdata,'r')
            sweet_info[q] = np.round(offsetbias,4)
        else:
            ax.plot(xaxis,fitdata,'w')
            sweet_info[q] = np.round(para[3],4)
        ax.set_title(q + f' {sweet_info[q]}')
    fig.suptitle(f'S21, rid={rid}',y=0.99)
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
        Frlist.append(freqlist[np.argmin(eachbias)])
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






