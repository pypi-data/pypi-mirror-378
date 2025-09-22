from dataclasses import dataclass

@dataclass
class TopologyConfig:
    """拓扑生成器的配置类，统一管理所有参数"""
    rows: int  # 行数
    cols: int  # 列数
  
    # 默认颜色配置
    q_default_color: tuple = (1, 0.65, 0.6)    # Q默认浅红色
    c_default_color: tuple = (0.65, 0.6, 1)    # C默认浅蓝色
    none_color: tuple = (0.8, 0.8, 0.8)        # 未高亮元素的浅灰色
    
    # 透明度与边框宽度
    q_alpha: float = 1.0
    c_alpha: float = 1.0
    q_edgewidth: float = 1.0
    c_edgewidth: float = 1.0
    
    # 分组高亮默认颜色
    highlight_q_color: tuple = (0.8, 0, 0)          # Q组高亮色
    highlight_qc_q_color: tuple = (0.8, 0, 0)       # QC组Q高亮色
    highlight_qc_c_color: tuple = (0, 0, 0.8)       # QC组C高亮色
    highlight_qcq_q_color: tuple = (0.8, 0, 0)      # QCQ_tight组Q高亮色
    highlight_qcq_c_color: tuple = (0, 0, 0.8)      # QCQ_tight组C高亮色
    highlight_qcq_sparse_q_color: tuple = (0.8, 0, 0)  # QCQ_sparse组Q高亮色
    highlight_qcq_sparse_c_color: tuple = (0, 0, 0.8)  # QCQ_sparse组C高亮色
    
    # 自定义高亮默认颜色
    custom_q_color: tuple = (0.8, 0, 0)
    custom_c_color: tuple = (0, 0, 0.8)

    # 属性热图颜色和范围定义
    custom_colorbar: bool = False
    property_q_color: tuple = (0.8, 0, 0)
    property_c_color: tuple = (0, 0, 0.8)
    q_max_limit: float = 100
    q_min_limit: float = 0
    c_max_limit: float = 100
    c_min_limit: float = 0
    
    # 可视化参数
    font_size: int = 8
    show_colorbar: bool = True
    fig_size: tuple = (12, 11)  # 图像尺寸
