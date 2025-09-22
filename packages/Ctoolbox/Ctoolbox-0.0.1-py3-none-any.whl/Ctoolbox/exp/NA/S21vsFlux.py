from quark.app import Recipe, s, get_data_by_rid
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
s.login()

def getextent(axis1,axis2):
    dx = (axis1[1]-axis1[0])/2
    dy = (axis2[1]-axis2[0])/2
    extent = [axis1[0]-dx,axis1[-1]+dx,axis2[0]-dy,axis2[-1]+dy]
    return extent

def qubit_spectrum_2D(bias,Ej,Ec,period,biasoffset,d):
    return np.sqrt(8*Ej*Ec*(np.cos(2*np.pi/period/2*(bias-biasoffset)))**2+
                   d**2*(np.sin(2*np.pi/period/2*(bias-biasoffset)))**2)-Ec

def S21_vs_flux(bias,Ej,Ec,period,biasoffset,d,fc,g):
    fq = qubit_spectrum_2D(bias,Ej,Ec,period,biasoffset,d)
    return (fc+fq)/2+np.sqrt(4*g**2+(fq-fc)**2)/2

def fit_S21vsflux(biaslist,Frlist,guessperiod=1.5):
    p0 = [50*170e6,170e6,guessperiod,0,0.2,np.mean(Frlist),75e6]
    try:
        para = curve_fit(S21_vs_flux,biaslist,Frlist,p0=p0,maxfev=1000000)[0]
        fitdata = S21_vs_flux(biaslist,*para)
    except:
        para = np.zeros(8)
        fitdata = np.mean(Frlist)*np.ones(len(Frlist))
    return para,fitdata

def circuit(Qubits, FrequencyStart, FrequencyStop, NumberOfPoints, Power, Flux, Bandwidth, Signal, ctx=None):
    c = []
    Flux = 1e-15 if Flux == 0 else Flux
    for q in Qubits:
        c.append((('setBias', 'flux', Flux), q))
    c += [
        (('SET', 'FrequencyStart', FrequencyStart), 'NA.CH1'),
        (('SET', 'FrequencyStop', FrequencyStop), 'NA.CH1'),
        (('SET', 'NumberOfPoints', NumberOfPoints), 'NA.CH1'),
        (('SET', 'Power', Power), 'NA.CH1'),
        (('SET', 'Bandwidth', Bandwidth), 'NA.CH1'),
        (('GET', Signal), 'NA.CH1')
    ]
    return c

def characterize(Qubits, FrequencyStart, FrequencyStop, NumberOfPoints, FluxStart, FluxStop, Fluxpoints, Power, Bandwidth, Signal,preview=[]):
    rcp = Recipe('NA_S21vsPower', signal = Signal)
    rcp.circuit = circuit
    rcp['Qubits'] = tuple(Qubits)
    rcp['Signal'] = Signal
    rcp['FrequencyStart'] = FrequencyStart
    rcp['FrequencyStop'] = FrequencyStop
    rcp['NumberOfPoints'] = NumberOfPoints
    rcp['Power'] = Power
    rcp['Bandwidth'] = Bandwidth
    rcp['Flux'] = np.linspace(FluxStart,FluxStop,Fluxpoints)
    thistask = s.submit(rcp.export(), block=True, preview=preview, plot=False)
    thistask.bar(interval=0.05)
    return thistask

def plot(thistask,TLnum,rid=None):
    if thistask is not None:
        result = thistask.result()
        rid = thistask.rid
    else:
        result = get_data_by_rid(rid)
    FrequencyStart = result['meta']['other']['FrequencyStart']
    FrequencyStop = result['meta']['other']['FrequencyStop']
    NumberOfPoints = result['meta']['other']['NumberOfPoints']
    Bandwidth = result['meta']['other']['Bandwidth']
    Signal = result['meta']['other']['Signal']
    Power = result['meta']['other']['Power']
    Fluxaxis = result['meta']['axis']['Flux']['def']
    Freqaxis = np.linspace(FrequencyStart, FrequencyStop, NumberOfPoints)
    plt.figure()
    plt.imshow(result['data'][Signal].T,extent=getextent(Fluxaxis,Freqaxis),aspect='auto',origin='lower',interpolation='none')
    plt.xlabel('Flux (dBm)')
    plt.ylabel('Frequency (Hz)')
    plt.title(f'S21vsFlux_{TLnum}, id={rid}')
    plt.show()

