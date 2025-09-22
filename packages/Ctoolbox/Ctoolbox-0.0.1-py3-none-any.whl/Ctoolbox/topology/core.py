from typing import Dict, List, Tuple
import numpy as np
from .config import TopologyConfig

class TopologyCore:
    """拓扑结构的核心生成逻辑，负责计算Q和C的位置及连接关系"""
    
    def __init__(self, config: TopologyConfig):
        """初始化拓扑核心
        
        Args:
            config: 拓扑配置对象
        """
        self.config = config
        
        # 存储拓扑数据的字典
        self.q_positions: Dict[int, Tuple[float, float]] = {}  # Q的位置 (id: (x, y))
        self.c_positions: Dict[int, Tuple[float, float]] = {}  # C的位置 (id: (x, y))
        self.c_angles: Dict[int, float] = {}                  # C的旋转角度 (id: angle)
        self.c_rows: Dict[int, int] = {}                      # C所属的行 (id: row)
        self.q_connections: Dict[int, Dict] = {}              # Q的连接信息
        self.c_connections: Dict[int, Dict] = {}              # C的连接信息
        
        # 缓存计算结果
        self._cache = {}
        
        # 生成拓扑和连接关系
        self._generate_topology()
        self._calculate_connections()
    
    def _generate_topology(self) -> None:
        """生成拓扑结构，计算Q和C的位置及属性"""
        q_count = 0
        c_count = 0

        # 验证行列数有效性
        if self.config.rows <= 0 or self.config.cols <= 0:
            raise ValueError("行数和列数必须为正整数")
        
        for row in range(self.config.rows):
            for col in range(self.config.cols):
                # 计算Q的位置
                if row % 2 == 0:  # 偶数行
                    x = col * 4
                else:  # 奇数行，错位排列
                    x = col * 4 + 2
                y = (self.config.rows - row - 1) * 2 
                self.q_positions[q_count] = (x, y)

                # 计算C的位置、角度和所属行（仅对非最后一行的Q生成C）
                if row < self.config.rows - 1:
                    c_belong_to_row = row
                    
                    if row % 2 == 0:  # 偶数行的Q生成的C
                        if col != 0:
                            # 左侧C（角度-45度）
                            c_x, c_y = x - 1, y - 1
                            self._add_c_element(c_count, c_x, c_y, -45, c_belong_to_row)
                            c_count += 1
                            
                        # 右侧C（角度45度）
                        c_x, c_y = x + 1, y - 1
                        self._add_c_element(c_count, c_x, c_y, 45, c_belong_to_row)
                        c_count += 1
                        
                    else:  # 奇数行的Q生成的C
                        if col != self.config.cols - 1:
                            # 左侧C（角度-45度）
                            c_x, c_y = x - 1, y - 1
                            self._add_c_element(c_count, c_x, c_y, -45, c_belong_to_row)
                            c_count += 1
                            # 右侧C（角度45度）
                            c_x, c_y = x + 1, y - 1
                            self._add_c_element(c_count, c_x, c_y, 45, c_belong_to_row)
                            c_count += 1
                        else:
                            # 左侧C（角度-45度）
                            c_x, c_y = x - 1, y - 1
                            self._add_c_element(c_count, c_x, c_y, -45, c_belong_to_row)
                            c_count += 1
                        
                q_count += 1
    
    def _add_c_element(self, c_id: int, x: float, y: float, angle: float, row: int) -> None:
        """添加C元素到拓扑结构
        
        Args:
            c_id: C元素ID
            x: x坐标
            y: y坐标
            angle: 旋转角度
            row: 所属行
        """
        self.c_positions[c_id] = (x, y)
        self.c_angles[c_id] = angle
        self.c_rows[c_id] = row
    
    def _calculate_connections(self) -> None:
        """计算Q和C之间的连接关系"""
        self._calculate_q_connections()
        self._calculate_c_connections()
    
    def _calculate_q_connections(self) -> None:
        """计算每个Q的连接关系（最近邻C和Q）"""
        for q_id, (q_x, q_y) in self.q_positions.items():
            connections = {
                'NC': [],  # 最近邻C
                'NQ': [],  # 最近邻Q
                'HNNQ': [],  # 横向次近邻Q
                'VNNQ': []   # 纵向次近邻Q
            }

            # 计算最近邻C（距离sqrt(2)）
            for c_id, (c_x, c_y) in self.c_positions.items():
                distance_sq = (q_x - c_x)**2 + (q_y - c_y)** 2
                if np.isclose(distance_sq, 2):
                    connections['NC'].append(f'C{c_id}')

            # 计算最近邻Q（距离2*sqrt(2)）
            for other_q_id, (other_x, other_y) in self.q_positions.items():
                if other_q_id == q_id:
                    continue
                distance_sq = (q_x - other_x)**2 + (q_y - other_y)** 2
                if np.isclose(distance_sq, 8):
                    connections['NQ'].append(f'Q{other_q_id}')

            # 计算横向次近邻Q（x差4，y相同）
            for other_q_id, (other_x, other_y) in self.q_positions.items():
                if other_q_id == q_id:
                    continue
                if np.isclose(abs(q_x - other_x), 4) and np.isclose(q_y, other_y):
                    connections['HNNQ'].append(f'Q{other_q_id}')

            # 计算纵向次近邻Q（y差4，x相同）
            for other_q_id, (other_x, other_y) in self.q_positions.items():
                if other_q_id == q_id:
                    continue
                if np.isclose(q_x, other_x) and np.isclose(abs(q_y - other_y), 4):
                    connections['VNNQ'].append(f'Q{other_q_id}')

            self.q_connections[q_id] = connections
    
    def _calculate_c_connections(self) -> None:
        """计算每个C的连接关系（最近邻Q）"""
        for c_id, (c_x, c_y) in self.c_positions.items():
            connections = {'NQ': []}
            # 最近邻Q（距离sqrt(2)）
            for q_id, (q_x, q_y) in self.q_positions.items():
                distance_sq = (c_x - q_x)**2 + (c_y - q_y)** 2
                if np.isclose(distance_sq, 2):
                    connections['NQ'].append(f'Q{q_id}')
            self.c_connections[c_id] = connections
    
    # 以下为获取数据的接口方法
    def get_q_positions(self) -> Dict[int, Tuple[float, float]]:
        """获取所有Q的位置"""
        return self.q_positions.copy()
    
    def get_c_positions(self) -> Dict[int, Tuple[float, float]]:
        """获取所有C的位置"""
        return self.c_positions.copy()
    
    def get_c_angles(self) -> Dict[int, float]:
        """获取所有C的旋转角度"""
        return self.c_angles.copy()
    
    def get_c_rows(self) -> Dict[int, int]:
        """获取所有C所属的行"""
        return self.c_rows.copy()
    
    def get_q_connections(self, q_id: int) -> Dict:
        """获取指定Q的连接关系"""
        if q_id not in self.q_connections:
            raise ValueError(f"Q ID {q_id} 不存在")
        return self.q_connections[q_id].copy()
    
    def get_all_q_connections(self) -> Dict[int, Dict]:
        """获取所有Q的连接关系"""
        return {k: v.copy() for k, v in self.q_connections.items()}
    
    def get_c_connections(self, c_id: int) -> Dict:
        """获取指定C的连接关系"""
        if c_id not in self.c_connections:
            raise ValueError(f"C ID {c_id} 不存在")
        return self.c_connections[c_id].copy()
    
    def get_all_c_connections(self) -> Dict[int, Dict]:
        """获取所有C的连接关系"""
        return {k: v.copy() for k, v in self.c_connections.items()}
