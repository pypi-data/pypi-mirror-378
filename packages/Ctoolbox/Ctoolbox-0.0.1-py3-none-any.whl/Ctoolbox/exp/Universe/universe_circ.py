# Created by HJX, @20250825

# 定义量子比特和耦合器列表
all_qubits = [f"Q{q}" for q in range(112)]
all_couplers = [f"QC{c}" for c in range(195)]
all_QC = all_qubits + all_couplers

# 定义各类延迟参数（单位：秒）
DELAY_AFTER_FIRST_SET_BIAS = 10e-6
DELAY_BEFORE_READ_BIAS = 200e-9
DELAY_AFTER_READ_BIAS = 200e-9
DELAY_AFTER_MEASURE = 200e-9
DELAY_AFTER_FINISH_BIAS = 1e-6


def init_iso(iso_QC, ctx):
    """初始化隔离区量子元件"""
    return [
        *[(('Delay', -1), qc) for qc in iso_QC],
        *[(("setBias", 'flux', ctx.query(f'{qc}.caliinfo.isobias')), qc) for qc in iso_QC],
        *[(('Delay', 1), qc) for qc in iso_QC]
    ]


def init_idle(qubits, ctx):
    """初始化空闲状态量子比特"""
    return [
        *[(('Delay', -1), q) for q in qubits],
        *[(("setBias", 'flux', ctx.query(f'{q}.caliinfo.idlebias')), q) for q in qubits],
        *[(('Delay', 1), q) for q in qubits]
    ]


def init_biasdelay(qubits, if_iso, ctx=None):
    """初始化偏置延迟"""
    if if_iso:
        # 隔离模式：区分活跃量子比特和隔离区元件
        iso_QC = [qc for qc in all_QC if qc not in qubits]
        circ = init_idle(qubits, ctx)
        circ += init_iso(iso_QC, ctx)
    else:
        # 非隔离模式：所有元件均设为空闲状态
        circ = init_idle(all_QC, ctx)
    
    # 添加公共延迟和屏障
    circ += [(('Delay', DELAY_AFTER_FIRST_SET_BIAS), qc) for qc in all_QC]
    circ += [('Barrier', tuple(all_QC))]
    
    return circ


def set_read_bias(qubits, if_iso, ctx):
    """设置读取偏置"""
    if if_iso:
        # 隔离模式：分别设置活跃量子比特和隔离区元件
        iso_QC = [qc for qc in all_QC if qc not in qubits]
        circ = [(("setBias", 'flux', ctx.query(f'{q}.caliinfo.readbias')), q) for q in qubits]
        circ += [(("setBias", 'flux', ctx.query(f'{qc}.caliinfo.isobias')), qc) for qc in iso_QC]
    else:
        # 非隔离模式：所有元件均设置为读取偏置
        circ = [(("setBias", 'flux', ctx.query(f'{qc}.caliinfo.readbias')), qc) for qc in all_QC]
    
    return circ


def finish_read_bias(qubits, if_iso, ctx):
    """结束读取偏置，恢复空闲状态"""
    if if_iso:
        # 隔离模式：分别恢复活跃量子比特和隔离区元件
        iso_QC = [qc for qc in all_QC if qc not in qubits]
        circ = [(("setBias", 'flux', ctx.query(f'{q}.caliinfo.idlebias')), q) for q in qubits]
        circ += [(("setBias", 'flux', ctx.query(f'{qc}.caliinfo.isobias')), qc) for qc in iso_QC]
    else:
        # 非隔离模式：所有元件均恢复为空闲偏置
        circ = [(("setBias", 'flux', ctx.query(f'{qc}.caliinfo.idlebias')), qc) for qc in all_QC]
    
    return circ


def readout(qubits, if_iso, ctx):
    """执行读取操作序列"""
    circ = [
        ('Barrier', tuple(all_QC)),
        *[(('Delay', DELAY_BEFORE_READ_BIAS), q) for q in qubits],
        ('Barrier', tuple(all_QC)),
    ]
    
    # 添加读取偏置设置、测量操作和恢复操作
    circ += set_read_bias(qubits, if_iso, ctx)
    circ += [(('Delay', DELAY_AFTER_READ_BIAS), q) for q in qubits]
    circ += [(("Measure", idx), q) for idx, q in enumerate(qubits)]
    circ += [(('Delay', DELAY_AFTER_MEASURE), q) for q in qubits]
    circ += finish_read_bias(qubits, if_iso, ctx)
    circ += [(('Delay', DELAY_AFTER_FINISH_BIAS), q) for q in qubits]
    
    return circ
