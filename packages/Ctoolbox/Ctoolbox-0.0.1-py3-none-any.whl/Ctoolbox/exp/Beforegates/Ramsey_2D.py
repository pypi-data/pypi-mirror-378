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
from scipy.signal import find_peaks

def circuit(qubits, if_iso, rotate,flux ,delay,phi, ctx=None):
    circ = init_biasdelay(qubits, if_iso, ctx)
    circ.extend([(('R',0),q) for q in qubits])
    circ.extend([(("setBias", 'flux', flux), q) for q in qubits])
    circ.extend([(('Delay',delay),q) for q in qubits])
    circ.extend([(("setBias", 'flux', ctx.query(f'{q}.caliinfo.idlebias')), q) for q in qubits])
    circ.extend([(('R',2*np.pi*rotate*delay+phi),q) for q in qubits])
    circ += readout(qubits, if_iso, ctx)
    return circ

def characterize(qubits,flux_st, flux_ed, flux_points,delay,rotate,signal,if_iso, phi=0):
    rcp = Recipe('Ramsey', signal=signal)
    rcp.circuit = circuit
    rcp['qubits'] = tuple(qubits)
    rcp['if_iso'] = if_iso
    rcp['rotate'] = rotate
    rcp['flux'] = np.linspace(flux_st, flux_ed, flux_points)
    rcp['delay'] = delay
    rcp['phi'] = phi 

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
    T2 = {}
    fidx = 0
    for qidx, q in enumerate(qubits):
        if q not in include:
            continue
        
        ax = axes[fidx]
        fidx += 1
        ax.set_title(q)
        xaxis = result['meta']['axis']['delay'][f'def']*1e6
        yaxis = result['meta']['axis']['flux'][f'def']
        extent = universe_plot.get_extent(yaxis, xaxis)
        ax.imshow(np.abs(data[:,:,qidx]).T,extent=extent,origin='lower',interpolation='none',aspect='auto')

    fig.suptitle(f'Ramsey, rid={rid}',y=0.99)
    fig.tight_layout()
    return fr_info, T2



def sin_fun(x,A,w,phi,B):
    return A*np.sin(2*np.pi*w*x +phi) + B

def dephasing_fun(x,t2,A,w,phi,B):
    return A*np.sin(2*np.pi*w*x +phi)*np.exp(-t2/x) + B
    
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



# 定义Ramsey序列的T2信号模型
def ramsey_model(tau, s0, t2, f0, phi,B):
    return s0 * np.exp(-tau / t2) * np.cos(2 * np.pi * f0 * tau + phi)+B

def estimate_initial_parameters(tau, signal):
    s0_guess = np.max(np.abs(signal))
    envelope = np.abs(signal)
    threshold = envelope[0] / np.e
    valid_idx = np.where(envelope >= threshold)[0]
    if len(valid_idx) > 0:
        t2_guess = tau[valid_idx[-1]] * 1.5  # 适当放大作为初始猜测
    else:
        t2_guess = np.max(tau) / 2  # 若无法找到阈值点，取最大时间的一半
    
    # 用FFT估算振荡频率f0
    n = len(tau)
    dt = np.mean(np.diff(tau))  # 时间间隔(ms)
    yf = fft(envelope * signal)  # 加权FFT，突出强信号成分
    xf = fftfreq(n, dt)[:n//2]   # 频率轴(kHz，因dt单位为ms，1/ms=1000Hz=1kHz)
    f0_guess = np.abs(xf[np.argmax(np.abs(yf[:n//2]))])
    
    # 初始相位默认设为0
    phi_guess = 0.0
    B = np.max(signal)/2 + np.min(signal)
    
    return [s0_guess, t2_guess, f0_guess, phi_guess,B]

def t1_model_iq(ti, t1, s0, b):
    return s0 * np.exp(-ti / t1) + b

def fit_t1(ti, y, signal='iq_avg'):
    t1_guess = -1/np.polyfit(ti, y-np.min(y),1)[0]
    s0_guess = np.max(abs(y))
    b_guess = np.min(abs(y))

    initial_guess = [t1_guess,s0_guess,b_guess]
    popt, pcov = curve_fit(t1_model_iq, ti, y, p0=initial_guess, 
                            bounds=([0, 0,-np.inf], [np.inf, np.inf, np.inf]))  # 确保参数为正值
    return popt, t1_model_iq

def envelope_peak_detection(signal, x=None, order=3):
    if x is None:
        x = np.arange(len(signal))
    
    # 检测上峰值（极大值）
    upper_peaks, _ = find_peaks(signal)
    
    # 确保包络覆盖整个信号范围（添加首尾点）
    upper_x = np.concatenate([[x[0]], x[upper_peaks], [x[-1]]])
    upper_y = np.concatenate([[signal[0]], signal[upper_peaks], [signal[-1]]])
    para,func = fit_t1(upper_x, upper_y, signal)
    fifdata = func(x,*para)
    
    return  x, fifdata,para