# from circuit import QuantumCircuit
# from standard_gate.SQGlibrary import HGate, RZGate, SQGate
# from standard_gate.DQGlibrary import SWAPGate, CXGate, CZGate, DQGate, DUGate
# from standard_gate.MQGlibrary import MUGate, MCUGate
# from standard_gate.instruction import CircuitError
# from standard_gate.instruction import Instruction
from typing import Union
from gate.operation import Operation
from gate.bit import QuantumRegister, Qubit
# from gate.single_gate import SingleGate, U
# from gate.multi_gate import MQGate
from gate.single_gate import *
from gate.double_gate import *
from gate.multi_gate import *
from gate.multi_ctrl_gate import *
from circuit.quantum_circuit import *
# from unitary_decomposition.init_unitary import circuit2unitary
# from unitary_decomposition.DQGdecomposition import DQG_decomposition
# from unitary_decomposition.SQGdecomposition import SQG_decomposition
from circuit.decompose.unitary_decomposition.init_unitary import generate_arbitrary_unitary_mat
# from unitary_decomposition.init_unitary import generate_randSU, is_special_unitary, generate_arbitrary_special_orthogonal_matrix
# from unitary_decomposition.ZYZ_decomposition import ry2list, ry2sx_rz_circ
# from SQG_reduction.SQGreduction import single_qubit_gate_reduction
# from DQG_reduction.DQGreduction import double_qubit_gate_reduction
# from unitary_decomposition import test_quantum_shannon_multiqubit
# from first_mapping import physical_qubit_selection
# from compiler import transpile
import numpy as np
import networkx as nx
# import matplotlib.pyplot as plt
import random
# import qiskit, cirq


SQGdict = {1: 'h', 2: 'x', 3: 'y', 4: 'z', 5: 'sx', 6: 'sxdg',
              7: 's', 8: 'sdg', 9: 't', 10: 'tdg', 11: 'rx', 12: 'r_y', 13: 'rz', 14: 'u'}
DQGset = ('cx', 'cy', 'cz', 'swap', 'iswap', 'iswapdg', 'du')
char_order = {v: k for k, v in SQGdict.items()}


def generate_connected_graph(n, p=0.2):
    """
    生成随机连通图
    :param n: 节点数
    :param p: 边存在的概率
    :return: 邻接矩阵
    """
    while True:
        G = nx.erdos_renyi_graph(n, p)  # 生成随机图
        if nx.is_connected(G):         # 检查连通性
            return nx.to_numpy_array(G)

def RxxGate(theta: float, x: float =0.0) -> np.ndarray:
    """
    Rxx gate matrix.
    """
    return np.array([[np.cos(theta / 2), x, x, -1j * np.sin(theta / 2)],
                     [x, np.cos(theta / 2), -1j * np.sin(theta / 2), x],
                     [x, -1j * np.sin(theta / 2), np.cos(theta / 2), x],
                     [-1j * np.sin(theta / 2), x, x, np.cos(theta / 2)]])
# def random_circuit(qubit_num, instr_num):
#     circuit = QuantumCircuit(qubit_num)

#     for _ in range(instr_num):
#         instr_type = random.choice(['h', 'x', 'y', 'z', 's', 't', 'cx', 'cz', 'cy', 'iswap', 'swap'])
#         if instr_type in ['cx', 'cz', 'cy', 'iswap', 'swap']:
#             # control_qubit = random.randint(0, qubit_num - 1)
#             # target_qubit = random.randint(0, qubit_num - 1)
#             control_qubit, target_qubit = random.sample(range(qubit_num), 2)
#             getattr(circuit, instr_type)(control_qubit, target_qubit)
#         else:
#             qubit = random.randint(0, qubit_num - 1)
#             getattr(circuit, instr_type)(qubit)

#     return circuit
        
