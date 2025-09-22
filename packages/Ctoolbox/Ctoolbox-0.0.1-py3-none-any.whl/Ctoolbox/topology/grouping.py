from typing import List, Dict, Tuple, Set, Any
from .core import TopologyCore
from .utils import parse_label, get_coords_mod
from .config import TopologyConfig

# 并查集数据结构，用于处理分组的传递性
class UnionFind:
    """并查集数据结构，用于处理元素分组的传递性关系"""
    def __init__(self, elements: List[Any]):
        self.parent = {elem: elem for elem in elements}
    
    def find(self, x: Any) -> Any:
        """查找元素的根节点"""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # 路径压缩
        return self.parent[x]
    
    def union(self, x: Any, y: Any) -> None:
        """合并两个元素所在的集合"""
        x_root = self.find(x)
        y_root = self.find(y)
        if x_root != y_root:
            self.parent[y_root] = x_root

class GroupingStrategy:
    """分组策略基类，定义分组接口"""
    def calculate(self, core: TopologyCore) -> List:
        """计算分组
        
        Args:
            core: 拓扑核心对象，提供必要的拓扑数据
            
        Returns:
            分组结果列表
        """
        raise NotImplementedError("子类必须实现calculate方法")

class QGroupingStrategy(GroupingStrategy):
    """Q元素的分组策略"""
    def calculate(self, core: TopologyCore) -> List[List[str]]:
        """计算4个Q分组
        
        Args:
            core: 拓扑核心对象
            
        Returns:
            4个Q分组的列表，每个分组包含Q标签
        """
        cols = core.config.cols
        if cols < 2:
            raise ValueError("列数cols必须至少为2才能生成指定的Q分组")
        
        # 确定四个组的起点Q的ID
        group_starts = [
            0,                  # 第一组：第一行第一个Q
            1,                  # 第二组：第一行第二个Q
            cols,               # 第三组：第二行第一个Q
            cols + 1            # 第四组：第二行第二个Q
        ]
        
        # 验证起点是否存在
        q_positions = core.get_q_positions()
        for start_id in group_starts:
            if start_id not in q_positions:
                raise ValueError(f"分组起点Q{start_id}不存在，请检查行列数设置")
        
        # 为每个起点生成组（广度优先搜索扩展）
        q_groups = []
        for start_id in group_starts:
            group = {start_id}  # 用集合存储组内Q的ID（去重）
            current_layer = {start_id}  # 当前层待扩展的Q
            
            while True:
                next_layer = set()
                # 遍历当前层的Q，寻找距离为4√2的Q
                for q_id in current_layer:
                    q_x, q_y = q_positions[q_id]
                    # 检查所有其他Q
                    for other_id in q_positions:
                        if other_id in group:  # 跳过已在组内的Q
                            continue
                        o_x, o_y = q_positions[other_id]
                        # 4√2的平方为32
                        distance_sq = (q_x - o_x)**2 + (q_y - o_y)** 2
                        if abs(distance_sq - 32) < 1e-6:
                            next_layer.add(other_id)
                
                if not next_layer:  # 没有新Q可添加，结束扩展
                    break
                group.update(next_layer)
                current_layer = next_layer  # 继续扩展新层
            
            # 转换为带标签的格式，并按Q的ID从小到大排序
            sorted_group = [f'Q{q_id}' for q_id in sorted(group)]
            q_groups.append(sorted_group)
            
        return q_groups

