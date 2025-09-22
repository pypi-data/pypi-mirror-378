from quark.app import Recipe, s, get_data_by_rid
import numpy as np
import matplotlib.pyplot as plt
s.login()

def getextent(axis1,axis2):
    dx = (axis1[1]-axis1[0])/2
    dy = (axis2[1]-axis2[0])/2
    extent = [axis1[0]-dx,axis1[-1]+dx,axis2[0]-dy,axis2[-1]+dy]
    return extent

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

def characterize(FrequencyStart, FrequencyStop, NumberOfPoints, PowerStart, PowerStop, PowerStep, Bandwidth, Signal):
    rcp = Recipe('NA_S21vsPower', signal = Signal)
    rcp.circuit = circuit
    rcp['Signal'] = Signal
    rcp['FrequencyStart'] = FrequencyStart
    rcp['FrequencyStop'] = FrequencyStop
    rcp['NumberOfPoints'] = NumberOfPoints
    rcp['Bandwidth'] = Bandwidth
    rcp['Power'] = np.arange(PowerStart,PowerStop+0.1,PowerStep)
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
    Bandwidth = result['meta']['other']['Bandwidth']
    Signal = result['meta']['other']['Signal']
    Poweraxis = result['meta']['axis']['Power']['def']
    Freqaxis = np.linspace(FrequencyStart, FrequencyStop, NumberOfPoints)
    plt.figure()
    plt.imshow(result['data'][Signal].T,extent=getextent(Poweraxis,Freqaxis),aspect='auto',origin='lower',interpolation='none')
    plt.xlabel('Power (dBm)')
    plt.ylabel('Frequency (Hz)')
    plt.title(f'S21vsPower_{TLnum}, id={rid}')
    plt.show()


