import numpy as np
from itertools import product
from collections import defaultdict

class QSTReconstructor:
    """量子态层析重构器：输入测量数据，输出重构的密度矩阵"""
    
    def __init__(self, n_qubits):
        self.n_qubits = n_qubits
        self.core_ops = self.get_core_operators(n_qubits)
        self.all_ops = self.generate_pauli_operators(n_qubits)

    # 生成所有泡利算符张量积（字符串标签）
    def generate_pauli_operators(self, n_qubits):
        pauli = ['I', 'X', 'Y', 'Z']
        all_combinations = product(pauli, repeat=n_qubits)
        return [''.join(combo) for combo in all_combinations]

    # 获取核心算符（不含'I'）
    def get_core_operators(self, n_qubits):
        core_pauli = ['X', 'Y', 'Z']
        core_combinations = product(core_pauli, repeat=n_qubits)
        return [''.join(combo) for combo in core_combinations]

    # 获取单量子比特泡利算符矩阵
    def get_pauli_matrix(self, op):
        if op == 'I':
            return np.array([[1, 0], [0, 1]])
        elif op == 'X':
            return np.array([[0, 1], [1, 0]])
        elif op == 'Y':
            return np.array([[0, -1j], [1j, 0]])
        elif op == 'Z':
            return np.array([[1, 0], [0, -1]])

    # 生成泡利算符张量积矩阵
    def generate_pauli_tensor(self, op_str):
        tensor = np.array([[1]], dtype=np.complex128)
        for c in op_str:
            tensor = np.kron(tensor, self.get_pauli_matrix(c))
        return tensor

    # 按照从左到右的比特编号提取结果
    def get_eigenvalues_for_op(self, op_str):
        n_qubits = self.n_qubits
        num_states = 2** n_qubits
        eigenvalues = np.ones(num_states)
        
        for state_idx in range(num_states):
            eigenvalue = 1.0
            for qubit_idx in range(n_qubits):  # qubit_idx=0→最左，3→最右
                op = op_str[qubit_idx]
                if op == 'I':
                    continue
                
                # 计算从左数第qubit_idx位对应的二进制位移
                shift = (n_qubits - 1) - qubit_idx
                bit = (state_idx >> shift) & 1
                eigenvalue *= 1 if bit == 0 else -1
            
            eigenvalues[state_idx] = eigenvalue
        
        return eigenvalues

    # 生成期望值提取映射规则
    def generate_mappings(self):
        mappings = defaultdict(list)
        n_qubits = self.n_qubits
        
        for op in self.all_ops:
            non_i_info = [(i, char) for i, char in enumerate(op) if char != 'I']
            
            if not non_i_info:  # 全I算符
                mappings[op] = [('CONSTANT', lambda: 1.0)]
            
            elif len(non_i_info) == n_qubits:  # 核心算符（无I）
                eigenvalues = self.get_eigenvalues_for_op(op)
                
                def create_func(eigenvalues):
                    def func(pops):
                        return np.sum(eigenvalues * pops)
                    return func
                
                mappings[op].append((op, create_func(eigenvalues)))
            
            else:  # 含I算符（如IIIX）
                eigenvalues = self.get_eigenvalues_for_op(op)
                
                # 仅匹配非I位置完全一致的核心算符
                for core_op in self.core_ops:
                    match = True
                    for i, target_char in non_i_info:
                        if core_op[i] != target_char:
                            match = False
                            break
                    if match:
                        def create_func(eigenvalues):
                            def func(pops):
                                return np.sum(eigenvalues * pops)
                            return func
                        
                        mappings[op].append((core_op, create_func(eigenvalues)))
        
        return mappings

    # 提取期望值
    def extract_expectations(self, measurement_array):
        n_qubits = self.n_qubits
        num_core = len(self.core_ops)
        num_states = 2 **n_qubits
        
        # 验证输入形状是否为 (3ⁿ, 2ⁿ)
        if measurement_array.shape != (num_core, num_states):
            raise ValueError(
                f"输入数组形状应为 ({num_core}, {num_states})，实际为 {measurement_array.shape}"
            )
        
        measurement_data = {}
        for i in range(num_core):
            pops = measurement_array[i].copy()
            pops[pops < 0] = 0.0  # 处理负数概率
            pop_sum = np.sum(pops)
            if pop_sum == 0:
                pops = np.ones_like(pops) / num_states
            else:
                pops = pops / pop_sum
            measurement_data[self.core_ops[i]] = pops
        
        mappings = self.generate_mappings()
        expectations = {}
        for op, rules in mappings.items():
            values = []
            for source, func in rules:
                if source == 'CONSTANT':
                    values.append(func())
                else:
                    if source in measurement_data:
                        values.append(func(measurement_data[source]))
            
            expectations[op] = np.mean(values) if values else 0.0
        
        return expectations

    # 重构密度矩阵（带后处理约束）
    def reconstruct_density_matrix(self, expectations):
        n_qubits = self.n_qubits
        dim = 2** n_qubits  # 密度矩阵维度
        rho = np.zeros((dim, dim), dtype=np.complex128)
        scale = 1.0 / (4 ** n_qubits)  # 泡利展开的归一化系数
        
        # 构建初始密度矩阵（泡利算符线性组合）
        for op_str in self.all_ops:
            exp_val = expectations.get(op_str, 0.0)  # 期望值
            op_tensor = self.generate_pauli_tensor(op_str)  # 泡利张量积
            rho += exp_val * op_tensor
        
        rho *= scale  # 应用归一化系数
        
        # 后处理修正物理约束
        # 约束1：强制厄米性
        rho = (rho + rho.conj().T) / 2
        
        # 约束2：迹归一化
        current_trace = np.trace(rho)
        if not np.isclose(current_trace, 0.0, atol=1e-10):
            rho = rho / current_trace
        else:
            rho = np.eye(dim) / dim  # 极端情况：最大混合态
        
        # # 约束3：半正定性
        # eigenvalues, eigenvectors = np.linalg.eigh(rho)
        # eigenvalues = np.maximum(eigenvalues, -1e-10)  # 截断负特征值
        # eigenvalues = eigenvalues / np.sum(eigenvalues)  # 重新归一化
        # rho = eigenvectors @ np.diag(eigenvalues) @ eigenvectors.conj().T
        
        return rho

    # 主函数：输入测量数据，输出重构的rho
    def process(self, measurement_array):
        """
        输入：shape为 (3ⁿ, 2ⁿ) 的测量数据数组
        输出：重构好的密度矩阵 rho
        """
        expectations = self.extract_expectations(measurement_array)
        rho = self.reconstruct_density_matrix(expectations)
        return rho


# 保真度计算函数（保持与你的代码一致）
def state_fidelity(rho1, rho2):
    """计算两个密度矩阵之间的保真度"""
    product = np.dot(rho1, rho2)
    fidelity = np.trace(product)
    return fidelity.real