class QCGroupingStrategy(GroupingStrategy):
    """Q和C组合的分组策略"""
    def calculate(self, core: TopologyCore, q_groups: List[List[str]]) -> List[Dict[str, List[str]]]:
        """计算16个Q&C组合分组
        
        Args:
            core: 拓扑核心对象
            q_groups: 4个Q分组的列表
            
        Returns:
            16个Q&C分组的列表，每个分组包含'Q'和'C'两个键
        """
        # 初始化16个分组（4个Q组 × 4个C子组）
        qc_groups = [{'Q': [], 'C': []} for _ in range(16)]
        
        # 遍历4个Q组
        for q_group_idx in range(4):
            q_group = q_groups[q_group_idx]  # 当前Q组的所有Q标签
            # 为当前Q组初始化对应的4个C子组
            for c_subgroup in range(4):
                group_idx = q_group_idx * 4 + c_subgroup
                qc_groups[group_idx]['Q'] = q_group.copy()  # 继承Q组的所有Q
            
            # 遍历当前Q组中的每个Q，对其NC的C进行分类
            for q_label in q_group:
                q_id = parse_label(q_label, 'Q')  # 提取Q的ID数字
                q_x, q_y = core.get_q_positions()[q_id]  # Q的坐标
                nc_list = core.get_q_connections(q_id)['NC']  # 该Q的最近邻C（标签列表）
                
                # 处理每个最近邻C
                for c_label in nc_list:
                    c_id = parse_label(c_label, 'C')  # 提取C的ID数字
                    c_x, c_y = core.get_c_positions()[c_id]  # C的坐标
                    
                    # 计算C相对于Q的坐标偏移
                    dx = c_x - q_x
                    dy = c_y - q_y
                    
                    # 根据偏移量判断C属于哪个子组
                    if abs(dx + 1) < 1e-6 and abs(dy - 1) < 1e-6:
                        c_subgroup = 0  # 第一子组：(x-1, y+1)
                    elif abs(dx - 1) < 1e-6 and abs(dy - 1) < 1e-6:
                        c_subgroup = 1  # 第二子组：(x+1, y+1)
                    elif abs(dx + 1) < 1e-6 and abs(dy + 1) < 1e-6:
                        c_subgroup = 2  # 第三子组：(x-1, y-1)
                    elif abs(dx - 1) < 1e-6 and abs(dy + 1) < 1e-6:
                        c_subgroup = 3  # 第四子组：(x+1, y-1)
                    else:
                        continue  # 不属于任何子组
                    
                    # 将C添加到对应的Q&C分组
                    group_idx = q_group_idx * 4 + c_subgroup
                    qc_groups[group_idx]['C'].append(c_label)
            
            # 对每个C子组的C标签按ID排序
            for c_subgroup in range(4):
                group_idx = q_group_idx * 4 + c_subgroup
                sorted_c = sorted(
                    qc_groups[group_idx]['C'],
                    key=lambda x: parse_label(x, 'C')  # 按C的ID数字排序
                )
                qc_groups[group_idx]['C'] = sorted_c
                
        return qc_groups

class QCQTightGroupingStrategy(GroupingStrategy):
    """QCQ_tight分组策略"""
    def calculate(self, core: TopologyCore) -> List[List[List[Any]]]:
        """计算4个QCQ_tight分组
        
        Args:
            core: 拓扑核心对象
            
        Returns:
            4个QCQ_tight分组的列表，每个分组元素格式为['C0', ('Q0', 'Q6')]
        """
        # 初始化4个QCQ_tight分组
        qcq_tight_groups = [[], [], [], []]
        
        # 遍历所有C，按规则分配到对应组
        c_positions = core.get_c_positions()
        c_angles = core.get_c_angles()
        c_rows = core.get_c_rows()
        
        for c_id in c_positions:
            # 获取C的关键信息
            c_angle = c_angles[c_id]
            c_row = c_rows[c_id]  # C所属的行（生成该C的Q所在行）
            c_label = f'C{c_id}'
            
            # 获取该C对应的最近邻Q（NQ），转换为元组并排序
            nq_list = core.get_c_connections(c_id)['NQ']
            sorted_nq = tuple(sorted(nq_list, key=lambda x: parse_label(x, 'Q')))  # 按Q ID排序
            
            # 判断所属分组
            if c_row % 2 == 1:  # 奇数行的C
                if c_angle == -45:
                    # 奇数行，angle=-45 → 第一组
                    qcq_tight_groups[0].append([c_label, sorted_nq])
                elif c_angle == 45:
                    # 奇数行，angle=45 → 第二组
                    qcq_tight_groups[1].append([c_label, sorted_nq])
            
            else:  # 偶数行的C
                if c_angle == -45:
                    # 偶数行，angle=-45 → 第三组
                    qcq_tight_groups[2].append([c_label, sorted_nq])
                elif c_angle == 45:
                    # 偶数行，angle=45 → 第四组
                    qcq_tight_groups[3].append([c_label, sorted_nq])
        
        # 对每个组内的元素按C的ID排序
        for i in range(4):
            qcq_tight_groups[i].sort(key=lambda x: parse_label(x[0], 'C'))  # 按C ID排序
            
        return qcq_tight_groups

