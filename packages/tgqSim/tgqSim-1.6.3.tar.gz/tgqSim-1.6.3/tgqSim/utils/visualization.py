from typing import Optional, List
from copy import deepcopy

def to_text_diag(gates: list, width: int, classical_bits: Optional[List[int]] = None) -> str:
    """
    绘制线路图

    Args:
        gates (list): 量子门列表
        width (int): 比特位数量

    Returns:
        str: 打印线路图
    """
    # use displayname_list element of quantumcircuit
    gateList = deepcopy(gates)
    qubitNum = width
    # 初始化相关参数
    diagInfo, indexList = init_diag_info(qubitNum=qubitNum)
    # e.g. gate_pos: Union[int, str], display_name: tuple, *gate_info
    diagInfo, indexList = draw_all_gate(diagInfo=diagInfo, gateList=gateList, indexList=indexList, qubitNum=qubitNum, classical_bits=classical_bits)
    diagInfo = circuit_alignment(diagInfo=diagInfo, indexList=indexList)
    return "\n".join(diagInfo)

def get_index_width(qubitNum: int) -> int:
    """
    获取比特位的宽度

    Args:
        qubitNum (int): 比特位数量

    Returns:
        int: 比特位宽度
    """
    # 若是两位数，则返回2，后面加上3是因为后面还有一个": -"
    qubit_index_width, tmpwidth = 0, qubitNum
    while tmpwidth > 0:
        tmpwidth //= 10
        qubit_index_width += 1
    return qubit_index_width + 3


def init_diag_info(qubitNum: int) -> list:
    """
    初始化画板信息

    Args:
        qubitNum (int): 比特位数量

    Returns:
        list: 画板信息
    """
    # 获取索引宽度，这部分信息会展示在每个比特位上
    # 如： 
    #   0: ────────────────────────────────────
    #   1: ────────────────────────────────────
    qubit_index_width = get_index_width(qubitNum=qubitNum)
    # 索引位偶数显示比特位，奇数位显示空隙
    diagInfo = [f"{i // 2}: ─".rjust(qubit_index_width) if i % 2 == 0 else ' ' * (qubit_index_width) for i in range(2 * qubitNum) ]
    # 最后两行显示测量位信息
    diagInfo += ["c: ═".rjust(qubit_index_width), ' ' * (qubit_index_width)]
    # 初始化指针位置
    indexList = [qubit_index_width for _ in range(2 * qubitNum + 2)]
    return diagInfo, indexList


def draw_all_gate(diagInfo:list, gateList: list, indexList:list, qubitNum:int, classical_bits: Optional[List[int]]) -> list:
    """
    绘制所有量子门
    由于测量门绘制样式与其他量子门不同，因此需要单独处理，后期可以将这些信息放在量子门类中
    
    todo: 量子门类增加绘制门的信息或者方法，to_text_diag方法直接拼接所有门的信息

    Args:
        diagInfo (list): 画板信息
        gateList (list): 量子门列表
        qubitNum (int): 比特位数量
        indexList (list): 指针位置列表

    Returns:
        list: 更新后的画板信息
    """
    measure_index_global = 0
    for display_name in gateList:
        # print(f"display_name:{display_name}")
        # print(f"measure_index_global: {measure_index_global}")
        if 'M' in display_name.values():
            # 测量门
            # number_measure_gate = len(display_name)
            # todo: 增加经典比特位
            length = len(classical_bits)
            display_name[qubitNum] = ['╩', f"{(classical_bits[measure_index_global] + length) % length}"]
            diagInfo, indexList = draw_gate(
                diagInfo=diagInfo, 
                indexList=indexList, 
                diagEle=display_name, 
                qubitNum=qubitNum
            )
            measure_index_global += 1
        else:
            # 非测量门
            diagInfo, indexList = draw_gate(
                diagInfo=diagInfo, 
                indexList=indexList, 
                diagEle=display_name,
                qubitNum=qubitNum
            )
    return diagInfo, indexList

def get_label_max_size(diagEle: dict):
    max_width = 0
    for key in diagEle:
        if isinstance(diagEle[key], list):
            for ele in diagEle[key]:
                max_width = max(max_width, len(ele))
        else:
            max_width = max(max_width, len(diagEle[key]))
    return max_width

def set_alignment_before(diagInfo: list, indexList: list, diagEle: dict):
    min_qbit, max_qbit = min(diagEle), max(diagEle)
    old_max_index = max([indexList[i] for i in range(2 * min_qbit, 2 * max_qbit + 1)])
    for i in range(2 * min_qbit, 2 * max_qbit + 1):
        if i == len(diagInfo) - 2:
            diagInfo[i] += "".ljust(old_max_index - indexList[i], "═")
            diagInfo[i+1] += "".ljust(old_max_index - indexList[i+1], " ")
            indexList[i+1] = old_max_index
        elif i % 2 == 0:
            # 比特位
            diagInfo[i] += "".ljust(old_max_index - indexList[i], "─")
        else:
            # 空隙
            diagInfo[i] += "".ljust(old_max_index - indexList[i], " ")
        # 更新指针位置 
        indexList[i] = old_max_index
    return diagInfo, indexList

