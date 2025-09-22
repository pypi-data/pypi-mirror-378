from quark.app import Recipe, s, get_data_by_rid
import numpy as np
import matplotlib.pyplot as plt
s.login()

def circuit(FrequencyStart, FrequencyStop, NumberOfPoints, Power, Bandwidth, Signal, JPA, Flux, PumpPower, PumpFreq, idx, ctx=None):
    switch = 'OFF' if idx == 0 else 'ON'
    flux = 1e-15 if idx == 0 else Flux
    c = [
        (('SET', 'Output', switch), 'MW.CH1'),
        (('setBias', 'flux', flux), JPA),
        (('SET', 'Power', PumpPower), 'MW.CH1'),
        (('SET', 'Frequency', PumpFreq), 'MW.CH1'),
        (('SET', 'FrequencyStart', FrequencyStart), 'NA.CH1'),
        (('SET', 'FrequencyStop', FrequencyStop), 'NA.CH1'),
        (('SET', 'NumberOfPoints', NumberOfPoints), 'NA.CH1'),
        (('SET', 'Power', Power), 'NA.CH1'),
        (('SET', 'Bandwidth', Bandwidth), 'NA.CH1'),
        (('GET', Signal), 'NA.CH1')
    ]
    return c

def characterize(JPA, FrequencyStart, FrequencyStop, NumberOfPoints, Power, Bandwidth, Signal, Flux, PumpPower, PumpFreq):
    rcp = Recipe('JPA_checkgain', signal = Signal)
    rcp.circuit = circuit
    rcp['Signal'] = Signal
    rcp['FrequencyStart'] = FrequencyStart
    rcp['FrequencyStop'] = FrequencyStop
    rcp['NumberOfPoints'] = NumberOfPoints
    rcp['Power'] = Power
    rcp['Bandwidth'] = Bandwidth
    rcp['JPA'] = JPA
    rcp['Flux'] = Flux
    rcp['PumpPower'] = PumpPower
    rcp['PumpFreq'] = PumpFreq
    rcp['idx'] = [0,1]
    thistask = s.submit(rcp.export(), block=True, preview=[], plot=False)
    thistask.bar(interval=0.05)
    return thistask

def plot(thistask,JPA,rid=None):
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
    PumpPower = result['meta']['other']['PumpPower']
    PumpFreq = result['meta']['other']['PumpFreq']
    Flux = result['meta']['other']['Flux']
    Freqaxis = np.linspace(FrequencyStart, FrequencyStop, NumberOfPoints)
    plt.figure()
    plt.plot(Freqaxis, result['data'][Signal][0],label=f'JPA_OFF')
    plt.plot(Freqaxis, result['data'][Signal][1],label=f'PP={PumpPower}, PF={PumpFreq}, Flux={Flux}')
    plt.legend()
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('S21 (dB)')
    plt.title(f'{JPA}_Gain, id={rid}')
    plt.show()

