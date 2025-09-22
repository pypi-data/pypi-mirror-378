"""

@author: Yuchen He
@contact: heyuchen@tgqs.net
@version: 1.0.0
@file: SingleGate.py
@time: 2024/1/16 17:05
"""

import numpy as np
from numba import prange
from typing import List

def SingleMatirx_ActOn_State(psi, num_qubits, Gate_mat, Gate_pos: List[int], ctrl_pos: List[int]):
    """
    单比特门矩阵作用于线路的实现
    :param psi:门作用前的状态
    :param num_qubits: 线路总体量子比特数量
    :param Gate_mat: 单比特门矩阵
    :param Gate_pos: 双臂特门矩阵
    :return:
    """
    Gate_pos = Gate_pos[0]
    flag = 0
    for i in ctrl_pos:
        flag += 1 << i
    i = 2 ** Gate_pos
    nstates = 2 ** num_qubits - 2 ** (Gate_pos + 1)
    klist = np.array([k for k in range(0, nstates + 1, i + i)])
    klen = len(klist)
    for k in prange(0, klen):
        for l in prange(0, i):
            i0 = l | klist[k]  # to find a(*...*0_j*...)
            i1 = i0 | i  # to find a(*...*1_j*...) by plus a(00001_j0000)
            if (i0 | flag == i0) and (i1 | flag == i1):
                temp = np.dot(Gate_mat, np.array([psi[i0], psi[i1]]))
                psi[i0], psi[i1] = temp[0], temp[1]
    return psi

def normalization(psi:list, num_qubits: int):
    norm = np.linalg.norm(psi)
    if 0 == norm:
        return [1 if 0 == i else 0 for i in range(2**num_qubits)]
    else:
        return list(np.divide(psi, norm))


