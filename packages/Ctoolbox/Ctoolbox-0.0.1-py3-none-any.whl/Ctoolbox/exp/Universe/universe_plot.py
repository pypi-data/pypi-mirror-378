import matplotlib.pyplot as plt

def creat_fig(qubits,fignum1row=7, eachfigsize=(3,2.5)): 
    rows = len(qubits)//fignum1row + 1 if len(qubits)%fignum1row != 0 else len(qubits)//fignum1row
    fig, axes = plt.subplots(rows, fignum1row, figsize=[fignum1row*eachfigsize[0],rows*eachfigsize[0]])
    try:
        axes = axes.flatten()
    except:
        axes = [axes]
    return fig, axes

def get_extent(xaxis, yaxis):
    dx = (xaxis[1]-xaxis[0])/2
    dy = (yaxis[1]-yaxis[0])/2
    extent = [xaxis[0]-dx, xaxis[-1]-dx, yaxis[0]-dy, yaxis[-1]+dy]
    return extent

import matplotlib.pyplot as plt
import numpy as np

def add_click_handler(fig):
    # 存储结果的字典
    selected_points = {}
    # 存储所有绘制的点对象，用于删除
    plotted_points = {}  # 结构: {identifier: [line_objects]}
    def on_click(event):
        """鼠标点击事件处理函数"""
        if event.inaxes is not None:
            # 获取标识符：优先使用标题，没有则用'__main__'
            identifier = event.inaxes.get_title().strip() or '__main__'
            # 初始化记录列表
            if identifier not in selected_points:
                selected_points[identifier] = {'x': [], 'y': []}
                plotted_points[identifier] = []
            # 左键点击 - 添加点
            if event.button == 1:  # 1表示左键
                x = event.xdata
                y = event.ydata
                selected_points[identifier]['x'].append(x)
                selected_points[identifier]['y'].append(y)
                # 标记选中的点并保存线条对象
                line, = event.inaxes.plot(x, y, 'ro', markersize=6)
                plotted_points[identifier].append(line)
                fig.canvas.draw()
                # 打印信息
                print(f"已在 {identifier} 上添加点: X={x:.4f}, Y={y:.4f}")
                print(f"当前 {identifier} 共有 {len(selected_points[identifier]['x'])} 个点")
            # 右键点击 - 删除最近的点
            elif event.button == 3:  # 3表示右键
                if len(selected_points[identifier]['x']) == 0:
                    print(f"{identifier} 上没有可删除的点")
                    return
                # 计算点击位置与所有点的距离
                x = event.xdata
                y = event.ydata
                points_x = np.array(selected_points[identifier]['x'])
                points_y = np.array(selected_points[identifier]['y'])
                # 计算欧氏距离
                distances = np.sqrt((points_x - x)**2 + (points_y - y)** 2)
                # 找到最近点的索引
                closest_idx = np.argmin(distances)
                # 删除数据
                removed_x = selected_points[identifier]['x'].pop(closest_idx)
                removed_y = selected_points[identifier]['y'].pop(closest_idx)
                # 从图上删除点
                line_to_remove = plotted_points[identifier].pop(closest_idx)
                line_to_remove.remove()
                fig.canvas.draw()
                # 打印信息
                print(f"已从 {identifier} 上删除点: X={removed_x:.4f}, Y={removed_y:.4f}")
                print(f"当前 {identifier} 剩余 {len(selected_points[identifier]['x'])} 个点")
    # 连接事件
    fig.canvas.mpl_connect('button_press_event', on_click)    
    return selected_points
