import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as lines
from matplotlib.axes._axes import Axes
import numpy as np
from typing import List, Tuple

def get_flipped_index_by_qubit(num_qubit:int, target_qubit:int)->int:
    """
    根据比特位信息，获取横坐标的索引值
    
    说明：因为画布越往上，对应的索引值就越大，但是显示比特位的索引是越小的，所以需要做一个反转
    Args:
        num_qubit (int): 线路的总比特数
        target_qubit (int): 目标比特位

    Returns:
        int: 横坐标的索引值
    """
    return num_qubit - target_qubit - 1

def set_alignment_before(gate: dict, gate_grid_index:list, num_qubits:int) -> list:
    """
    在绘制比特门前，先将所有的比特门（该量子门所跨度的比特位）进行对齐

    Args:
        gate (dict): 量子比特门信息
        gate_grid_index (list): 每一个量子比特位对应的横坐标信息
        num_qubits (int): 线路量子比特数

    Returns:
        list: 对齐后的横坐标信息
    """
    y_index = [get_flipped_index_by_qubit(num_qubits, key) for key in gate]
    min_y_index, max_y_index = min(y_index), max(y_index)
    max_x = max(gate_grid_index[min_y_index:max_y_index + 1])
    for i in range(min_y_index, max_y_index + 1):
        gate_grid_index[i] = max_x
    return gate_grid_index

def get_text_width(text:str, fontsize:float=12, fontfamily:str='sans-serif')->float:
    """
    根据字体大小获取文本的宽度

    Args:
        text (str): 文本信息
        fontsize (float, optional): 字体大小. Defaults to 12.
        fontfamily (str, optional): 字体类型. Defaults to 'sans-serif'.

    Returns:
        float: 字体宽度
    """
    fig, ax = plt.subplots()
    dpi = fig.dpi  # 默认DPI通常为100
    text_obj = ax.text(0, 0, text, fontsize=fontsize, family=fontfamily)
    
    # 获取渲染器（必须在绘制后调用）
    fig.canvas.draw()
    bbox = text_obj.get_window_extent()
    text_width_inch = bbox.width / 72
    text_width_pixels = text_width_inch * dpi
    x_range = ax.get_xlim()[1] - ax.get_xlim()[0]
    width_data = text_width_pixels / fig.get_figwidth() * x_range
    
    plt.close(fig)  # 关闭临时图像
    # print(width_data)
    return width_data / 16  # 返回像素宽度

def get_max_gate_width(gate:dict, fontsize:float=12)->float:
    """
    获取量子门的最大宽度

    Args:
        gate (dict): 量子门信息
        fontsize (float, optional): 字体大小. Defaults to 12.

    Returns:
        float: 最大宽度
    """
    max_size = 0.0
    for key in gate:
        width_data = get_text_width(text=gate[key], fontsize=fontsize)
        max_size = max(max_size, width_data)
    return max_size