def random_circuit(qubit_num, instr_num, general_unitary_num=0, max_unitary_qubit_num=5):
    circuit = QuantumCircuit(qubit_num)
    added_general_unitary_num = 0

    for _ in range(instr_num):
        if added_general_unitary_num < general_unitary_num:
            instr_type = random.choice(['h', 'x', 'y', 'z', 's', 't', 'cx', 'cz', 'iswap', 'swap', 'mcu'])
        else:
            instr_type = random.choice(['h', 'x', 'y', 'z', 's', 't', 'cx', 'cz', 'iswap', 'swap'])
        if instr_type in ['cx', 'cz', 'iswap', 'swap']:
            # control_qubit = random.randint(0, qubit_num - 1)
            # target_qubit = random.randint(0, qubit_num - 1)
            control_qubit, target_qubit = random.sample(range(qubit_num), 2)
            getattr(circuit, instr_type)(control_qubit, target_qubit)
        elif instr_type == 'mcu':
            qubits = random.sample(range(qubit_num), min(qubit_num, max_unitary_qubit_num))
            controled_single_qubit_gate = generate_arbitrary_special_orthogonal_matrix(2)
            # getattr(circuit, instr_type)('u', qubits[:-1], [qubits[-1]], matrix=controled_single_qubit_gate)
            getattr(circuit, instr_type)(controled_single_qubit_gate, qubits[:-1], [qubits[-1]])
            added_general_unitary_num += 1
        else:
            qubit = random.randint(0, qubit_num - 1)
            getattr(circuit, instr_type)(qubit)

    return circuit


if __name__ == '__main__':
    # num_qubits = 3
    # qreg = QuantumRegister(size=num_qubits, name="qreg")
    # m1 = generate_arbitrary_unitary_mat(2)
    # m1 = x_mat
    # # print(m1)
    # qubits = [0]
    # target_qubits = [1]
    # tmp_matrix = y_mat
    # tmp_test = y_mat * np.exp(-1j * np.pi / 6)
    # tmp = MCUGate(target=tmp_test, control_qubits=qubits, target_qubits=target_qubits)
    # # tmp = CCX(0, 1, 2)
    # print(tmp.params)
    # SQGateList = [H, X, Y, Z, S, S_DAG, T, T_DAG, SQRT_X, SQRT_X_DAG]
    # for g in SQGateList:
    #     sggate_rep = g(0)
    #     print(sggate_rep)
    #     print(sggate_rep.name)
    #     print(sggate_rep.params)
    qc = QuantumCircuit(3)
    qc.cnot(1, 0)
    qc.ccx(0, 2, 1)
    print(qc)
    print(qc.circuit)

    extend_qc = QuantumCircuit(3)
    extend_qc.x(2)
    extend_qc.cz(0, 1)
    extend_qc.cnot(2, 0)
    qc.compose(extend_qc, [0, 1, 2])
    print(qc)
    # g = CP(0, 1, np.pi/3)
    # print(g)
    # g = CCX(0, 1, 2)
    # print(g)
    # print(g.upload_params().params)


    # # # 创建一个线路的实例
    # g = SWAP(0, 1)
    # print(g)
    # g.reset_qubits([1, 2])
    # print(g.on_qubits)
    # print(g)
    # g.control_by(2)
    # print(g)
    # print(g.matrix)
    # print(g.upload_params().params)
    # target = np.array([[1, 2], [3, 0]])
    # g = MCUGate(target, [1, 2], [3])
    # print(g)
    # g = CX(1, 3)
    # print(g)
    # qc = QuantumCircuit(4)
    # qc.mcu('rz', [0, 1, 2], 3, None, np.pi/7)
    # qc.x(0)
    # qc.rz(1, np.pi/7)
    # qc.h(2)
    # # qc.cnot(0, 3)
    # # print(qc.circuit)
    # add_qc = QuantumCircuit(4)
    # add_qc.cz(0, 1)
    # add_qc.z(2)
    # add_qc.h(3)
    # qc.compose(add_qc, [0, 1, 2, 3])
    # print(qc.circuit)

    # circuit = QuantumCircuit(3)
    # circuit.cnot(0, 1)
    # circuit.h(2)
    # print(circuit)

    # # circuit.du(qreg[0], qreg[1], tmp)
    # circuit.h(qreg[0])
    # circuit.x(qreg[1])
    # print(circuit)
    # tes = MQGate(name="mq", matrix=tmp, on_qubits=[qreg[0], qreg[1], qreg[2]])
    # theta = np.pi/8
    # tmp = X(0)

    # # tmp = MCUGate(1 / 2 * np.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]], dtype=np.complex128), [0,1,3], [2])
    # # print(len(tmp.on_qubits))
    # tmp.control_by(1)
    # print(tmp)
    # print(type(tmp))
    # for gate in circuit:
    #     max_qubit_index = max(gate.on_qubits).index()
    #     print(max_qubit_index)
    # max(gate.on_qubits).index()
    # tes = tmp.control_by(qreg[1]).control_by(qreg[2])
    # print(tes)
    # print("1q1trfwrtf")
    # print(tes.params)
    # # print(tes.params)
    # circuit.append(tes)
    # print(circuit)
    # CRxxGate = Operation(name="RxGate", on_qubits=[qreg[1], qreg[2]], matrix=RxxGate, num_qubits=2, theta=np.pi / 4, x=0).control_by(qreg[0])
    # print(CRxxGate.on_qubits)
    # print(CRxxGate.data)
    # print(circuit.circuit)