def ActOn_State(psi, num_qubits, gate_matrix, gate_pos, ctrl_pos: List[int]):
# def ActOn_State(psi, num_qubits, gate_type:str, gate_pos, *angles):
    """
    单比特门作用于线路的实现
    :param psi:
    :param num_qubits:
    :param gate_type: 门类型
    :param gate_pos:
    :param angles:
    :return:
    """
    # todo 这里不再维护一遍各个门的矩阵了，直接传进来
    # print("position is : ", gate_pos)
    return SingleMatirx_ActOn_State(psi, num_qubits, Gate_mat=gate_matrix, Gate_pos=gate_pos, ctrl_pos=ctrl_pos)
    # if gate_type.lower() == 'h':
    #     h_mat = np.array([[1, 1], [1, -1]]) / np.sqrt(2.0)
    #     return SingleMatirx_ActOn_State(psi, num_qubits, Gate_mat=h_mat, Gate_pos=gate_pos)
    # elif gate_type.lower() == 'x':
    #     x_mat = np.array([[0, 1], [1, 0]])
    #     return SingleMatirx_ActOn_State(psi, num_qubits, Gate_mat=x_mat, Gate_pos=gate_pos)
    # elif gate_type.lower() == 'y':
    #     y_mat = np.array([[0, -1j], [1j, 0]])
    #     return SingleMatirx_ActOn_State(psi, num_qubits, Gate_mat=y_mat, Gate_pos=gate_pos)
    # elif gate_type.lower() == 'z':
    #     z_mat = np.array([[1,0],[0,-1]])
    #     return SingleMatirx_ActOn_State(psi, num_qubits, Gate_mat=z_mat, Gate_pos=gate_pos)
    # elif gate_type.lower() == 'u3':
    #     u3_mat = np.array([
    #         [m.cos(angles[0] / 2.0), -cm.exp(1j * angles[2]) * m.sin(angles[0] / 2.0)],
    #         [cm.exp(1j * angles[1]) * m.sin(angles[0] / 2.0),
    #          cm.exp(1j * (angles[1] + angles[2])) * m.cos(angles[0] / 2.0)]
    #     ])
    #     return SingleMatirx_ActOn_State(psi, num_qubits, Gate_mat=u3_mat, Gate_pos=gate_pos)
    # elif gate_type.lower() == 'rx':
    #     rx_mat = np.array([[m.cos(angles[0] / 2.0), -1j * m.sin(angles[0] / 2.0)],
    #                        [-1j * m.sin(angles[0] / 2.0), m.cos(angles[0] / 2.0)]]
    #                       )
    #     return SingleMatirx_ActOn_State(psi, num_qubits, Gate_mat=rx_mat, Gate_pos=gate_pos)
    # elif gate_type.lower() == 'ry':
    #     ry_mat = np.array([[m.cos(angles[0] / 2.0), -m.sin(angles[0] / 2.0)],
    #                        [m.sin(angles[0] / 2.0), m.cos(angles[0] / 2.0)]]
    #                       )
    #     return SingleMatirx_ActOn_State(psi, num_qubits, Gate_mat=ry_mat, Gate_pos=gate_pos)
    # elif gate_type.lower() == 'rz':
    #     rz_mat = np.array([[cm.exp(-1j * angles[0] / 2.0), 0],
    #                        [0, cm.exp(1j * angles[0] / 2.0)]])
    #     return SingleMatirx_ActOn_State(psi, num_qubits, Gate_mat=rz_mat, Gate_pos=gate_pos)
    # elif gate_type.lower() == 's':
    #     rz_mat = np.array(
    #         [
    #             [1, 0],
    #             [0, 1j]
    #         ]
    #     )
    #     return SingleMatirx_ActOn_State(psi, num_qubits, Gate_mat=rz_mat, Gate_pos=gate_pos)
    # elif gate_type.lower() == 'sdg':
    #     rz_mat = np.array(
    #         [
    #             [1, 0],
    #             [0, -1j]
    #         ]
    #     )
    #     return SingleMatirx_ActOn_State(psi, num_qubits, Gate_mat=rz_mat, Gate_pos=gate_pos)
    # elif gate_type.lower() == 't':
    #     rz_mat = np.array(
    #         [
    #             [1, 0],
    #             [0, cm.exp(np.pi / 4 * 1j)]
    #         ]
    #     )
    #     return SingleMatirx_ActOn_State(psi, num_qubits, Gate_mat=rz_mat, Gate_pos=gate_pos)
    # elif gate_type.lower() == 'tdg':
    #     rz_mat = np.array(
    #         [
    #             [1, 0],
    #             [0, cm.exp(-np.pi / 4 * 1j)]
    #         ]
    #     )
    #     return SingleMatirx_ActOn_State(psi, num_qubits, Gate_mat=rz_mat, Gate_pos=gate_pos)
    # elif gate_type.lower() == "damp_i":
    #     error_rate = angles[0]
    #     rz_mat = np.array(
    #         [
    #             [1, 0],
    #             [0, np.sqrt(1 - error_rate)]
    #         ]
    #     )
    #     return normalization(SingleMatirx_ActOn_State(psi, num_qubits, Gate_mat=rz_mat, Gate_pos=gate_pos), num_qubits)
    # elif gate_type.lower() == "pd":
    #     error_rate = angles[0]
    #     rz_mat = np.array(
    #         [
    #             [0, 0],
    #             [0, np.sqrt(error_rate)]
    #         ]
    #     )
    #     return normalization(SingleMatirx_ActOn_State(psi, num_qubits, Gate_mat=rz_mat, Gate_pos=gate_pos), num_qubits)
    # elif gate_type.lower() == "ad":
    #     error_rate = angles[0]
    #     rz_mat = np.array(
    #         [
    #             [0, np.sqrt(error_rate)],
    #             [0, 0]
    #         ]
    #     )
    #     return normalization(SingleMatirx_ActOn_State(psi, num_qubits, Gate_mat=rz_mat, Gate_pos=gate_pos), num_qubits)