def draw_on_qubit_gate(
    ax: Axes, 
    wire_grid:np.ndarray, 
    gate_grid_index:list, 
    gate:dict, 
    num_qubits: int, 
    plot_params:dict
)->Tuple[list, dict]:
    """
    绘制在比特位上的量子门

    Args:
        ax (Axes): 画布信息
        wire_grid (np.ndarray): 纵坐标信息
        gate_grid_index (list): 横坐标信息
        gate (dict): 量子门信息
        num_qubits (int): 比特位数量
        plot_params (dict): 绘制参数

    Returns:
        list: 更新后的横坐标信息
        dict: 更新后的量子门的横坐标与纵坐标的映射关系
    """
    scale = plot_params['scale']
    mapping = {}
    gate_grid_index = set_alignment_before(gate, gate_grid_index, num_qubits)
    max_size = get_max_gate_width(gate, plot_params['fontsize'])
    length_gate_info = len(gate)
    # print(f"gate: {gate}")
    for key in gate:
        row_index = get_flipped_index_by_qubit(num_qubits, key)
        y = wire_grid[row_index]
        x = gate_grid_index[row_index] + max_size / 2
        # print(x, y)
        if gate[key] == '@':
            cdot(ax=ax, x=x, y=y, plot_params=plot_params, dotcolor='#4561de')
        elif gate[key] == 'X' and length_gate_info > 1:
            oplus(ax=ax, x=x, y=y, plot_params=plot_params)
        elif gate[key] == 'x':
            swapx(ax=ax, x=x, y=y, plot_params=plot_params)
        elif gate[key] == 'M':
            text(ax=ax, x=x, y=y, textstr=gate[key], plot_params=plot_params, ec='#ff6f3c', fc='#ff6f3c')
        else:
            text(ax=ax, x=x, y=y, textstr=gate[key], plot_params=plot_params, newboxpad=max_size / 2)
            gate_grid_index[row_index] += max_size
        mapping[y] = x
        gate_grid_index[row_index] += scale
    return gate_grid_index, mapping

def draw_vertical_line(ax: Axes, mapping:dict, plot_params: dict):
    """
    绘制两比特门及两比特以上的量子门连接线

    Args:
        ax (Axes): 花瓣对象
        mapping (dict): 比特位的横坐标与纵坐标映射关系
        plot_params (dict): 绘制参数
    """
    # scale = plot_params['scale']
    min_y, max_y = min(mapping.keys()), max(mapping.keys())
    # max_x = max(mapping.values())
    line(ax=ax, x1=mapping[min_y], x2=mapping[max_y], y1=min_y, y2=max_y, plot_params=plot_params, linecolor="#4561de")

def draw_gates(
    ax:Axes, 
    display_list: List[dict], 
    gate_grid_index:list, 
    wire_grid:np.ndarray, 
    plot_params:dict, 
    num_qubits: int
)->list:
    """
    绘制量子比特门
    Args:
        ax (Axes): 绘图对象
        display_list (List[dict]): 量子门信息
        gate_grid_index (list): 横坐标信息
        wire_grid (np.ndarray): 纵坐标信息
        plot_params (dict): 绘制参数
        num_qubits (int): 比特位数量

    Returns:
        list: 更新后的横坐标信息
    """
    for gate in display_list:
        # print(f"gate: {gate}")
        gate_grid_index, mapping = draw_on_qubit_gate(ax, wire_grid, gate_grid_index, gate, num_qubits, plot_params)
        if len(gate) >= 2 and "M" not in gate.values():
            draw_vertical_line(ax, mapping, plot_params)
    return gate_grid_index

def line(
    ax:Axes, 
    x1:float, 
    x2:float, 
    y1:float, 
    y2:float,
    plot_params:dict, 
    linecolor:str='#50C1E9', 
    zorder:int=1
):
    """
    绘制直线

    Args:
        ax (Axes): 绘图对象
        x1 (float): 线段第一个点的横坐标
        x2 (float): 线段第二个点的横坐标
        y1 (float): 线段第一个点的纵坐标
        y2 (float): 线段第二个点的纵坐标
        plot_params (dict): 基本参数信息
        linecolor (str, optional): 线段的颜色，默认值是'#50C1E9'
        zorder (int, optional): 线段的层级，默认值是1
    """
    Line2D = lines.Line2D
    line = Line2D((x1, x2), (y1, y2),
        color=linecolor,lw=plot_params['linewidth'])
    line.set_zorder(zorder)
    ax.add_line(line)

