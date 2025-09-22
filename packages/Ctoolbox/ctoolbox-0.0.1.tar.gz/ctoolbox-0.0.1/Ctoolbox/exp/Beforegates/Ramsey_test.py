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
from scipy.fft import fft, fftfreq

def circuit(qubits, if_iso, rotate ,delay,phi, ctx=None):
    circ = init_biasdelay(qubits, if_iso, ctx)
    circ.extend([(('R',0),q) for q in qubits])
    circ.extend([(('Delay',delay),q) for q in qubits])
    circ.extend([(('R',2*np.pi*rotate*delay+phi),q) for q in qubits])
    circ += readout(qubits, if_iso, ctx)
    return circ

def characterize(qubits,delay, phi, rotate,signal,if_iso):
    rcp = Recipe('Ramsey', signal=signal)
    rcp.circuit = circuit
    rcp['qubits'] = tuple(qubits)
    rcp['if_iso'] = if_iso
    rcp['rotate'] = rotate
    rcp['phi'] = phi 
    rcp['delay'] = delay 

    thistask = s.submit(rcp.export(), block=True, preview=[], plot=False)
    thistask.bar(interval=0.05)
    return thistask

def analyze(thistask_rid, fignum1row=7, eachfigsize=(3,2.5), include='all'):
    try:
        result = thistask_rid.result()
        rid = thistask_rid.rid
    except:
        result = get_data_by_rid(thistask_rid)
        rid = thistask_rid
    cfg = get_config_by_rid(rid)
    signal = result['meta']['other']['signal']
    qubits = result['meta']['other']['qubits']
    data = result['data'][signal]
    if include == 'all':
        include = qubits
    fig, axes = universe_plot.creat_fig(include,fignum1row=fignum1row, eachfigsize=eachfigsize)
    fr_info = {}
    fidx = 0

    for qidx, q in enumerate(qubits):
        if q not in include:
            continue
        
        ax = axes[fidx]
        fidx += 1
        ax.set_title(q)
        xaxis = result['meta']['axis']['phi'][f'def']
        delay = result['meta']['other'][f'delay']
        ax.plot(xaxis, np.abs(data[:,qidx]))
        ax.set_xlabel('phi')

    fig.suptitle(f'Ramsey,delay={round(delay*1e9)}ns, rid={rid}',y=0.99)
    fig.tight_layout()
    return fr_info



def sin_fun(x,A,w,phi,B):
    return A*np.sin(2*np.pi*w*x +phi) + B
    
def fit_sin(x,y):
    w0 = estimate_frequency(x, y)[0]
    p0 = [-np.min(y)/2+ np.max(y)/2, w0, 0, np.min(y)/2+ np.max(y)/2]
    para = curve_fit(sin_fun,x,y,p0=p0,maxfev=1000000)[0]
    return para

def estimate_frequency(x, y):
    """使用FFT估计信号的主频率"""
    n = len(y)
    dt = x[1] - x[0]  # 采样间隔
    
    # 计算FFT
    yf = fft(y - np.mean(y))  # 去除直流分量，避免影响频率估计
    xf = fftfreq(n, dt)[:n//2]  # 频率轴（仅取正频率）
    
    # 找到最大功率对应的频率
    power = 2.0/n * np.abs(yf[:n//2])  # 功率谱
    f_estimate = xf[np.argmax(power)]  # 主频率估计
    
    return f_estimate, xf, power