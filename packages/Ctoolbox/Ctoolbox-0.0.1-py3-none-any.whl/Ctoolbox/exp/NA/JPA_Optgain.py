from quark.app import Recipe, s, get_data_by_rid
import numpy as np
import matplotlib.pyplot as plt
from sko.GA import GA
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

def analyze(thistask, JPA, stdfactor=3, gain_threshold=8, rid=None):
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
    Flux = result['meta']['other']['Flux']
    PumpPower = result['meta']['other']['PumpPower']
    PumpFreq = result['meta']['other']['PumpFreq']
    Freqaxis = np.linspace(FrequencyStart, FrequencyStop, NumberOfPoints)
    data = result['data'][Signal][1]
    ave_data = np.mean(data)
    if ave_data >= gain_threshold:
        print('######################')
        print(f'PumpPower={PumpPower}',' ', f'PumpFreq={PumpFreq}',' ', f'Flux={Flux}')
        print('######################')
    std_data = np.std(data)
    print(ave_data, std_data, 'PP',PumpPower,'PF', PumpFreq,'Fl', Flux)
    cal_data = ave_data - std_data*stdfactor
    return cal_data


def Opt_gain(JPA, FrequencyStart, FrequencyStop, NumberOfPoints, Power, Bandwidth, Signal, param_ranges, stdfactor, gain_threshold):
    global count
    count = 0
    def fitness_func(params):
        global count
        count +=1
        flux, PumpFreq_10G, PumpPower_10dBm = params
        Flux = flux/10
        PumpFreq = PumpFreq_10G * 1e10
        PumpPower = PumpPower_10dBm
        thistask = characterize(JPA, FrequencyStart, FrequencyStop, NumberOfPoints, Power, Bandwidth, Signal, Flux, PumpPower, PumpFreq)
        cal_data = analyze(thistask, JPA, stdfactor, gain_threshold, rid=None)
        print(count)
        return -cal_data

    ga = GA(
        func=fitness_func,  # 适应度函数
        n_dim=3,  # 参数数量
        size_pop=20,  # 种群大小
        max_iter=20,  # 迭代次数
        lb=[r[0] for r in param_ranges],  # 参数下界
        ub=[r[1] for r in param_ranges],  # 参数上界
        prob_mut=0.03,  # 变异概率
    )
    best_x, best_y = ga.run()
    print("最优解:", best_x)
    print("最优适应度（原始目标值）:", -best_y)  # 还原为最大化的目标值

    plt.figure()
    plt.plot(ga.generation_best_Y)
    plt.xlabel("迭代次数")
    plt.ylabel("最优适应度")
    plt.show()
    return best_x