def text(
    ax:Axes, 
    x:float, 
    y:float, 
    textstr:str, 
    plot_params:dict, 
    newboxpad:float=None, 
    textcolor:str="w", 
    ec:str='#4561de', 
    fc:str='#4561de'
):
    """
    绘制一般的单门，如H, X, Y, Z等
    Args:
        ax (Axes): 绘图对象
        x (float): box中写入文字的横坐标
        y (float): box中写入文字的纵坐标
        textstr (str): 在box中需要写入的内容
        plot_params (dict): 基本参数信息
        textcolor (str, optional): 默认值是w，对应的文字颜色
        newboxpad (float, optional): box的宽度，默认值是None
        ec (str, optional): box的边框颜色，默认值是'#4561de'
        fc (str, optional): box的填充颜色，默认值是'#4561de'
    """
    # print(ax)
    linewidth = plot_params['linewidth']
    fontsize = plot_params['fontsize']
    height_pad = plot_params['box_pad']
    if newboxpad is None or newboxpad < height_pad:
        width_pad = plot_params['box_pad']
    else:
        width_pad = newboxpad
    if textstr.endswith('^½†'):
        textstr = r'$\sqrt{%s}^\dagger$' % textstr[0]
    if textstr.endswith("^½"):
        textstr = r'$\sqrt{%s}$' % textstr[0]
        
    targetbox = patches.FancyBboxPatch(xy=(x - width_pad, y - height_pad), height=2 * height_pad, width=2 * width_pad, ec=ec, fc=fc, fill=True, lw=linewidth, boxstyle='round,pad=0.08', zorder=2)
    ax.add_patch(targetbox)
    ax.text(x, y, textstr, color=textcolor, ha='center', va='center', size=fontsize)
    return

def oplus(ax:Axes, x:float, y:float, plot_params:dict):
    """
    绘制CX和CCX这两个门，主要是解决直和那个符号
    Args:
        ax (Axes): 绘图对象
        x (float): 对应的圆心横坐标
        y (float): 对应的圆心纵坐标
        plot_params (dict): 基本参数信息
    """
    Circle = patches.Circle
    not_radius = plot_params['not_radius']
    linewidth = plot_params['linewidth']
    c = Circle((x, y), not_radius, ec='#4561de',
               fc='#4561de', fill=False, lw=linewidth)
    ax.add_patch(c)
    line(ax, x, x, y - not_radius, y + not_radius, plot_params, '#4561de')
    line(ax, x - not_radius, x + not_radius, y, y, plot_params, '#4561de')
    return

def cdot(ax:Axes, x:float, y:float, plot_params:dict, dotcolor:str='#7A56D0'):
    """
    绘制控制位那个点
    Args:
        ax (Axes): 绘图对象
        x (float): 对应的圆心横坐标
        y (float): 对应的圆心纵坐标
        plot_params (dict): 基本参数信息
        dotcolor (str, optional): 设置点的颜色，默认值是'#7A56D0'.
    """
    Circle = patches.Circle
    control_radius = plot_params['control_radius']
    scale = plot_params['scale']
    linewidth = plot_params['linewidth']
    c = Circle((x, y), control_radius*scale,
        ec=dotcolor, fc=dotcolor, fill=True, lw=linewidth, zorder=2)
    ax.add_patch(c)
    return

def swapx(ax:Axes, x:float, y:float, plot_params:dict):
    """
    绘制交换门
    Args:
        ax (Axes): 绘图对象
        x (float): 绘制❌中心位置的横坐标
        y (float): 绘制❌中心位置的纵坐标
        plot_params (dict): 基本参数信息
    """
    d = plot_params['swap_delta']
    line(ax, x-d, x+d, y-d, y+d, plot_params, linecolor='#4561de')
    line(ax, x-d, x+d, y+d, y-d, plot_params, linecolor='#4561de')
    return

