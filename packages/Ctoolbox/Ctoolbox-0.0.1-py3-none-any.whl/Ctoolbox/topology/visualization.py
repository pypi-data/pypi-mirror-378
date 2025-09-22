import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
from typing import List, Set, Dict, Any, Union, Optional
from .core import TopologyCore
from .grouping import GroupManager
from .utils import extract_highlight_ids, get_text_color, validate_group_number
from .config import TopologyConfig

class TopologyVisualizer:
    """拓扑结构可视化器，负责绘制拓扑结构和分组高亮"""
    
    def __init__(self, core: TopologyCore, group_manager: GroupManager):
        """初始化可视化器
        
        Args:
            core: 拓扑核心对象
            group_manager: 分组管理器
        """
        self.core = core
        self.group_manager = group_manager
        self.config = core.config
        
        # 属性存储
        self.q_properties: Dict[int, Dict] = {q_id: {} for q_id in core.get_q_positions()}
        self.c_properties: Dict[int, Dict] = {c_id: {} for c_id in core.get_c_positions()}
    
    def set_q_property(self, q_id: int, property_name: str, value: Any) -> None:
        """设置Q元素的属性
        
        Args:
            q_id: Q元素ID
            property_name: 属性名称
            value: 属性值
        """
        if q_id not in self.q_properties:
            raise ValueError(f"Q ID {q_id} 不存在")
        self.q_properties[q_id][property_name] = value
    
    def set_c_property(self, c_id: int, property_name: str, value: Any) -> None:
        """设置C元素的属性
        
        Args:
            c_id: C元素ID
            property_name: 属性名称
            value: 属性值
        """
        if c_id not in self.c_properties:
            raise ValueError(f"C ID {c_id} 不存在")
        self.c_properties[c_id][property_name] = value
    
    def plot_topology(
        self, 
        property_type: Optional[str] = None, 
        target: str = 'both', 
        highlight_group: Optional[int] = None,
        highlight_qc_group: Optional[int] = None,
        highlight_qs: Optional[List[str]] = None,
        highlight_cs: Optional[List[str]] = None,
        highlight_qcq_tight: Optional[int] = None,
        highlight_qcq_sparse: Optional[int] = None,
        custom_q_color: Optional[tuple] = None,
        custom_c_color: Optional[tuple] = None
    ) -> None:


        """绘制拓扑结构，支持多种高亮模式
        
        Args:
            property_type: 按指定属性值着色，默认为None（使用默认颜色）
            target: 绘制目标，'q'（仅Q）、'c'（仅C）或'both'（两者都绘制）
            highlight_group: 高亮Q组（1-4），默认为None
            highlight_qc_group: 高亮Q&C组（1-16），默认为None
            highlight_qs: 自定义高亮Q列表（如['Q0', 'Q3']），默认为None
            highlight_cs: 自定义高亮C列表（如['C1', 'C5']），默认为None
            highlight_qcq_tight: 高亮QCQ_tight组（1-4），默认为None
            highlight_qcq_sparse: 高亮QCQ_sparse组（1-16），默认为None
            custom_q_color: 自定义Q高亮颜色，默认为None（使用配置中的默认值）
            custom_c_color: 自定义C高亮颜色，默认为None（使用配置中的默认值）
        """
        # 初始化高亮ID集合
        highlighted_q_ids: Set[int] = set()
        highlighted_c_ids: Set[int] = set()
        highlight_mode = 'none'  # 默认非高亮模式
        
        # 解析自定义颜色（如未提供则使用配置中的默认值）
        custom_q_color = custom_q_color or self.config.custom_q_color
        custom_c_color = custom_c_color or self.config.custom_c_color
        
        # 1. 处理自定义Q/C高亮（最高优先级）
        if (highlight_qs is not None) or (highlight_cs is not None):
            highlight_mode = 'custom'
            # 解析自定义Q列表
            if highlight_qs is not None:
                for q_label in highlight_qs:
                    try:
                        q_id = int(q_label[1:])  # 提取Q的ID数字
                        if q_id in self.core.get_q_positions():
                            highlighted_q_ids.add(q_id)
                    except (ValueError, IndexError):
                        raise ValueError(f"Q标签格式错误：{q_label}，应为'Q+数字'格式（如'Q0'）")
            
            # 解析自定义C列表
            if highlight_cs is not None:
                for c_label in highlight_cs:
                    try:
                        c_id = int(c_label[1:])  # 提取C的ID数字
                        if c_id in self.core.get_c_positions():
                            highlighted_c_ids.add(c_id)
                    except (ValueError, IndexError):
                        raise ValueError(f"C标签格式错误：{c_label}，应为'C+数字'格式（如'C0'）")
        
        # 2. 处理QCQ_sparse分组高亮
        elif highlight_qcq_sparse is not None:
            validate_group_number(highlight_qcq_sparse, 0, 15, "highlight_qcq_sparse")
            group_idx = highlight_qcq_sparse
            qcq_group = self.group_manager.get_qcq_sparse_groups()[group_idx]
            
            highlighted_c_ids = extract_highlight_ids(qcq_group, 'C')
            # 提取Q的ID
            for item in qcq_group:
                if isinstance(item, list) and len(item) > 1 and isinstance(item[1], tuple):
                    for q_label in item[1]:
                        if q_label.startswith('Q'):
                            try:
                                q_id = int(q_label[1:])
                                if q_id in self.core.get_q_positions():
                                    highlighted_q_ids.add(q_id)
                            except ValueError:
                                continue
            highlight_mode = 'qcq_sparse'
        
        # 3. 处理QCQ_tight分组高亮
        elif highlight_qcq_tight is not None:
            validate_group_number(highlight_qcq_tight, 0, 3, "highlight_qcq_tight")
            group_idx = highlight_qcq_tight
            qcq_group = self.group_manager.get_qcq_tight_groups()[group_idx]
            
            highlighted_c_ids = extract_highlight_ids(qcq_group, 'C')
            # 提取Q的ID
            for item in qcq_group:
                if isinstance(item, list) and len(item) > 1 and isinstance(item[1], tuple):
                    for q_label in item[1]:
                        if q_label.startswith('Q'):
                            try:
                                q_id = int(q_label[1:])
                                if q_id in self.core.get_q_positions():
                                    highlighted_q_ids.add(q_id)
                            except ValueError:
                                continue
            highlight_mode = 'qcq_tight'
        
        # 4. 处理Q&C组高亮
        elif highlight_qc_group is not None:
            validate_group_number(highlight_qc_group, 0, 15, "highlight_qc_group")
            group_idx = highlight_qc_group
            qc_group = self.group_manager.get_qc_groups()[group_idx]
            
            highlighted_q_ids = {int(q_label[1:]) for q_label in qc_group['Q']}
            highlighted_c_ids = {int(c_label[1:]) for c_label in qc_group['C']}
            highlight_mode = 'qc'
        
        # 5. 处理Q组高亮（最低优先级）
        elif highlight_group is not None:
            validate_group_number(highlight_group, 0, 3, "highlight_group")
            group_idx = highlight_group
            group_members = self.group_manager.get_q_groups()[group_idx]
            highlighted_q_ids = {int(q_label[1:]) for q_label in group_members}
            highlight_mode = 'q'
        
        # 创建热图（仅非高亮模式使用）
        if self.config.custom_colorbar:
            q_cmap = LinearSegmentedColormap.from_list(
                "white_to_qcolor", [(1, 1, 1), self.config.property_q_color]
            )
            c_cmap = LinearSegmentedColormap.from_list(
                "white_to_ccolor", [(1, 1, 1), self.config.property_c_color]
            )
        else:
            q_cmap = LinearSegmentedColormap.from_list(
                "white_to_red", [(1, 1, 1), (0.8, 0, 0)]
            )
            c_cmap = LinearSegmentedColormap.from_list(
                "white_to_blue", [(1, 1, 1), (0, 0, 0.8)]
            )
        
        # 预计算属性值的归一化参数（仅非高亮模式使用）
        q_valid_values = []
        avg_val = None
        q_max_val = q_min_val = None
        if property_type and highlight_mode == 'none' and target in ['q', 'both']:
            q_valid_values = [
                self.q_properties[q_id].get(property_type) 
                for q_id in self.core.get_q_positions() 
                if self.q_properties[q_id].get(property_type) is not None
            ]

            if q_valid_values:
                q_max_val = max(q_valid_values)
                q_min_val = min(q_valid_values)
                avg_val = sum(q_valid_values) / len(q_valid_values)
                
        
        c_valid_values = []
        c_max_val = c_min_val = None
        if property_type and highlight_mode == 'none' and target in ['c', 'both']:
            c_valid_values = [
                self.c_properties[c_id].get(property_type) 
                for c_id in self.core.get_c_positions() 
                if self.c_properties[c_id].get(property_type) is not None
            ]
            if c_valid_values:
                c_max_val = max(c_valid_values)
                c_min_val = min(c_valid_values)
                avg_val = sum(c_valid_values) / len(c_valid_values)

        # 创建图形
        fig, ax = plt.subplots(figsize=self.config.fig_size)
        
        # 配置坐标轴
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        # 绘制C元素
        if target in ['c', 'both']:
            self._plot_c_elements(ax, highlight_mode, highlighted_c_ids, 
                                 property_type, c_valid_values, c_min_val, c_max_val, c_cmap)
        
        # 绘制Q元素
        if target in ['q', 'both']:
            self._plot_q_elements(ax, highlight_mode, highlighted_q_ids, 
                                property_type, q_valid_values, q_min_val, q_max_val, q_cmap)
        
        # 处理颜色条（仅非高亮模式且需要时显示）
        if property_type and self.config.show_colorbar and highlight_mode == 'none':
            self._add_colorbars(ax, fig, q_valid_values, c_valid_values, q_cmap, c_cmap, target)
        
        # 设置标题
        if avg_val:
            self._set_plot_title(fig, highlight_mode, highlight_group, highlight_qc_group,
                                 highlight_qs, highlight_cs, highlight_qcq_tight, highlight_qcq_sparse, property_type, avg_val)
        else:
            self._set_plot_title(fig, highlight_mode, highlight_group, highlight_qc_group,
                                 highlight_qs, highlight_cs, highlight_qcq_tight, highlight_qcq_sparse, property_type)
        
        # 调整坐标轴范围
        self._adjust_axes_limits(ax, target)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()
    
    def _plot_c_elements(self, ax, highlight_mode, highlighted_c_ids, 
                        property_type, c_valid_values, c_min_val, c_max_val, c_cmap):
        """绘制C元素"""
        c_positions = self.core.get_c_positions()
        c_angles = self.core.get_c_angles()
        
        for c_id, (x, y) in c_positions.items():
            angle = c_angles[c_id]
            value = self.c_properties[c_id].get(property_type) if property_type else None
            
            # 根据高亮模式确定颜色
            bg_color = self._get_c_color(c_id, highlight_mode, highlighted_c_ids, 
                                       property_type, value, c_valid_values, c_min_val, c_max_val, c_cmap)
            
            edge_color = bg_color
            text_color = get_text_color(bg_color)
            
            # 绘制C元素（矩形）
            if angle > 0:  # 45度角C
                rect = Rectangle((x + 0.495, y - 0.919), 0.6, 2, 
                                angle=angle, 
                                facecolor=bg_color, 
                                alpha=self.config.c_alpha,
                                edgecolor=edge_color,
                                linewidth=self.config.c_edgewidth)
            else:  # -45度角C
                rect = Rectangle((x - 0.919, y - 0.495), 0.6, 2, 
                                angle=angle, 
                                facecolor=bg_color, 
                                alpha=self.config.c_alpha,
                                edgecolor=edge_color,
                                linewidth=self.config.c_edgewidth)
            
            ax.add_patch(rect)
            
            # 添加文本标签
            if property_type and value is not None and highlight_mode == 'none':
                ax.text(x, y + 0.15, f'C{c_id}', ha='center', va='center', 
                        color=text_color, fontsize=self.config.font_size)
                ax.text(x, y - 0.15, f'{value}', ha='center', va='center', 
                        color=text_color, fontsize=self.config.font_size - 1)
            else:
                ax.text(x, y, f'C{c_id}', ha='center', va='center', 
                        color=text_color, fontsize=self.config.font_size)
    
    def _plot_q_elements(self, ax, highlight_mode, highlighted_q_ids, 
                       property_type, q_valid_values, q_min_val, q_max_val, q_cmap):
        """绘制Q元素"""
        q_positions = self.core.get_q_positions()
        
        for q_id, (x, y) in q_positions.items():
            value = self.q_properties[q_id].get(property_type) if property_type else None
            
            # 根据高亮模式确定颜色
            bg_color = self._get_q_color(q_id, highlight_mode, highlighted_q_ids, 
                                       property_type, value, q_valid_values, q_min_val, q_max_val, q_cmap)
            
            edge_color = bg_color
            text_color = get_text_color(bg_color)
            
            # 绘制Q元素（圆形）
            circle = Circle((x, y), 0.7, 
                           facecolor=bg_color, 
                           alpha=self.config.q_alpha,
                           edgecolor=edge_color,
                           linewidth=self.config.q_edgewidth)
            ax.add_patch(circle)
            
            # 添加文本标签
            if property_type and value is not None and highlight_mode == 'none':
                ax.text(x, y + 0.2, f'Q{q_id}', ha='center', va='center', 
                        color=text_color, fontsize=self.config.font_size)
                ax.text(x, y - 0.2, f'{value}', ha='center', va='center', 
                        color=text_color, fontsize=self.config.font_size - 1)
            else:
                ax.text(x, y, f'Q{q_id}', ha='center', va='center', 
                        color=text_color, fontsize=self.config.font_size)
    
    def _get_c_color(self, c_id, highlight_mode, highlighted_c_ids, 
                    property_type, value, c_valid_values, c_min_val, c_max_val, c_cmap):
        """获取C元素的颜色"""
        if highlight_mode == 'custom':
            return self.config.custom_c_color if c_id in highlighted_c_ids else self.config.none_color
        elif highlight_mode == 'qcq_sparse':
            return self.config.highlight_qcq_sparse_c_color if c_id in highlighted_c_ids else self.config.none_color
        elif highlight_mode == 'qcq_tight':
            return self.config.highlight_qcq_c_color if c_id in highlighted_c_ids else self.config.none_color
        elif highlight_mode == 'qc':
            return self.config.highlight_qc_c_color if c_id in highlighted_c_ids else self.config.none_color
        elif highlight_mode == 'q':
            return self.config.none_color
        else:
            if property_type and value is not None and c_valid_values:
                if self.config.custom_colorbar:
                    c_norm = (value - self.config.c_min_limit) / (self.config.c_max_limit - self.config.c_min_limit)
                else:
                    if c_max_val == c_min_val:
                        c_norm = 0.5
                    else:
                        c_norm = (value - c_min_val) / (c_max_val - c_min_val)
                return c_cmap(c_norm)
            else:
                return self.config.c_default_color if property_type is None else self.config.none_color
    
    def _get_q_color(self, q_id, highlight_mode, highlighted_q_ids, 
                   property_type, value, q_valid_values, q_min_val, q_max_val, q_cmap):
        """获取Q元素的颜色"""
        if highlight_mode == 'custom':
            return self.config.custom_q_color if q_id in highlighted_q_ids else self.config.none_color
        elif highlight_mode == 'qcq_sparse':
            return self.config.highlight_qcq_sparse_q_color if q_id in highlighted_q_ids else self.config.none_color
        elif highlight_mode == 'qcq_tight':
            return self.config.highlight_qcq_q_color if q_id in highlighted_q_ids else self.config.none_color
        elif highlight_mode == 'qc':
            return self.config.highlight_qc_q_color if q_id in highlighted_q_ids else self.config.none_color
        elif highlight_mode == 'q':
            return self.config.highlight_q_color if q_id in highlighted_q_ids else self.config.none_color
        else:
            if property_type and value is not None and q_valid_values:
                if self.config.custom_colorbar:
                    q_norm = (value - self.config.q_min_limit) / (self.config.q_max_limit - self.config.q_min_limit)
                else:
                    if q_max_val == q_min_val:
                        q_norm = 0.5
                    else:
                        q_norm = (value - q_min_val) / (q_max_val - q_min_val)
                return q_cmap(q_norm)
            else:
                return self.config.q_default_color if property_type is None else self.config.none_color
    
    def _add_colorbars(self, ax, fig, q_valid_values, c_valid_values, q_cmap, c_cmap, target):
        """添加颜色条"""
        # 为Q添加左侧颜色条
        if target in ['q', 'both'] and q_valid_values:
            divider = make_axes_locatable(ax)
            cax_q = divider.append_axes("left", size="3%", pad=0.2)
            sm_q = plt.cm.ScalarMappable(cmap=q_cmap)
            sm_q.set_array(q_valid_values)
            if self.config.custom_colorbar:
                sm_q.set_clim(self.config.q_min_limit, self.config.q_max_limit) 
            cbar_q = fig.colorbar(sm_q, cax=cax_q)
            cbar_q.set_label('')
            cax_q.yaxis.set_label_position('left')
            cax_q.yaxis.set_ticks_position('left')
            cbar_q.ax.tick_params(labelsize=6)
        
        # 为C添加右侧颜色条
        if target in ['c', 'both'] and c_valid_values:
            divider = make_axes_locatable(ax)
            cax_c = divider.append_axes("right", size="3%", pad=0.2)
            sm_c = plt.cm.ScalarMappable(cmap=c_cmap)
            sm_c.set_array(c_valid_values)
            if self.config.custom_colorbar:
                sm_c.set_clim(self.config.c_min_limit, self.config.c_max_limit)            
            cbar_c = fig.colorbar(sm_c, cax=cax_c)
            cbar_c.set_label('')
            cbar_c.ax.tick_params(labelsize=6)
    
    def _set_plot_title(self, fig, highlight_mode, highlight_group, highlight_qc_group,
                      highlight_qs, highlight_cs, highlight_qcq_tight, highlight_qcq_sparse, property_type, avg_val: Optional[float]=None):
        """设置图表标题"""
        if highlight_mode == 'custom':
            q_info = f"Q: {highlight_qs}" if highlight_qs else ""
            c_info = f"C: {highlight_cs}" if highlight_cs else ""
            title = f"Custom Highlight ({q_info} {c_info})".strip()
            fig.suptitle(title, fontsize=14, y=0.96)
        elif highlight_mode == 'qcq_sparse':
            fig.suptitle(f"QCQ_sparse Group {highlight_qcq_sparse} Highlighted", fontsize=14, y=0.96)
        elif highlight_mode == 'qcq_tight':
            fig.suptitle(f"QCQ_tight Group {highlight_qcq_tight} Highlighted", fontsize=14, y=0.96)
        elif highlight_mode == 'qc':
            fig.suptitle(f"Q&C Group {highlight_qc_group} Highlighted", fontsize=14, y=0.96)
        elif highlight_mode == 'q':
            fig.suptitle(f"Q Group {highlight_group} Highlighted", fontsize=14, y=0.96)
        else:
            fig.suptitle("Topology Structure" if property_type is None else property_type+', avg='+str(round(avg_val,2)), 
                        fontsize=14, y=0.96)
    
    def _adjust_axes_limits(self, ax, target):
        """调整坐标轴范围"""
        all_x = []
        all_y = []
        if target in ['c', 'both']:
            all_x.extend([x for x, y in self.core.get_c_positions().values()])
            all_y.extend([y for x, y in self.core.get_c_positions().values()])
        if target in ['q', 'both']:
            all_x.extend([x for x, y in self.core.get_q_positions().values()])
            all_y.extend([y for x, y in self.core.get_q_positions().values()])
        
        if all_x and all_y:  # 避免空列表的情况
            ax.set_xlim(min(all_x) - 2, max(all_x) + 2)
            ax.set_ylim(min(all_y) - 2, max(all_y) + 2)
            ax.set_aspect('equal')
