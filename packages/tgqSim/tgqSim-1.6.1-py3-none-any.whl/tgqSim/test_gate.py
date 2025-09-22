from typing import Union
from gate.operation import Operation

from gate.single_gate import *
from gate.double_gate import *
from gate.multi_gate import *
from gate.multi_ctrl_gate import *
from gate.instruction import *
from circuit.quantum_circuit import *
from gate.gate_matrix import *
from circuit.decompose.unitary_decomposition.init_unitary import generate_arbitrary_unitary_mat

import numpy as np
import networkx as nx
# import matplotlib.pyplot as plt
import random

SQGateList = [H, X, Y, Z, S, S_DAG, T, T_DAG, SQRT_X, SQRT_X_DAG]
SPGateList = [RX, RY, RZ]
SUGateList = [U]
# DCGateList = [CX, CP, CZ]
DPGateList = [RXX, RYY, RZZ]
DSGateList = [ISWAP, SWAP]
DUGateList = [DU]

test_SQG = {'h': h_mat, 'x': x_mat, 'y': y_mat, 'z': z_mat, 'sqrt_x': sqrt_x_mat, 'sqrt_x_dag': sqrt_x_sdg_mat,
            's': s_mat, 's_dag': s_dag_mat, 't': t_mat, 't_dag': t_dag_mat}
test_SPG = {'rx': rx_mat, 'ry': ry_mat, 'rz': rz_mat}
test_DQG = {}
test_DPG = {'rxx': rxx_mat, 'ryy': ryy_mat, 'rzz': rzz_mat}

def test_single_gates():
    # 以下测试单比特门
    pass_test = 0
    for sq in SQGateList:
        sggate_rep = sq(0)
        sggate_name = sggate_rep.name
        flag = np.allclose(sggate_rep.params, test_SQG[sggate_name.lower()], atol=1e-4)
        # print(f"输入门: {sggate_rep}")
        # print(f"门矩阵: {sggate_rep.params}")
        # print(f"逆门矩阵: {sggate_rep.inverse()}")
        # print(f"生成的单比特门是否合理: {flag}")
        if flag is True:
            pass_test += 1
    for sp in SPGateList:
        theta = np.random.randint(0, 8) * np.pi / 4
        spgate_rep = sp(0, theta)
        spgate_name = spgate_rep.name
        flag = np.allclose(spgate_rep.params, test_SPG[spgate_name.lower()](theta), atol=1e-4)
        # print(f"输入门: {spgate_rep}")
        # print(f"门矩阵: {spgate_rep.params}")
        # print(f"逆门矩阵: {spgate_rep.inverse()}")
        # print(f"生成的单比特泡利门是否合理: {flag}")
        if flag is True:
            pass_test += 1
    test_num = len(SQGateList) + len(SPGateList)
    if test_num != pass_test:
        print("Tests not pass")
    else:
        print("Tests pass!!!")


def test_double_gates():
    # 以下测试双比特门
    pass_test = 0
    for dq in DPGateList:
        theta = np.random.randint(0, 8) * np.pi / 4
        dpgate_rep = dq(0, 1, theta)
        dpgate_name = dpgate_rep.name
        flag = np.allclose(dpgate_rep.params, test_DPG[dpgate_name.lower()](theta), atol=1e-4)

        # print(f"输入门: {dpgate_name}")
        # print(f"门矩阵: {dpgate_rep.params}")
        # print(f"逆门矩阵: {dpgate_rep.inverse()}")
        # print(f"生成的双比特泡利门是否合理: {flag}")
        if flag is True:
            pass_test += 1
    test_num = len(DPGateList)
    if test_num != pass_test:
        print("Tests not pass")
    else:
        print("Tests pass!!!")


def test_mcu_gates(exception_type):
    # 以下测试，多控制门输入目标比特和目标矩阵不符合时候报错
    target_matrix = generate_arbitrary_unitary_mat(4)
    control_qubits = [0, 1]
    target_qubits = [2]
    try:
        MCUGate(target_matrix, control_qubits, target_qubits)
        print("False,没抛出异常")
    except exception_type as e:
        print("True,目标比特数和目标矩阵形状必须匹配")
    except Exception as e:
        print("False,抛出其它异常")


def test_matrix(exception_type):
    # 以下测试，自定义门输入矩阵必须是酉的
    matrix_1 = np.array([[1, 1], [2, 2]])
    try:
        U(0, matrix_1)
        print("False,没抛出异常")
    except exception_type as e:
        print("True,门必须输入酉矩阵")
    except Exception as e:
        print("False,抛出其它异常")

    # 以下测试，自定义单比特门输入矩阵应该符合比特数
    matrix_2 = generate_arbitrary_unitary_mat(4)
    try:
        U(0, matrix_2)
        print("False,没抛出异常")
    except exception_type as e:
        print("True,单比特门输入矩阵应该符合比特数")
    except Exception as e:
        print("False,抛出其它异常")

    # 以下测试，自定义双比特门输入矩阵应该符合比特数
    matrix_3 = generate_arbitrary_unitary_mat(2)
    try:
        DU(0, 1, matrix_3)
        print("False,没抛出异常")
    except exception_type as e:
        print("True,双比特门输入矩阵应该符合比特数")
    except Exception as e:
        print("False,抛出其它异常")

    matrix_4 = generate_arbitrary_unitary_mat(2)
    try:
        MU([0, 1, 2], matrix_4)
        print("False,没抛出异常")
    except exception_type as e:
        print("True,多比特门输入矩阵应该符合比特数")
    except Exception as e:
        print("False,抛出其它异常")







# def test_matrix_2(exception_type):
#     # 以下测试，自定义门输入矩阵应该符合比特数
#     random_matrix = generate_arbitrary_unitary_mat(4)
#     try:
#         U(0, random_matrix)
#         return False  # 没有抛出异常
#     except exception_type as e:
#         print("True")
#         return True   # 抛出了正确的异常
#     except Exception as e:
#         print("False")
#         return False  # 抛出了其他异常




test_matrix(ValueError)
# test_single_gates()
# test_double_gates()
# test_mcu_gates(TgqSimError)




# def test_single_gates():
#     pass_test = 0
#     for sq in SQGateList:
#         sggate_rep = sq(0)
#         sggate_name = sggate_rep.name
#         flag = np.allclose(sggate_rep.params, test_SQG[sggate_name.lower()], atol=1e-4)
#         print(f"输入门: {sggate_rep}")
#         print(f"门矩阵: {sggate_rep.params}")
#         print(f"逆门矩阵: {sggate_rep.inverse()}")
#         print(f"生成的单比特门是否合理: {flag}")
#         if flag is True:
#             pass_test += 1
#     test_num = len(SQGateList)
#     if test_num != pass_test:
#         print("Tests not pass")
#     else:
#         print("Tests pass!!!")