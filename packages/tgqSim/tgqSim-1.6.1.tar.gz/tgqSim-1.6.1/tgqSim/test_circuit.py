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
# SingleGateList = ['h', 'x', 'y', 'z', 's', 'sdg', 't', 'tdg', 'sx', 'sxdg', 'rx', 'ry', 'rz', 'u']
# DoubleGateList = ['cx', 'cz', 'rxx', 'ryy', 'rzz', 'swap', 'iswap', 'iswapdg', 'du']
test_SQG = {'h': h_mat, 'x': x_mat, 'y': y_mat, 'z': z_mat, 'sqrt_x': sqrt_x_mat, 'sqrt_x_dag': sqrt_x_sdg_mat,
            's': s_mat, 's_dag': s_dag_mat, 't': t_mat, 't_dag': t_dag_mat}
test_SPG = {'rx': rx_mat, 'ry': ry_mat, 'rz': rz_mat}

test_DPG = {'rxx': rxx_mat, 'ryy': ryy_mat, 'rzz': rzz_mat}
test_DSWAPG = {'swap': swap_mat, 'iswap': iswap_mat}


SQInstrList = ['h', 'x', 'y', 'z', 'sqrt_x', 'sqrt_x_dag', 's', 's_dag', 't', 't_dag']
SPInstrList = ['rx', 'ry', 'rz']
SUInstrList = ['u']
# DCInstrList = [CX, CP, CZ]
DPInstrList = ['rxx', 'ryy', 'rzz']
DSInstrList = ['swap', 'iswap']
CUInstrList = ['cnot', 'cz', 'cp']

SGInsList = ['h', 'x', 'y', 'z', 'sqrt_x', 'sqrt_x_dag', 's', 's_dag', 't', 't_dag', 'rx', 'ry', 'rz', 'u']

DGInsList = ['rxx', 'ryy', 'rzz', 'swap', 'iswap']

CUInsList = ['cnot', 'cz', 'cp']
InstructionList = SGInsList + DGInsList + CUInsList
def circuit_generate():
    qc = QuantumCircuit(3)
    for ins in SQInstrList:
        method = getattr(qc, ins)
        method(0)
    for ins in SPInstrList:
        method = getattr(qc, ins)
        theta = np.random.randint(0, 8) * np.pi / 4
        method(1, theta)
    for ins in SUInstrList:
        method = getattr(qc, ins)
        matrix = generate_arbitrary_unitary_mat(2)
        method(2, matrix)
    for ins in DPInstrList:
        method = getattr(qc, ins)
        theta = np.random.randint(0, 8) * np.pi / 4
        method(0, 2, theta)
    for ins in DSInstrList:
        method = getattr(qc, ins)
        method(0, 1)
    return qc

def test_qc_compose():
    # 以下测试线路拼接，其中，第二个线路要能重新设置门的位置
    ori_qc = QuantumCircuit(5)
    ori_qc.x(2)
    ori_qc.cnot(1, 4)
    ori_qc.cz(0, 3)
    com_qc = QuantumCircuit(4)
    com_qc.h(0)
    com_qc.cnot(1, 3)
    com_qc.cz(0, 2)
    ori_qc.compose(com_qc, [1, 2, 3, 4])
    return ori_qc
qc1 = circuit_generate()
print(qc1)

qc2 = test_qc_compose()
print(qc2.circuit)