def setup_figure(nq:int, ng:int, gate_grid:np.array, wire_grid:np.array, plot_params:dict):
    """
    设置图形的基本信息
    Args:
        nq (int): 比特数
        ng (int): 门序列列数，主要是设置整个图的宽度
        gate_grid (np.array): 整个图的所有点的横坐标
        wire_grid (np.array): 整个图的所有点的纵坐标
        plot_params (dict): 基本参数信息
    """
    scale = plot_params['scale']
    fig = plt.figure(
        figsize=(ng * scale, nq * scale),
        facecolor='w',
        edgecolor='w'
    )
    ax = fig.add_subplot(1, 1, 1,frameon=True)
    # fig.tight_layout()
    ax.set_axis_off()
    offset = 0.5*scale
    ax.set_xlim(gate_grid[0] - offset, gate_grid[-1] + offset)
    ax.set_ylim(wire_grid[0] - offset, wire_grid[-1] + offset)
    ax.set_aspect('equal')
    return fig,ax

def draw_wires(ax:Axes, nq:int, gate_grid: np.array, wire_grid:np.array, plot_params:dict, linecolor:str):
    """
    绘制线路图中横线
    Args:
        ax (Axes): 绘图对象
        nq (int): 比特数
        gate_grid (np.array): 整个图的所有点的横坐标
        wire_grid (np.array): 整个图的所有点的纵坐标
        plot_params (dict): 基本参数信息
        linecolor (str): 线段的颜色
        measured (dict, optional): 测量门位置信息
    """
    scale = plot_params['scale']
    for i in range(nq):
        line(ax, gate_grid[0] - scale, gate_grid[-1] + scale, wire_grid[i], wire_grid[i], plot_params, linecolor, zorder=0)
    return

def draw_labels(ax:Axes, num_qubits: int, inits:dict, gate_grid:list, wire_grid:np.array, plot_params:dict, textcolor:str):
    """
    每根线谱前对应的标签
    Args:
        ax (Axes): 绘图对象
        labels (list): 里面元素都是字符串，列举出每一个比特的标签
        inits (dict): 线路图中每一条线前面的标签与索引的关系
        gate_grid (list): 整个图的所有点的横坐标
        wire_grid (np.array): 整个图的所有点的纵坐标
        plot_params (dict): 基本参数信息
        textcolor (str): 填写内容的颜色
    """
    scale = plot_params['scale']
    label_buffer = plot_params['label_buffer']
    for i in range(num_qubits):
        qbit = inits[f"q_{i}"]
        j = get_flipped_index_by_qubit(num_qubit=num_qubits, target_qubit=qbit)
        text(ax=ax, x=gate_grid[0] - label_buffer * scale, y=wire_grid[j], 
             textstr=render_label(f"q_{i}", inits), plot_params=plot_params, 
             textcolor=textcolor
            )
    return

def render_label(label:str, inits:dict={}):
    """
    绘制前面标签内容
    Args:
        label (str): 在当前代码中比特位的标签
        inits (dict, optional): 线路图中每一条线前面的标签与索引的关系

    Returns:
        str: Latex字符串代码
    """
    if label in inits:
        s = inits[label]
        if s is None:
            return ''
        else:
            return r'$q_%s|0\rangle$' % inits[label]
    return r'$q_%s|0\rangle$' % label



if __name__ == "__main__":
    # 测试代码
    import matplotlib.pyplot as plt

    def update_fontsize(event):
        # 获取当前窗口的物理尺寸（英寸）
        fig_width_inch = event.canvas.figure.get_size_inches()[0]
        
        # 根据窗口宽度计算新字体大小（经验公式）
        new_fontsize = fig_width_inch * 4  # 缩放因子根据需求调整
        
        # 更新所有文字的字体大小
        for text_obj in event.canvas.figure.axes[0]._texts:
            text_obj.set_fontsize(new_fontsize)
        
        # 重绘图形
        event.canvas.draw()

    # 初始化图形
    fig, ax = plt.subplots(figsize=(8, 6))
    texts = [
        ax.text(0.3, 0.5, "动态文字1", ha='center', va='center', fontsize=32),
        ax.text(0.7, 0.5, "动态文字2", ha='center', va='center', fontsize=32)
    ]

    # 绑定窗口缩放事件
    fig.canvas.mpl_connect('resize_event', update_fontsize)
    plt.show()