from quark.app import Recipe, s, get_data_by_rid
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
s.login()

def circuit(Qubits, FrequencyCenter, FrequencySpan, NumberOfPoints, NAPower, Bandwidth, MWFrequency, MWPower, Flux, Signal, ctx=None):
    c = []
    Flux = 1e-15 if Flux == 0 else Flux
    for q in Qubits:
        c.append((('setBias', 'flux', Flux), q))
    c += [
        (('SET', 'FrequencyStart', FrequencyCenter - FrequencySpan), 'NA.CH1'),
        (('SET', 'FrequencyStop', FrequencyCenter + FrequencySpan), 'NA.CH1'),
        (('SET', 'NumberOfPoints', NumberOfPoints), 'NA.CH1'),
        (('SET', 'Power', NAPower), 'NA.CH1'),
        (('SET', 'Bandwidth', Bandwidth), 'NA.CH1'),
        (('SET', 'Frequency', MWFrequency), 'MW.CH1'),
        (('SET', 'Power', MWPower), 'MW.CH1'),
        (('GET', Signal), 'NA.CH1')
    ]
    return c

def characterize(Qubits, FrequencySpan, NumberOfPoints, NAPower, Bandwidth, MWFrequency, MWPower, Signal, plot, preview):
    rcp = Recipe('NA_spectrum', signal = Signal)
    rcp.circuit = circuit
    rcp['Qubits'] = tuple(Qubits)
    rcp['Signal'] = Signal
    rcp['FrequencySpan'] = FrequencySpan
    rcp['NumberOfPoints'] = NumberOfPoints
    rcp['NAPower'] = NAPower
    rcp['Bandwidth'] = Bandwidth
    rcp['MWFrequency'] = MWFrequency
    rcp['MWPower'] = MWPower
    for q in Qubits:
        rcp['FrequencyCenter'] = s.query(f'{q}.Measure.frequency')
        rcp['Flux'] = s.query(f'{q}.caliinfo.sweetbias')
    thistask = s.submit(rcp.export(), block=True, preview=preview, plot=plot)
    thistask.bar(interval=0.05)
    return thistask


def analyze_plot(thistask, rid=None, height=15, distance=20, mode = 'max'):
    if thistask is not None:
        result = thistask.result()
        rid = thistask.rid
    else:
        result = get_data_by_rid(rid)
    Qubits = result['meta']['other']['Qubits']
    MWPower = result['meta']['other']['MWPower']
    Flux = result['meta']['other']['Flux']
    Signal = result['meta']['other']['Signal']
    MWFrequency = result['meta']['axis']['MWFrequency']['def']
    S21 = result['data'][Signal].mean(axis=-1)
    if mode is 'max':
        peaks, _ = find_peaks(S21, height = height, distance = distance)
    else:
        peaks, _ = find_peaks(-S21, height = height, distance = distance)
    x, y = MWFrequency[peaks], S21[peaks]
    plt.figure()
    if isinstance(x,str):
        pass
    else:
        for i in range(len(x)):
            plt.plot(x[i],y[i],'ro',label=f'{x[i]/1e9:.3f}GHz')
    plt.plot(MWFrequency, S21, label=f'Drive Power={MWPower}dBm')
    plt.legend()
    plt.xlabel('Drive frequency (Hz)')
    plt.ylabel('S21 (dB)')
    plt.title(f'{Qubits[0]}@Flux: {Flux}, id={rid}')
    plt.show()
    return x