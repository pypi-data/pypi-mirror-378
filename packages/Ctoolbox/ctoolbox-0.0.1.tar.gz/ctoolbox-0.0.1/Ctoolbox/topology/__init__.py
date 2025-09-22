from .config import TopologyConfig
from .core import TopologyCore
from .grouping import GroupManager
from .visualization import TopologyVisualizer

class TopologyGenerator:
    """拓扑生成器主类，整合核心功能、分组管理和可视化"""
    
    def __init__(self, config: TopologyConfig):  # 仅保留config参数
        """初始化拓扑生成器
        
        Args:
            config: 拓扑配置对象，包含行数、列数等所有参数
        """
        self.config = config
        self.core = TopologyCore(self.config)
        self.group_manager = GroupManager(self.core)
        self.visualizer = TopologyVisualizer(self.core, self.group_manager)
    

    # 暴露核心功能接口
    def get_q_positions(self):
        """获取所有Q的位置"""
        return self.core.get_q_positions()
    
    def get_c_positions(self):
        """获取所有C的位置"""
        return self.core.get_c_positions()
    
    def get_q_connections(self, q_id):
        """获取指定Q的连接关系"""
        return self.core.get_q_connections(q_id)
    
    def get_c_connections(self, c_id):
        """获取指定C的连接关系"""
        return self.core.get_c_connections(c_id)
    
    # 暴露分组接口
    def get_q_groups(self):
        """获取4个Q分组"""
        return self.group_manager.get_q_groups()
    
    def get_qc_groups(self):
        """获取16个Q&C组合分组"""
        return self.group_manager.get_qc_groups()
    
    def get_qcq_tight_groups(self):
        """获取4个QCQ_tight分组"""
        return self.group_manager.get_qcq_tight_groups()
    
    def get_qcq_sparse_groups(self):
        """获取16个QCQ_sparse分组"""
        return self.group_manager.get_qcq_sparse_groups()
    
    # 暴露属性设置接口
    def set_q_property(self, q_id, property_name, value):
        """设置Q元素的属性"""
        self.visualizer.set_q_property(q_id, property_name, value)
    
    def set_c_property(self, c_id, property_name, value):
        """设置C元素的属性"""
        self.visualizer.set_c_property(c_id, property_name, value)
    
    # 暴露可视化接口
    def plot_topology(self, *args, **kwargs):
        """绘制拓扑结构"""
        self.visualizer.plot_topology(*args, **kwargs)

# 版本信息
__version__ = "0.0.0"
