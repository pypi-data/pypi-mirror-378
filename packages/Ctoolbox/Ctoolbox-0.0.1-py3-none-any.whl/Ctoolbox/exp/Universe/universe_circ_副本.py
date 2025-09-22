# created by HJX, @20250825
all_qubits = [f"Q{q}" for q in range(112)]
all_couplers = [f"QC{c}" for c in range(195)]
all_QC = all_qubits +  all_couplers

delay_after_firstsetbias = 10e-6
delay_before_readbias = 200e-9
delay_after_readbias = 200e-9
delay_after_measure = 200e-9
delay_after_finishbias = 1e-6

def init_iso(iso_QC, ctx):
    circ = [
        *[(('Delay', -1), qc) for qc in iso_QC],
        *[(("setBias", 'flux', ctx.query(f'{qc}.caliinfo.isobias')), qc) for qc in iso_QC],
        *[(('Delay', 1), qc) for qc in iso_QC]
    ]
    return circ

def init_idle(qubits, ctx):
    circ = [
        *[(('Delay', -1), q) for q in qubits],
        *[(("setBias", 'flux', ctx.query(f'{q}.caliinfo.idlebias')), q) for q in qubits],
        *[(('Delay', 1), q) for q in qubits]
    ]
    return circ

def init_biasdelay(qubits, if_iso, ctx=None):
    if if_iso:
        iso_QC = [qc for qc in all_QC if qc not in qubits]
        circ = init_idle(qubits,ctx)
        circ += init_iso(iso_QC,ctx)
    else:
        circ = init_idle(all_QC,ctx)
    circ += [(('Delay', delay_after_firstsetbias), qc) for qc in all_QC]
    circ += [('Barrier',tuple(all_QC))]
    return circ

def set_read_bias(qubits, if_iso, ctx):
    if if_iso:
        iso_QC = [qc for qc in all_QC if qc not in qubits]
        circ = [(("setBias", 'flux', ctx.query(f'{q}.caliinfo.readbias')), q) for q in qubits]
        circ += [(("setBias", 'flux', ctx.query(f'{qc}.caliinfo.isobias')), qc) for qc in iso_QC]
    else:
        circ = [(("setBias", 'flux', ctx.query(f'{qc}.caliinfo.readbias')), qc) for qc in all_QC]
    return circ

def finish_read_bias(qubits, if_iso, ctx):
    if if_iso:
        iso_QC = [qc for qc in all_QC if qc not in qubits]
        circ = [(("setBias", 'flux', ctx.query(f'{q}.caliinfo.idlebias')), q) for q in qubits]
        circ += [(("setBias", 'flux', ctx.query(f'{qc}.caliinfo.isobias')), qc) for qc in iso_QC]
    else:
        circ = [(("setBias", 'flux', ctx.query(f'{qc}.caliinfo.idlebias')), qc) for qc in all_QC]
    return circ

def readout(qubits, if_iso, ctx):
    circ = [
        ('Barrier',tuple(all_QC)),
        *[(('Delay',delay_before_readbias),q) for q in  qubits],
        ('Barrier',tuple(all_QC)),
    ]
    circ += set_read_bias(qubits, if_iso, ctx)
    circ += [(('Delay',delay_after_readbias),q) for q in  qubits]
    circ += [(("Measure", idx), q) for idx, q in enumerate(qubits)]
    circ += [(('Delay',delay_after_measure),q) for q in  qubits]
    circ += finish_read_bias(qubits, if_iso, ctx)
    circ += [(('Delay',delay_after_finishbias),q) for q in  qubits]
    return circ
