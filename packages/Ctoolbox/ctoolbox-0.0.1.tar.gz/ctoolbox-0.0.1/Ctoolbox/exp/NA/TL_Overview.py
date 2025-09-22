from quark.app import Recipe, s, get_data_by_rid
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
s.login()

def circuit(FrequencyStart, FrequencyStop, NumberOfPoints, Power, Bandwidth, Signal, ctx=None):
    c = [
        (('SET', 'FrequencyStart', FrequencyStart), 'NA.CH1'),
        (('SET', 'FrequencyStop', FrequencyStop), 'NA.CH1'),
        (('SET', 'NumberOfPoints', NumberOfPoints), 'NA.CH1'),
        (('SET', 'Power', Power), 'NA.CH1'),
        (('SET', 'Bandwidth', Bandwidth), 'NA.CH1'),
        (('GET', Signal), 'NA.CH1')
    ]
    return c

def characterize(FrequencyStart, FrequencyStop, NumberOfPoints, Power, Bandwidth, Signal):
    rcp = Recipe('NA_S21_TL_overview', signal = Signal)
    rcp.circuit = circuit
    rcp['Signal'] = Signal
    rcp['FrequencyStart'] = FrequencyStart
    rcp['FrequencyStop'] = FrequencyStop
    rcp['NumberOfPoints'] = NumberOfPoints
    rcp['Power'] = Power
    rcp['Bandwidth'] = Bandwidth
    thistask = s.submit(rcp.export(), block=True, preview=[], plot=False)
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
    Power = result['meta']['other']['Power']
    Bandwidth = result['meta']['other']['Bandwidth']
    Signal = result['meta']['other']['Signal']
    Freqaxis = np.linspace(FrequencyStart, FrequencyStop, NumberOfPoints)
    plt.figure()
    plt.plot(Freqaxis, result['data'][Signal][0],label=f'Power={Power}dB'+f' Bw={Bandwidth}')
    plt.legend()
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('S21 (dB)')
    plt.title(f'TL{TLnum}_overview, id={rid}')
    plt.show()

def analyze_plot(thistask,TLnum,rid=None,height=15,distance=20):
    if thistask is not None:
        result = thistask.result()
        rid = thistask.rid
    else:
        result = get_data_by_rid(rid)
    FrequencyStart = result['meta']['other']['FrequencyStart']
    FrequencyStop = result['meta']['other']['FrequencyStop']
    NumberOfPoints = result['meta']['other']['NumberOfPoints']
    Power = result['meta']['other']['Power']
    Bandwidth = result['meta']['other']['Bandwidth']
    Signal = result['meta']['other']['Signal']
    Freqaxis = np.linspace(FrequencyStart, FrequencyStop, NumberOfPoints)
    S21 = result['data'][Signal][0]
    peaks, _ = find_peaks(-S21, height = height, distance = distance)
    x, y = Freqaxis[peaks], S21[peaks]
    plt.figure()
    plt.plot(Freqaxis, S21, label=f'Power={Power}dB'+f' Bw={Bandwidth}')
    for i in range(len(x)):
        plt.plot(x[i],y[i],'ro')
    plt.legend()
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('S21 (dB)')
    plt.title(f'TL{TLnum}_overview, id={rid}')
    plt.show()
    return x