def analyze_plot(thistask,TLnum,Qubit,num_qubit,rid=None,height=15,distance=20):
    '''
    用于遍历调单个qubit的情景，可返回当前所调的是第几个腔
    '''
    if thistask is not None:
        result = thistask.result()
        rid = thistask.rid
    else:
        result = get_data_by_rid(rid)
    FrequencyStart = result['meta']['other']['FrequencyStart']
    FrequencyStop = result['meta']['other']['FrequencyStop']
    NumberOfPoints = result['meta']['other']['NumberOfPoints']
    Bandwidth = result['meta']['other']['Bandwidth']
    Signal = result['meta']['other']['Signal']
    Power = result['meta']['other']['Power']
    Fluxaxis = result['meta']['axis']['Flux']['def']
    Freqaxis = np.linspace(FrequencyStart, FrequencyStop, NumberOfPoints)
    S212D = result['data'][Signal]
    all_peaks_x = []
    for idx, eachbiasS21 in enumerate(S212D):
        peaks, _ = find_peaks(-eachbiasS21, height = height, distance = distance)
        x, y = Freqaxis[peaks], eachbiasS21[peaks]
        if len(x) != num_qubit:
            continue
        all_peaks_x.append(x)
    all_peaks_x = np.array(all_peaks_x)
    tunecavity_idx = np.argmax(np.std(all_peaks_x,axis=0))
    plt.figure()
    plt.imshow(S212D.T,extent=getextent(Fluxaxis,Freqaxis),aspect='auto',origin='lower',interpolation='none')
    plt.xlabel('Flux (dBm)')
    plt.ylabel('Frequency (Hz)')
    plt.title(f'S21vsFlux_{Qubit}, id={rid}')
    plt.show()
    return tunecavity_idx

def fit_plot(thistask,TLnum,Qubit,rid=None,guessperiod=0.8):
    if thistask is not None:
        result = thistask.result()
        rid = thistask.rid
    else:
        result = get_data_by_rid(rid)
    FrequencyStart = result['meta']['other']['FrequencyStart']
    FrequencyStop = result['meta']['other']['FrequencyStop']
    NumberOfPoints = result['meta']['other']['NumberOfPoints']
    Bandwidth = result['meta']['other']['Bandwidth']
    Signal = result['meta']['other']['Signal']
    Power = result['meta']['other']['Power']
    Fluxaxis = result['meta']['axis']['Flux']['def']
    Freqaxis = np.linspace(FrequencyStart, FrequencyStop, NumberOfPoints)
    S212D = result['data'][Signal]
    all_Fr = []
    for eachbiasS21 in S212D:
        idx = np.argmin(eachbiasS21)
        Fr = Freqaxis[idx]
        all_Fr.append(Fr)
    all_Fr = np.array(all_Fr)
    para,fitdata = fit_S21vsflux(Fluxaxis,all_Fr,guessperiod)
    plt.figure()
    plt.imshow(S212D.T,extent=getextent(Fluxaxis,Freqaxis),aspect='auto',origin='lower',interpolation='none')
    plt.plot(Fluxaxis, all_Fr,'r.')
    plt.plot(Fluxaxis,fitdata,'w--')
    plt.xlabel('Flux (dBm)')
    plt.ylabel('Frequency (Hz)')
    plt.title(f'S21vsFlux_{Qubit}, id={rid}')
    plt.show()
    return para

def circuit_test(Qubits, FrequencyStart, FrequencyStop, NumberOfPoints, Power, Flux, Bandwidth, Signal, ctx=None):
    c = []
    Flux = 1e-15 if Flux == 0 else Flux
    for q in Qubits:
        c.append((('setBias', 'flux', Flux), q))
    c += [
        (('SET', 'FrequencyStart', FrequencyStart), 'NA.CH1'),
        (('SET', 'FrequencyStop', FrequencyStop), 'NA.CH1'),
        (('SET', 'NumberOfPoints', NumberOfPoints), 'NA.CH1'),
        (('SET', 'Power', Power), 'NA.CH1'),
        (('SET', 'Bandwidth', Bandwidth), 'NA.CH1'),
        (('GET', Signal), 'NA.CH1')
    ]
    return c