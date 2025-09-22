"""
@author: Yuchen He
@contact: heyuchen@tgqs.net
@version: 1.0.0
@file: DoubleGate.py
@time: 2024/1/16 17:05
"""
import numpy as np
from numba import prange
from typing import List

def ActOn_State(psi: np.ndarray, num_qubits: int, matrix: np.ndarray, Gate_pos: List[int], ctrl_pos: List[int]) -> np.ndarray:
    # Determine the two target qubit indices (j0 = lower, j1 = higher)
    j0, j1 = sorted(Gate_pos)
    # Pre-compute index offsets and section sizes for the target qubits
    i1_plus = 2 ** j0               # mask to flip bit j0
    i2_plus = 2 ** j1               # mask to flip bit j1
    i3_plus = i1_plus + i2_plus     # mask to flip both j0 and j1
    delta1  = 2 ** (j0 + 1)         # step when toggling j0
    delta2  = 2 ** (j1 + 1)         # step when toggling j1
    max0    = 2 ** j0  - 1          # loop limit for inner m-loop
    max1    = 2 ** j1  - delta1     # loop limit for middle l-loop
    max2    = 2 ** num_qubits - delta2  # loop limit for outer k-loop
    
    flag = 0
    for i in ctrl_pos:
        flag += 1 << i

    # Iterate through the state vector in blocks, covering all combinations of target qubits
    for k in prange(0, max2 + 1, delta2):
        for l in prange(0, max1 + 1, delta1):
            for m in prange(0, max0 + 1):
                # Base index where both target qubits j1 and j0 are 0:
                i0 = m | l | k
                # Indices where j0 and/or j1 bits are set:
                i1 = i0 | i1_plus   # j0 = 1, j1 = 0
                i2 = i0 | i2_plus   # j0 = 0, j1 = 1
                i3 = i0 | i3_plus   # j0 = 1, j1 = 1
                if (i0 | flag == i0) and (i1 | flag == i1) and (i2 | flag == i2) and (i3 | flag == i3):
                    # Copy current amplitudes of these basis states
                    v0, v1, v2, v3 = psi[i0], psi[i1], psi[i2], psi[i3]
                    # Apply the 4x4 gate matrix to compute new amplitudes
                    psi[i0] = matrix[0, 0] * v0 + matrix[0, 1] * v1 + matrix[0, 2] * v2 + matrix[0, 3] * v3
                    psi[i1] = matrix[1, 0] * v0 + matrix[1, 1] * v1 + matrix[1, 2] * v2 + matrix[1, 3] * v3
                    psi[i2] = matrix[2, 0] * v0 + matrix[2, 1] * v1 + matrix[2, 2] * v2 + matrix[2, 3] * v3
                    psi[i3] = matrix[3, 0] * v0 + matrix[3, 1] * v1 + matrix[3, 2] * v2 + matrix[3, 3] * v3
    return psi

# def ActOn_State(psi, num_qubits, Gate_type, Gate_pos, *Angles):
# # def ActOn_State(psi, num_qubits, Gate_type, Gate_pos, *Angles):
#     # Gate_pos[0]:control bit
#     j1 = sorted(Gate_pos)[1]  # 高位比特，不区分控制位与目标位
#     # Gate_pos[1]:target bit
#     j0 = sorted(Gate_pos)[0]  # 低位比特，不区分控制位与目标位
#
#     i1_plus = 2 ** j0  #
#     i2_plus = 2 ** j1  #
#     i3_plus = 2 ** j0 + 2 ** j1  # for i3 = i0 + i3_plus
#     delta2 = 2 ** (j1 + 1)
#     delta1 = 2 ** (j0 + 1)
#     max2 = 2 ** num_qubits - delta2
#     max1 = 2 ** j1 - delta1
#     max0 = 2 ** j0 - 1
#
#     for k in prange(0, max2 + 1, delta2):
#         for l in prange(0, max1 + 1, delta1):
#             for m in prange(0, max0 + 1):
#                 # todo : 为多控制门加一个判断分支，做一个按位或运算
#                 i0 = m | l | k  # to get a(*...*0_j1*...*0_j0*...)
#                 i1 = i0 | i1_plus  # to get a(*...*0_j1*...*1_j0*...)
#                 i2 = i0 | i2_plus  # to get a(*...*1_j1*...*0_j0*...)
#                 i3 = i0 | i3_plus  # to get a(*...*1_j1*...*1_j0*...)
#                 if Gate_type == 'cx':
#                     if Gate_pos[0] > Gate_pos[1]:
#                         psi[i2],  psi[i3] =  psi[i3],  psi[i2]
#                     else:
#                         psi[i1],  psi[i3] =  psi[i3],  psi[i1]
#                 elif Gate_type == 'swap':
#                     psi[i1], psi[i2] = psi[i2],  psi[i1]
#                 elif Gate_type == 'iswap':
#                     psi[i1], psi[i2] = 1j * psi[i2], 1j * psi[i1]
#                 elif Gate_type == 'cz':
#                     psi[i3] = -1.0 * psi[i3]
#                 elif Gate_type == 'cp':
#                     psi[i3] = cm.exp(1j * Angles[0]) * psi[i3]
#                 elif Gate_type == 'syc':
#                     psi[i1], psi[i2], psi[i3] = -1j * psi[i2], -1j * psi[i1], cm.exp(-1j * np.pi / 6) * psi[i3]
#                 elif Gate_type == 'rxx':
#                     psi[i0], psi[i3] = cm.cos(Angles[0] / 2.0) *  psi[i0] + (-1j) * cm.sin(
#                         Angles[0] / 2.0) *  psi[i3], \
#                                                 cm.cos(Angles[0] / 2.0) *  psi[i3] + (-1j) * cm.sin(
#                                                     Angles[0] / 2.0) *  psi[i0]
#                     psi[i1], psi[i2] = cm.cos(Angles[0] / 2.0) * psi[i1] + (-1j) * cm.sin(
#                         Angles[0] / 2.0) *  psi[i2], \
#                                                 cm.cos(Angles[0] / 2.0) * psi[i2] + (-1j) * cm.sin(
#                                                     Angles[0] / 2.0) * psi[i1]
#                 elif Gate_type == 'ryy':
#                     psi[i0], psi[i3] = cm.cos(Angles[0] / 2.0) * psi[i0] + 1j * cm.sin(
#                         Angles[0] / 2.0) *  psi[i3], \
#                                                 cm.cos(Angles[0] / 2.0) * psi[i3] + 1j * cm.sin(
#                                                     Angles[0] / 2.0) *  psi[i0]
#                     psi[i1], psi[i2] = cm.cos(Angles[0] / 2.0) *  psi[i1] + (-1j) * cm.sin(
#                         Angles[0] / 2.0) *  psi[i2], \
#                                                 cm.cos(Angles[0] / 2.0) * psi[i2] + (-1j) * cm.sin(
#                                                     Angles[0] / 2.0) * psi[i1]
#
#                 elif Gate_type == 'rzz':
#                     psi[i0], psi[i1],  psi[i2],  psi[i3] = cm.exp(-0.5j * Angles[0]) *  psi[
#                         i0], cm.exp(0.5j * Angles[0]) *  psi[i1], \
#                                                                                 cm.exp(0.5j * Angles[0]) *  psi[
#                                                                                     i2], cm.exp(-0.5j * Angles[0]) * \
#                                                                                 psi[i3]
#
#     return psi