#     matrix22 = np.array([
#     [1, 2, 3],
#     [4, 5, 6],
#     [7, 8, 9]
# ])
#     tmp = U(qreg[0], matrix22)
#     print(tmp)
#     print(tmp.on_qubits)




    # np.random.seed(10)
    # r_U = generate_randSU(4)
    # g1 = MCUGate('y', [0, 1], [2])
    # print(g1)
    # g2 = g1.control([3])
    # print(g2)
    # g1 = RZGate(1, 0)
    # print(g1[1])
    # print(g1.params)
    # print(g1)
    # print(g1.inverse())
    # print(g1.reset_qubit(1))
    # print(g1[1])
    # g2 = CXGate(0, 1)
    # print(g2[1][0])
    # print(g2.params)
    # print(g2.reset_qubit(1, 0))
    # print(isinstance(g2, Instruction))
    # tmparray = np.array([[0.-0.70710678j, 0.5-0.5j, 0.+0.j, 0.+0.j],[0.70710678+0.j, -0.5-0.5j, 0.+0.j, 0.+0.j],[0.+0.j, 0.+0.j, -0.5-0.5j, 0.70710678+0.j],[0.+0.j, 0.+0.j, 0.5-0.5j, 0.-0.70710678j]])
    # print(tmparray)
    # qc = QuantumCircuit(6)
    # # qc.du(np.array([[0.-0.70710678j, 0.5-0.5j, 0.+0.j, 0.+0.j],[0.70710678+0.j, -0.5-0.5j, 0.+0.j, 0.+0.j],[0.+0.j, 0.+0.j, -0.5-0.5j, 0.70710678+0.j],[0.+0.j, 0.+0.j, 0.5-0.5j, 0.-0.70710678j]]), 0, 1)
    # qc.mcu('h', [1, 2], [0])
    # # print(qc)
    # print(qc.data[0])
    # print(qc.data[0].name)
    # print(HGate(0).control([1, 2]))
    # print(MCU)
    # qc.t(0)
    # qc.cx(0, 1)
    # qc.x(1)
    # qc.rz(np.pi, 0)
    # qc.h(1)
    # # qc.cx(0, 1)
    # qc.s(0)
    # qc.z(0)
    # qc.cx(1, 0)
    # # qc.x(1)
    # new_qc, tmp = double_qubit_gate_reduction(qc)

    # print(qc)
    # BASIS_DOUBLE_QUBIT_GATE = set(['cx', 'cz', 'iswap'])
    # print(type(BASIS_DOUBLE_QUBIT_GATE))
    # print(new_qc)
    # print(new_qc.data)
    # print(new_qc.data[0])
    # print(type(new_qc.data[0]))
    # print(len(new_qc.data[0]))
    # qc.cz(0, 3)
    # qc.h(0)
    # DQGset = {'cx', 'cz', 'swap', 'iswap', 'iswapdg', 'du'}
    # print(qc.data)
    # print(qc.num_gate)
    # added_qc = [RZGate(0, 0), HGate(1)]
    # qc.reset_qc(added_qc)
    # print(qc.data)
    # print(qc.num_gate)
    # qc.compose(RZGate(0, 1), [0])
    # print(qc.data)
    # print(circuit2unitary(qc))
    # print(SQG_decomposition(qc))

    # test_quantum_shannon_multiqubit()
    # print("\n=== 所有量子比特系统验证通过 ===")


    # 生成节点的连通图
    # adj_matrix = generate_connected_graph(100, p=0.2)
    # print("邻接矩阵:\n", adj_matrix, type(adj_matrix))
    # total_graph_degree = sum([sum(x) for x in adj_matrix])/2
    # print("total_graph_degree:\n", total_graph_degree)
    # # 将邻接矩阵中的数据类型变为int
    # adj_matrix = adj_matrix.astype(int)

    # subgraph, selected_physical_qubits, graph_degree = physical_qubit_selection(adj_matrix, 40, 2)
    # print("subgraph:\n", subgraph)
    # print("selected_physical_qubits:\n", selected_physical_qubits)
    # print("graph_degree:\n", graph_degree)

    # # 在同一张图中画出总图以及子图，区分节点颜色
    # G = nx.Graph(adj_matrix)
    # subgraph = G.subgraph(selected_physical_qubits)
    # pos = nx.spring_layout(G)
    # nx.draw(G, pos, with_labels=True)
    # nx.draw(subgraph, pos, with_labels=True, node_color='red')
    # plt.show()


    # qc = random_circuit(10, 200, general_unitary_num=10, max_unitary_qubit_num=5)
    # print(qc)
    # qc = transpile(
    #     circuit=qc,
    #     basis_single_qubit_gate=None,
    #     basis_double_qubit_gate=None,
    #     decomposition_method=None,
    #     single_qubit_gate_reduction_level=None,
    #     double_qubit_gate_reduction_method=None,
    #     backend=None,
    #     chip_topology=adj_matrix,
    #     starting_physical_qubit_num=None,
    #     physical_qubit_fidelity=None
    #     )
    
    # num_qubits = 3
    # cir = QuantumCircuit(num_qubits)
    # mat = np.array([[1, 1], [1, -1]] / np.sqrt(2), dtype=np.complex128)
    # CCH = MCUGate(mat, [0, 1], [2])
    # print("transpiler quantum circuit: ")
    # print(CCH.params)
    # cir.append_mcugate(CCH, [[0, 1], [2]])
    

    # # # quantum chip layout
    # layout = np.ones((num_qubits, num_qubits), dtype=np.int8)
    # # # start to transpile
    # transpiled_circuit, _, _ = transpile(cir, chip_topology=layout)
    # # print("Transpiled Circuit:")
    # # print(type(transpiled_circuit[0].data))
    # print(transpiled_circuit)
    
    # qubit = cirq.LineQubit.range(3)
    # cir = cirq.Circuit()
    # # cir.append(cirq.X(qubit[0]))
    # # cir.append(cirq.X(qubit[1]))
    # for gate in transpiled_circuit[0].data:
    #     if gate[0].upper() == 'RZ':
    #         cir.append(cirq.rz(gate.theta)(qubit[gate[1][0]]))
    #     elif gate[0].upper() == 'SX':
    #         cir.append(cirq.XPowGate(exponent=0.5)(qubit[gate[1][0]]))
    #     elif gate[0].upper() == 'CX':
    #         cir.append(cirq.CNOT(qubit[gate[1][0]], qubit[gate[1][1]]))
    #     else:
    #         raise ValueError(f"The gate is not in base gate, {gate[0]}")

    # print(cir)

    # sim = cirq.Simulator()
    # result = sim.simulate(program=cir)
    # print("拆解后的模拟结果：")
    # print(result.final_state_vector)

    # # 对比试验
    # circuit_real = cirq.Circuit()
    # # circuit_real.append(cirq.X(qubit[0]))
    # # circuit_real.append(cirq.X(qubit[1]))
    # ch = cirq.ControlledGate(sub_gate=cirq.H, num_controls=2)
    # print(cirq.unitary(ch(qubit[0], qubit[1], qubit[2])))
    # circuit_real.append(ch(qubit[0], qubit[1], qubit[2]))
    # print(circuit_real)
    # result = sim.simulate(program=circuit_real)
    # print("原始线路图运行结果：")
    # print(result.final_state_vector)
    
    
    # udevadm info --query=all --name=/dev/sda | grep ID_SERIAL
    # ip link show ens5f0np0 | grep -oP 'link/ether \K[^ ]+'
    # free -h
    # cat /proc/cpuinfo
    # fdisk -l /dev/sda