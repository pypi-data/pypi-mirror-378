from quark.app import Recipe, s, get_data_by_rid
import numpy as np
import matplotlib.pyplot as plt
s.login()

def getextent(axis1,axis2):
    dx = (axis1[1]-axis1[0])/2
    dy = (axis2[1]-axis2[0])/2
    extent = [axis1[0]-dx,axis1[-1]+dx,axis2[0]-dy,axis2[-1]+dy]
    return extent

def sort_cal_data(cal_data, PumpFreqaxis, PumpPoweraxis):
    """
    按numpy二维数组cal_data的值从大到小排序，返回包含值及其对应索引的列表
    sorted_list: 排序后的列表，格式为[(值, (频率索引, 功率索引)), ...]
    """
    power_indices, freq_indices = np.indices(cal_data.shape)
    values = cal_data.flatten()
    freq_indices_flat = freq_indices.flatten()
    power_indices_flat = power_indices.flatten()
    sorted_indices = np.argsort(values)[::-1]
    sorted_list = [
        (values[i], (freq_indices_flat[i], power_indices_flat[i]))
        for i in sorted_indices
    ]
    return sorted_list

def circuit(JPA, FrequencyStart, FrequencyStop, NumberOfPoints, Power, Flux, 
            Bandwidth, Signal, PumpFreq, PumpPower, ctx=None):
    Flux = 1e-15 if Flux == 0 else Flux
    c = [
        (('setBias', 'flux', Flux), JPA),
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

def characterize(JPA, FrequencyStart, FrequencyStop, NumberOfPoints, 
                 Flux, Power, Bandwidth, Signal, PumpFreqlist, PumpPowerlist):
    rcp = Recipe('NA_JPAgainvspumppara', signal = Signal)
    rcp.circuit = circuit
    rcp['JPA'] = JPA
    rcp['Signal'] = Signal
    rcp['FrequencyStart'] = FrequencyStart
    rcp['FrequencyStop'] = FrequencyStop
    rcp['NumberOfPoints'] = NumberOfPoints
    rcp['Power'] = Power
    rcp['Bandwidth'] = Bandwidth
    rcp['Flux'] = Flux
    rcp['PumpFreq'] = PumpFreqlist
    rcp['PumpPower'] = PumpPowerlist
    thistask = s.submit(rcp.export(), block=True, preview=[], plot=False)
    thistask.bar(interval=0.5)
    return thistask

def analyze_plot(thistask,JPA,stdfactor=3,rid=None):
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
    Flux = result['meta']['other']['Flux']
    PumpFreqaxis = result['meta']['axis']['PumpFreq']['def']
    PumpPoweraxis = result['meta']['axis']['PumpPower']['def']
    data = result['data'][Signal]
    ave_data = np.mean(data,axis=-1)
    std_data = np.std(data,axis=-1)
    cal_data = ave_data - std_data*stdfactor
    sorted_result = sort_cal_data(cal_data, PumpFreqaxis, PumpPoweraxis)
    plt.figure()
    plt.imshow(cal_data.T,extent=getextent(PumpFreqaxis,PumpPoweraxis),aspect='auto',origin='lower',interpolation='none')
    plt.xlabel('PumpFreq (Hz)')
    plt.ylabel('PumpPower (dBm)')
    plt.title(f'{JPA}_GainvsPumppara, id={rid}')
    plt.colorbar()
    plt.show()    
    return Flux, sorted_result