def draw_on_quite_gate(diagInfo: list, indexList: list, diagEle: dict, qubitNum:int)->list:
    """
    绘制比特位上的信息

    Args:
        diagInfo (list): 画板信息
        pos (list): 比特位位置
        indexList (list): 指针位置列表
        diagEle (tuple): 绘制的图形信息
        qubitNum (int): 比特位数量

    Returns:
        list: 更新后的画板信息
    """
    # 两个量子门之间的间隔
    interval_dash_number = 2
    # 获取量子门显示宽度
    max_width = get_label_max_size(diagEle=diagEle)
    # 两比特及以上的量子门，查询最大的深度
    diagInfo, indexList = set_alignment_before(diagInfo=diagInfo, indexList=indexList, diagEle=diagEle)
    tmpIndexList = indexList.copy()
    for qIndex in diagEle:
        # print(i, qIndex)
        if qIndex == qubitNum:
            # 量子门作用在最后一个比特位上，直接用╩替代
            diagInfo[-2] += diagEle[qIndex][0].ljust(max_width + interval_dash_number, "═")
            diagInfo[-1] += diagEle[qIndex][1].ljust(max_width + interval_dash_number, " ")
            tmpIndexList[-1] += max_width + interval_dash_number
        else:
            diagInfo[2 * qIndex] += diagEle[qIndex].ljust(max_width + interval_dash_number, "─")
    
    # 对画布绘制结束后，对其跨度所有的比特位
    min_qbit, max_qbit = min(diagEle), max(diagEle)    
    for i in range(2 * min_qbit, 2 * max_qbit + 1):
        # print(i)
        tmpIndexList[i] += max_width + interval_dash_number
    # print("draw_on_quite_gate: ", indexList, tmpIndexList)
    return diagInfo, tmpIndexList


def draw_vertical_line(diagInfo: list, oldIndexList: list, newIndexList: list, diagEle: tuple, qubitNum: int)->list:
    """
    绘制两比特量子门或者两比特以上的量子门之间的连线

    Args:
        diagInfo (list): 画板信息
        pos (list): 量子门作用位置
        oldIndexList (list): 原始索引列表
        newIndexList (list): 更新后的索引列表
        diagEle (tuple): 绘制的图形信息

    Returns:
        list: 更新后的画板信息
    """
    min_qbit, max_qbit = min(diagEle), max(diagEle)
    # print("draw_vertical_line", oldIndexList, newIndexList)
    for i in range(2 * min_qbit, 2 * max_qbit + 1):
        width = newIndexList[i] - oldIndexList[i]
        # width = 3
        # print(width)
        if i % 2 == 0:
            qIndex = i // 2
            if qIndex in diagEle:
                # 这个位置是门作用的位置，不能覆盖
                continue
            else:
                if qubitNum in diagEle:
                    # print(f"measure-width:{width}")
                    diagInfo[i] += '╫'.ljust(width, "─")
                else:
                    # print(f"gate-width:{width}")
                    # 若是当前位置比特位，则利用垂直线替代┼
                    diagInfo[i] += "┼".ljust(width, "─")
        else:
            if qubitNum in diagEle:
                # print(f"width:{width}")
                # 若是测量门，则用║替代
                diagInfo[i] += "║".ljust(width, ' ')
            else:
                # print(f"gate-width:{width}")
                # 若是当前位置是两个相邻比特之间的空隙，直接用│替代
                diagInfo[i] += "│".ljust(width, ' ')
    return diagInfo


def draw_gate(diagInfo: list, indexList: list, diagEle: tuple, qubitNum:int)->list:
    """
    绘制量子门

    Args:
        diagInfo (list): 画板信息
        pos (list): 量子门作用位置
        indexList (list): 指针位置列表
        diagEle (tuple): 绘制的图形信息
        qubitNum (int): 比特位数量

    Returns:
        list: 更新后的画板信息
    """
    # 绘制量子门
    diagInfo, newIndexList = draw_on_quite_gate(
        diagInfo=diagInfo, 
        indexList=indexList, 
        diagEle=diagEle,
        qubitNum=qubitNum
    )
    # print(indexList, newIndexList)
    # 绘制跨比特位
    diagInfo = draw_vertical_line(
        diagInfo=diagInfo, 
        oldIndexList=indexList, 
        newIndexList=newIndexList, 
        diagEle=diagEle,
        qubitNum=qubitNum
    )
    return diagInfo, newIndexList

def circuit_alignment(diagInfo: list, indexList: list) -> list:
    """
    对齐线路图

    Args:
        diagInfo (list): 画板信息
        indexList (list): 指针位置列表

    Returns:
        list: 更新后的画板信息
    """
    # print(indexList)
    max_index = 0
    for i in range(len(indexList)):
        if i % 2 == 0:
            max_index = max(max_index, indexList[i])
    # print(f"max_index:{max_index}")
    
    for i in range(len(diagInfo)):
        width = max_index - indexList[i]
        # print(f"width: {width}")
        if i == len(diagInfo) - 2:
            diagInfo[i] += "".rjust(width, "═")
        elif i % 2 == 0:
            diagInfo[i] += "".rjust(width, "─")
        else:
            diagInfo[i] += "".rjust(width, " ")
    return diagInfo