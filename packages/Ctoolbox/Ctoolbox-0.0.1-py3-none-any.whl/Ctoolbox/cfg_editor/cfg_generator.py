import json
import pprint
from typing import Dict, List, Any, Optional
from pathlib import Path

class ConfigGenerator:
    """配置表生成器，用于生成包含设备、量子比特等信息的配置字典
    
    提供一系列方法用于构建完整的配置表，包括站点信息、设备信息、
    量子比特信息、耦合器信息等，并支持导出为JSON文件。
    """
    
    def __init__(self):
        """初始化配置生成器，创建空配置字典"""
        self.cfg_dict: Dict[str, Any] = {}

    def generate_station(self, sample_name: str, trigdev_name: str) -> "ConfigGenerator":
        """生成站点信息配置
        
        Args:
            sample_name: 样品名称
            trigdev_name: 触发设备名称
            
        Returns:
            配置生成器实例（支持链式调用）
        """
        self.cfg_dict['station'] = {
            'sample': sample_name,
            'triggercmds': [f'{trigdev_name}.CH1.TRIG'],
            'triggerClockCycle': 16e-9,
            'waveform_length': 99e-6,
            'shots': 1024,
            'lib': 'lib.gates.u3rcp',
            'arch': 'rcp',
            'align_right': False,
            'auto_clear': {
                'init': [],
                'main': ['drive','drive','probe'],
                'post': ['flux','drive','probe'],
            }
        }
        return self

    def generate_dev(self, devinfo_dict: Dict[str, List[tuple]]) -> "ConfigGenerator":
        """生成设备信息配置
        
        根据设备类型字典，更新配置中的设备信息
        
        Args:
            devinfo_dict: 设备信息字典，键为设备类型，值为设备地址列表
            
        Returns:
            配置生成器实例（支持链式调用）
        """
        if 'dev' not in self.cfg_dict:
            self.cfg_dict['dev'] = {}
            
        # 设备类型与基础配置的映射关系
        dev_type_mappings = {
            'ChipQ': {
                'base_dict': {
                    'host': '', 'port': '', 'type': 'remote', 
                    'srate': -1, 'inuse': True
                },
                'fields': ['host', 'port']  # 对应addrlist中的位置
            },
            'rNS': {
                'base_dict': {
                    'host': '', 'port': '', 'type': 'remote', 
                    'srate': -1, 'inuse': True
                },
                'fields': ['host', 'port']
            },
            'driverdev': {
                'base_dict': {
                    'addr': '', 'name': '', 'type': 'driver', 
                    'srate': -1, 'inuse': True
                },
                'fields': ['addr', 'name']
            },
            'NA': {
                'base_dict': {
                    'addr': '', 'name': 'NetworkAnalyzer', 'type': 'driver',
                    'model': '', 'srate': -1, 'inuse': True
                },
                'fields': ['addr', 'model']
            }
        }
        
        # 处理每种设备类型
        for devtype, addrlist in devinfo_dict.items():
            if devtype not in dev_type_mappings:
                raise ValueError(f"不支持的设备类型: {devtype}")
                
            mapping = dev_type_mappings[devtype]
            self._update_device(mapping['base_dict'], mapping['fields'], addrlist)
            
        return self

    def _update_device(self, base_dict: Dict[str, Any], 
                      fields: List[str], 
                      addrlist: List[tuple]) -> None:
        """通用设备更新方法，提取重复逻辑
        
        Args:
            base_dict: 设备基础配置字典
            fields: 需要从addrlist更新的字段列表
            addrlist: 设备地址信息列表，每个元素为(设备名, 字段1, 字段2, ...)
        """
        for item in addrlist:
            dev_name = item[0]
            # 创建基础配置的副本
            dev_config = base_dict.copy()
            # 更新字段值
            for i, field in enumerate(fields, start=1):
                dev_config[field] = item[i]
            # 添加到配置中
            self.cfg_dict['dev'][dev_name] = dev_config

    def update_Q(self, Qinfo_dict: Dict[str, Dict[str, str]], topology: Any) -> "ConfigGenerator":
        """更新量子比特(Q)配置信息
        
        Args:
            Qinfo_dict: 量子比特信息字典
            topology: 拓扑结构对象，用于获取连接信息
            
        Returns:
            配置生成器实例（支持链式调用）
        """
        for qubit, info in Qinfo_dict.items():
            qidx = int(qubit[1:])  # 从"Q0"提取索引0
            connections = topology.get_q_connections(qidx)
            
            # 构建量子比特基础配置
            q_config = {
                'probe': {
                    'address': f"{info['probe_channel']}.Waveform",
                    'delay': 0
                },
                'acquire': {
                    'address': f"{info['acquire_channel']}.IQ",
                    'TRIGD': 0
                },
                'drive': {
                    'address': f"{info['drive_channel']}.Waveform",
                    'delay': 0
                },
                'flux': {
                    'address': f"{info['flux_channel']}.Waveform",
                    'delay': 0,
                    'distortion': {
                        'decay': [],
                        'expfit': [],
                        'multfit': []
                    }
                },
                'R': {
                    'shape': 'cosPulse',
                    'frequency': 4e9,
                    'amp': 0.2,
                    'width': 2e-8,
                    'plateau': 0,
                    'eps': 1,
                    'buffer': 0,
                    'alpha': 1,
                    'beta': 0,
                    'delta': 0,
                    'block_freq': None,
                    'tab': 0.5,
                },
                'R12': {
                    'shape': 'cosPulse',
                    'frequency': 3.8e9,
                    'amp': 0.2,
                    'width': 2e-8,
                    'plateau': 0,
                    'eps': 1,
                    'buffer': 0,
                    'alpha': 1,
                    'beta': 0,
                    'delta': 0,
                    'block_freq': None,
                    'tab': 0.5,
                },
                'Measure': {
                    'frequency': 7e9,
                    'duration': 1.8e-6,
                    'amp': 0.08,
                    'ring_up_amp': 0.04,
                    'ring_up_time': 50e-9,
                    'rsing_edge_time': 5e-9,
                    'buffer': 0,
                    'space': 0,
                    'weight': 'square(1800e-9)>>900e-9',
                    'bias': None,
                    'signal': 'state',
                    'threshold': 0,
                    'phi': 0,
                    'PgPe': [0, 1],
                },
                'caliinfo': {
                    'sweetbias': 0,
                    'idlebias': 0,
                    'isobias': 0,
                    'readbias': 0,
                    'spectrum2D': [],     
                },
                'topoinfo': {
                    'couplers': [f'Q{c}' for c in connections['NC']],
                    'NQ': connections['NQ'],
                    'HNNQ': connections['HNNQ'],
                    'VNNQ': connections['VNNQ']
                },
                'params': {
                    'T1': 0,
                    'T2_star': 0,
                    'T2_echo': 0,
                    '1Qfidelity': 0,
                    'Readfidelity_g': 0,
                    'Readfidelity_e': 0
                }
            }
            
            self.cfg_dict[qubit] = q_config
            
        return self

    def update_QC(self, QCinfo_dict: Dict[str, Dict[str, str]], topology: Any) -> "ConfigGenerator":
        """更新耦合器(QC)配置信息
        
        Args:
            QCinfo_dict: 耦合器信息字典
            topology: 拓扑结构对象，用于获取连接信息
            
        Returns:
            配置生成器实例（支持链式调用）
        """
        for coupler, info in QCinfo_dict.items():
            qc_idx = int(coupler[2:])  # 从"QC0"提取索引0
            connections = topology.get_c_connections(qc_idx)
            
            # 构建耦合器基础配置
            qc_config = {
                'flux': {
                    'address': f"{info['flux_channel']}.Waveform",
                    'delay': 0,
                    'distortion': {
                        'decay': [],
                        'expfit': [],
                        'multfit': []
                    }
                },
                'caliinfo': {
                    'sweetbias': 0,
                    'idlebias': 0,
                    'isobias': 0,
                    'readbias': 0,
                    'spectrum2D': [],     
                },
                'topoinfo': {
                    'qubits': connections['NQ'],
                },
            }
            
            self.cfg_dict[coupler] = qc_config
            
        return self

    def update_QQ(self, topology: Any) -> "ConfigGenerator":
        """更新量子比特间连接(QQ)配置信息
        
        Args:
            topology: 拓扑结构对象，用于获取连接组信息
            
        Returns:
            配置生成器实例（支持链式调用）
        """
        # 获取所有QCQ组
        qcq_groups = topology.get_qcq_tight_groups()
        qcq_group_all = [group for sublist in qcq_groups for group in sublist]
        
        # 处理前两个组
        for qcq in qcq_group_all[:2]:
            coupler = f'Q{qcq[0]}'
            group_name = f'{qcq[1][0]}_{qcq[1][1]}'
            
            self.cfg_dict[group_name] = {
                'coupler': coupler,
                'CZ': {},
                'iSWAP': {},
                'fsim': {}
            }
            
        return self

    @staticmethod
    def instantiate_topology(rows: int, cols: int, 
                            topology_path: Optional[str] = None) -> Any:
        """实例化拓扑生成器
        
        Args:
            rows: 芯片比特行数
            cols: 每行比特数量
            topology_path: 拓扑生成器所在路径，默认为None使用系统路径
            
        Returns:
            实例化的拓扑生成器对象
        """
        import sys
        # 如果提供了路径，添加到系统路径
        if topology_path:
            sys.path.append(str(Path(topology_path).resolve()))
        else:
            # 可根据实际情况调整默认路径
            default_path = Path(__file__).parent.parent / "toolbox/Cloud_exp/home"
            sys.path.append(str(default_path.resolve()))
        
        # 导入拓扑生成器
        from Ctoolbox.topology import TopologyGenerator, TopologyConfig
        
        # 自定义拓扑配置
        custom_config = TopologyConfig(
            rows=rows,
            cols=cols,
            q_default_color=(0.95, 0.7, 0.7),    # Q默认浅红色
            c_default_color=(0.7, 0.7, 0.95),    # C默认浅蓝色
            none_color=(0.8, 0.8, 0.8),          # 未高亮元素的浅灰色
            q_alpha=1.0,
            c_alpha=1.0,
            q_edgewidth=1.0,
            c_edgewidth=1.0,
            highlight_q_color=(0.9, 0, 0),
            highlight_qc_q_color=(0.9, 0, 0),
            highlight_qc_c_color=(0, 0, 0.9),
            highlight_qcq_q_color=(0.9, 0, 0),
            highlight_qcq_c_color=(0, 0, 0.9),
            highlight_qcq_sparse_q_color=(0.9, 0, 0),
            highlight_qcq_sparse_c_color=(0, 0, 0.9),
            custom_q_color=(0.9, 0, 0),
            custom_c_color=(0, 0, 0.9),
            custom_colorbar=True,
            property_q_color=(0.9, 0, 0),
            property_c_color=(0, 0, 0.9),
            q_max_limit=60,
            q_min_limit=10,
            c_max_limit=80,
            c_min_limit=10,
            font_size=9,
            show_colorbar=True,
            fig_size=(12, 11),
        )
        
        return TopologyGenerator(config=custom_config)

    def save_to_file(self, file_path: str) -> "ConfigGenerator":
        """将配置字典保存为JSON文件
        
        Args:
            file_path: 保存文件路径
            
        Returns:
            配置生成器实例（支持链式调用）
        """
        with open(file_path, 'w') as f:
            json.dump(self.cfg_dict, f, indent=2)
        return self

    def get_config(self) -> Dict[str, Any]:
        """获取当前配置字典
        
        Returns:
            当前配置字典
        """
        return self.cfg_dict

    def print_config(self) -> "ConfigGenerator":
        """打印当前配置字典
        
        Returns:
            配置生成器实例（支持链式调用）
        """
        pprint.pprint(self.cfg_dict)
        return self
