import numpy as np
from typing import List, Set, Tuple, Union
from matplotlib.colors import to_rgb

def parse_label(label: str, prefix: str) -> int:
    """解析标签字符串，提取数字ID
    
    Args:
        label: 标签字符串，如'Q3'或'C5'
        prefix: 前缀字符，如'Q'或'C'
    
    Returns:
        提取的数字ID
        
    Raises:
        ValueError: 标签格式错误时抛出
    """
    if not label.startswith(prefix):
        raise ValueError(f"标签格式错误：{label}，应为'{prefix}+数字'格式")
    try:
        return int(label[1:])
    except ValueError:
        raise ValueError(f"标签格式错误：{label}，应为'{prefix}+数字'格式")

def get_coords_mod(value: float, mod: int) -> int:
    """计算坐标值对mod取模的结果（四舍五入后）
    
    Args:
        value: 坐标值（x或y）
        mod: 模数（如8）
    
    Returns:
        取模后的整数结果
    """
    return int(round(value)) % mod

def extract_highlight_ids(group_data: List, prefix: str) -> Set[int]:
    """从分组数据中提取需要高亮的ID集合
    
    Args:
        group_data: 分组数据，如QCQ_sparse分组的元素列表
        prefix: 前缀字符，如'Q'或'C'
    
    Returns:
        高亮ID的集合
    """
    ids = set()
    for item in group_data:
        if isinstance(item, list) and len(item) > 0:
            # 处理QCQ分组格式 ['C0', ('Q0', 'Q6')]
            if isinstance(item[0], str) and item[0].startswith(prefix):
                try:
                    ids.add(parse_label(item[0], prefix))
                except ValueError:
                    continue
            # 处理Q和QC分组中的标签
            if isinstance(item, str) and item.startswith(prefix):
                try:
                    ids.add(parse_label(item, prefix))
                except ValueError:
                    continue
    return ids

def get_text_color(bg_color: Union[Tuple, str]) -> str:
    """根据背景颜色确定文字颜色（黑/白）
    
    Args:
        bg_color: 背景颜色（RGB元组或颜色字符串）
    
    Returns:
        'black'或'white'
    """
    try:
        rgb = to_rgb(bg_color)
    except ValueError:
        rgb = (1.0, 1.0, 1.0)
    r, g, b = [min(1.0, max(0.0, c)) for c in rgb[:3]]
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return 'black' if luminance > 0.5 else 'white'

def validate_group_number(group_num: int, min_val: int, max_val: int, group_name: str) -> None:
    """验证分组编号是否在有效范围内
    
    Args:
        group_num: 分组编号
        min_val: 最小值
        max_val: 最大值
        group_name: 分组名称，用于错误提示
        
    Raises:
        ValueError: 分组编号不在有效范围内时抛出
    """
    if not (isinstance(group_num, int) and min_val <= group_num <= max_val):
        raise ValueError(f"{group_name}必须是{min_val}-{max_val}之间的整数，当前为{group_num}")