class QCQSparseGroupingStrategy(GroupingStrategy):
    """QCQ_sparse分组策略"""
    def calculate(self, core: TopologyCore, qcq_tight_groups: List[List[List[Any]]]) -> List[List[List[Any]]]:
        """计算16个QCQ_sparse分组
        
        分组规则：
        对于同一QCQ_tight分组中的C元素，满足以下任一条件则分到同一组：
        1. C的y坐标模8结果相同 且 C的x坐标相同
        2. C的y坐标相同 且 C的x坐标模8结果相同
        
        Args:
            core: 拓扑核心对象
            qcq_tight_groups: 4个QCQ_tight分组的列表
            
        Returns:
            16个QCQ_sparse分组的列表，每个分组元素格式为['C0', ('Q0', 'Q6')]
        """
        # 初始化16个QCQ_sparse分组（4个QCQ_tight组 × 4个子组）
        qcq_sparse_groups = [[] for _ in range(16)]
        
        # 遍历4个QCQ_tight分组
        for tight_group_idx in range(4):
            tight_group = qcq_tight_groups[tight_group_idx]
            if not tight_group:  # 空组处理
                continue
            
            # 收集该tight组中所有C的信息：(c_label, x, y, item)
            c_info_list = []
            c_positions = core.get_c_positions()
            
            for item in tight_group:
                c_label = item[0]
                c_id = parse_label(c_label, 'C')
                x, y = c_positions[c_id]
                c_info_list.append((c_label, x, y, item))
            
            # 使用并查集处理分组的传递性
            # 以c_label为唯一标识
            uf = UnionFind([c_info[0] for c_info in c_info_list])
            
            # 检查所有C对，按规则合并分组
            for i in range(len(c_info_list)):
                c1_label, c1_x, c1_y, _ = c_info_list[i]
                c1_x_mod8 = get_coords_mod(c1_x, 8)  # x坐标模8
                c1_y_mod8 = get_coords_mod(c1_y, 8)  # y坐标模8
                
                for j in range(i + 1, len(c_info_list)):
                    c2_label, c2_x, c2_y, _ = c_info_list[j]
                    c2_x_mod8 = get_coords_mod(c2_x, 8)
                    c2_y_mod8 = get_coords_mod(c2_y, 8)
                    
                    # 条件1：y坐标模8相同 且 x坐标相同
                    condition1 = (c1_y_mod8 == c2_y_mod8) and abs(c1_x - c2_x) < 1e-6
                    # 条件2：y坐标相同 且 x坐标模8相同
                    condition2 = abs(c1_y - c2_y) < 1e-6 and (c1_x_mod8 == c2_x_mod8)
                    
                    # 满足任一条件则合并分组
                    if condition1 or condition2:
                        uf.union(c1_label, c2_label)
            
            # 按并查集结果分组
            groups: Dict[str, List] = {}
            for c_info in c_info_list:
                c_label, _, _, item = c_info
                root = uf.find(c_label)
                if root not in groups:
                    groups[root] = []
                groups[root].append(item)
            
            # 转换为列表并排序
            sorted_groups = sorted(groups.values(), key=lambda g: parse_label(g[0][0], 'C'))
            
            # 确保每个tight组生成4个子组（如果不足则补空，超过则合并最后几个）
            final_groups = []
            for i in range(4):
                if i < len(sorted_groups):
                    # 对子组内元素按C ID排序
                    sorted_group = sorted(
                        sorted_groups[i],
                        key=lambda x: parse_label(x[0], 'C')
                    )
                    final_groups.append(sorted_group)
                else:
                    final_groups.append([])
            
            # 将4个子组添加到对应的位置
            for sub_idx in range(4):
                qcq_sparse_groups[tight_group_idx * 4 + sub_idx] = final_groups[sub_idx]
                
        return qcq_sparse_groups

class GroupManager:
    """分组管理器，协调各种分组策略"""
    def __init__(self, core: TopologyCore):
        """初始化分组管理器
        
        Args:
            core: 拓扑核心对象
        """
        self.core = core
        self.q_groups: List[List[str]] = []
        self.qc_groups: List[Dict[str, List[str]]] = []
        self.qcq_tight_groups: List[List[List[Any]]] = []
        self.qcq_sparse_groups: List[List[List[Any]]] = []
        
        # 初始化分组策略
        self.q_strategy = QGroupingStrategy()
        self.qc_strategy = QCGroupingStrategy()
        self.qcq_tight_strategy = QCQTightGroupingStrategy()
        self.qcq_sparse_strategy = QCQSparseGroupingStrategy()
        
        # 计算所有分组
        self._calculate_all_groups()
    
    def _calculate_all_groups(self) -> None:
        """计算所有类型的分组"""
        self.q_groups = self.q_strategy.calculate(self.core)
        self.qc_groups = self.qc_strategy.calculate(self.core, self.q_groups)
        self.qcq_tight_groups = self.qcq_tight_strategy.calculate(self.core)
        self.qcq_sparse_groups = self.qcq_sparse_strategy.calculate(self.core, self.qcq_tight_groups)
    
    # 获取分组的接口方法
    def get_q_groups(self) -> List[List[str]]:
        """获取4个Q分组"""
        return [group.copy() for group in self.q_groups]
    
    def get_qc_groups(self) -> List[Dict[str, List[str]]]:
        """获取16个Q&C组合分组"""
        return [{'Q': g['Q'].copy(), 'C': g['C'].copy()} for g in self.qc_groups]
    
    def get_qcq_tight_groups(self) -> List[List[List[Any]]]:
        """获取4个QCQ_tight分组"""
        return [group.copy() for group in self.qcq_tight_groups]
    
    def get_qcq_sparse_groups(self) -> List[List[List[Any]]]:
        """获取16个QCQ_sparse分组"""
        return [group.copy() for group in self.qcq_sparse_groups]
