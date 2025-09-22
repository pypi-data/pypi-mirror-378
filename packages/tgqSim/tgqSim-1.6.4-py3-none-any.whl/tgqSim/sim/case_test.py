from turtledemo.sorting_animate import qsort

import cirq
from qiskit.pulse import num_qubits
import numpy as np

from build_tensor_from_gates_v3 import build_tensor_graph_from_circuit
from tensor_graph_scheduler_v2 import TensorGraphScheduler

def simulate_cirq_amplitude(num_qubits=20, bitstring="0"*20):
    qubits = cirq.LineQubit.range(num_qubits)

    # 构建电路：Hadamard + 链式CNOT
    circuit = cirq.Circuit()
    for q in qubits:
        circuit.append(cirq.H(q))
    for i in range(num_qubits - 1):
        circuit.append(cirq.CNOT(qubits[i], qubits[i + 1]))

    simulator = cirq.Simulator()
    result = simulator.simulate(circuit)

    final_state = result.final_state_vector

    # 将bitstring转换为索引
    index = int(bitstring, 2)
    amp = final_state[index]

    print(f"Cirq 模拟得到振幅（|{bitstring}⟩）: {amp}")
    return circuit, amp

def simulate_tensor_graph_amplitude(circuit, bitnum):
    tg = build_tensor_graph_from_circuit(circuit)
    tg.set_initial_state_from_bitstring("0" * bitnum)
    tg.set_final_state_from_bitstring("0" * bitnum)

    scheduler = TensorGraphScheduler(tg)
    scheduler.run()
    print("\n=== FINAL EDGE SUMMARY ===\n")
    print("单振幅算法结果\n")
    scheduler.summary()
    # print(f"张量图模拟结果振幅（|{bitstring}⟩）: {amp}")


if __name__ == "__main__":
    num = 11

    ###########QFT算法
    # 创建11个量子比特
    qubits = [cirq.LineQubit(i) for i in range(11)]

    # 创建量子电路
    circuit = cirq.Circuit()

    # 初始 H 门
    for i in range(9):
        circuit.append(cirq.H(qubits[i]))

    # 初始化 X 门
    circuit.append(cirq.X(qubits[9]))

    # H-CX-H 结构
    circuit.append(cirq.H(qubits[10]))
    circuit.append(cirq.CNOT(qubits[10], qubits[9]))
    circuit.append(cirq.H(qubits[10]))


    # CPhase 门定义
    def cphase(theta, control, target):
        return cirq.CZPowGate(exponent=theta / np.pi)(control, target)


    # 第一组 CPhase 门
    circuit.append([
        cphase(1.570796, qubits[9], qubits[10]),
        cphase(0.785398, qubits[8], qubits[10]),
        cphase(0.392699, qubits[7], qubits[10]),
        cphase(0.19635, qubits[6], qubits[10]),
        cphase(0.098175, qubits[5], qubits[10]),
        cphase(0.049087, qubits[4], qubits[10]),
        cphase(0.024544, qubits[3], qubits[10]),
        cphase(0.012272, qubits[2], qubits[10]),
        cphase(0.006136, qubits[1], qubits[10]),
        cphase(0.003068, qubits[0], qubits[10])
    ])

    # H 门和 CPhase 门循环（简化）
    for target in range(9, 0, -1):
        circuit.append(cirq.H(qubits[target]))
        for control in range(target - 1, -1, -1):
            angle = 1.570796 / (2 ** (target - control))
            circuit.append(cphase(angle, qubits[control], qubits[target]))

    # H 门和 X 门
    circuit.append(cirq.H(qubits[0]))
    circuit.append(cirq.X(qubits[0]))

    # Swap 门
    swap_pairs = [(0, 10), (1, 9), (2, 8), (4, 6)]
    for q1, q2 in swap_pairs:
        circuit.append(cirq.SWAP(qubits[q1], qubits[q2]))

    ###########
    ############量子加法器
    # 创建10个量子比特
    # qubits = [cirq.LineQubit(i) for i in range(10)]
    #
    # # 创建量子电路
    # circuit = cirq.Circuit()
    #
    # # 初始 X 门
    # initial_x_gates = [1, 2, 3, 4]
    # for i in initial_x_gates:
    #     circuit.append(cirq.X(qubits[i]))
    #
    # # 第一轮 Swap 门
    # swap_sequence_1 = [(5, 6), (4, 5), (3, 4), (2, 3), (1, 2)]
    # for q1, q2 in swap_sequence_1:
    #     circuit.append(cirq.SWAP(qubits[q1], qubits[q2]))
    #
    # # CX 门
    # circuit.append(cirq.CNOT(qubits[0], qubits[1]))
    #
    # # 第二轮 Swap 门
    # swap_sequence_2 = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (3, 4), (4, 5)]
    # for q1, q2 in swap_sequence_2:
    #     circuit.append(cirq.SWAP(qubits[q1], qubits[q2]))
    #
    # # 第一个 CCX 和 CX
    # circuit.append(cirq.CCNOT(qubits[5], qubits[6], qubits[7]))
    # circuit.append(cirq.CNOT(qubits[5], qubits[6]))
    #
    # # 第三轮 Swap 门
    # swap_sequence_3 = [
    #     (4, 5), (3, 4), (1, 2), (2, 3),
    #     (3, 4), (4, 5), (5, 6)
    # ]
    # for q1, q2 in swap_sequence_3:
    #     circuit.append(cirq.SWAP(qubits[q1], qubits[q2]))
    #
    # # 第二个 CCX 和 CX
    # circuit.append(cirq.CCNOT(qubits[6], qubits[7], qubits[8]))
    # circuit.append(cirq.CNOT(qubits[6], qubits[7]))
    #
    # # 第四轮 Swap 门
    # swap_sequence_4 = [
    #     (5, 6), (4, 5), (3, 4), (2, 3),
    #     (1, 2), (4, 5), (5, 6)
    # ]
    # for q1, q2 in swap_sequence_4:
    #     circuit.append(cirq.SWAP(qubits[q1], qubits[q2]))
    #
    # # 第三个 CCX 和 CX
    # circuit.append(cirq.CCNOT(qubits[6], qubits[7], qubits[8]))
    # circuit.append(cirq.CNOT(qubits[6], qubits[7]))
    #
    # # 第五轮 Swap 门
    # swap_sequence_5 = [
    #     (5, 6), (4, 5), (2, 3), (3, 4),
    #     (4, 5), (5, 6), (6, 7)
    # ]
    # for q1, q2 in swap_sequence_5:
    #     circuit.append(cirq.SWAP(qubits[q1], qubits[q2]))
    #
    # # 第四个 CCX 和 CX
    # circuit.append(cirq.CCNOT(qubits[7], qubits[8], qubits[9]))
    # circuit.append(cirq.CNOT(qubits[7], qubits[8]))
    #
    # # 第六轮 Swap 门
    # swap_sequence_6 = [
    #     (6, 7), (5, 6), (4, 5), (3, 4),
    #     (2, 3), (5, 6), (6, 7)
    # ]
    # for q1, q2 in swap_sequence_6:
    #     circuit.append(cirq.SWAP(qubits[q1], qubits[q2]))
    #
    # # 最后一个 CCX 和 CX
    # circuit.append(cirq.CCNOT(qubits[7], qubits[8], qubits[9]))
    # circuit.append(cirq.CNOT(qubits[7], qubits[8]))
    #
    # # 最后一轮 Swap 门
    # swap_sequence_7 = [(6, 7), (5, 6)]
    # for q1, q2 in swap_sequence_7:
    #     circuit.append(cirq.SWAP(qubits[q1], qubits[q2]))
    #############

    ##########三整数加法器
    # qubits = [cirq.LineQubit(i) for i in range(12)]
    #
    # # 创建量子电路
    # circuit = cirq.Circuit()
    #
    # # 初始化X门
    # initial_x_gates = [0, 1, 2, 5, 6, 7]
    # for i in initial_x_gates:
    #     circuit.append(cirq.X(qubits[i]))
    #
    # # CCX (Toffoli) 门
    # circuit.append(cirq.CCNOT(qubits[0], qubits[1], qubits[3]))
    # circuit.append(cirq.CCNOT(qubits[5], qubits[6], qubits[8]))
    #
    # # CX (CNOT) 门
    # circuit.append(cirq.CNOT(qubits[0], qubits[1]))
    # circuit.append(cirq.CNOT(qubits[5], qubits[6]))
    #
    # # 进一步的 CCX 门
    # circuit.append(cirq.CCNOT(qubits[1], qubits[2], qubits[4]))
    # circuit.append(cirq.CCNOT(qubits[6], qubits[7], qubits[9]))
    #
    # # 继续的 CX 门
    # circuit.append(cirq.CNOT(qubits[1], qubits[2]))
    # circuit.append(cirq.CNOT(qubits[3], qubits[4]))
    # circuit.append(cirq.CNOT(qubits[6], qubits[7]))
    # circuit.append(cirq.CNOT(qubits[8], qubits[9]))
    #
    # # CCX 和 CX 门
    # circuit.append(cirq.CCNOT(qubits[4], qubits[7], qubits[10]))
    # circuit.append(cirq.CNOT(qubits[4], qubits[7]))
    # circuit.append(cirq.CCNOT(qubits[9], qubits[10], qubits[11]))
    # circuit.append(cirq.CNOT(qubits[9], qubits[10]))
    ################

    #############QAOA最大分割
    # qubits = [cirq.LineQubit(i) for i in range(4)]
    #
    # # 创建量子电路
    # circuit = cirq.Circuit()
    #
    # # 添加H门
    # circuit.append([cirq.H(qubits[i]) for i in range(4)])
    #
    #
    # # 添加RZZ门（自定义）
    # def rzz(theta, q1, q2):
    #     return cirq.ZZPowGate(exponent=theta / np.pi)(q1, q2)
    #
    #
    # # 第一组RZZ门
    # circuit.append([
    #     rzz(2.270266, qubits[0], qubits[1]),
    #     rzz(2.270266, qubits[1], qubits[2]),
    #     rzz(2.270266, qubits[2], qubits[3]),
    #     rzz(2.270266, qubits[0], qubits[3])
    # ])
    #
    # # 添加RX门
    # circuit.append([cirq.rx(1.450496)(qubits[i]) for i in range(4)])
    #
    # # 第二组RZZ门
    # circuit.append([
    #     rzz(1.749331, qubits[0], qubits[1]),
    #     rzz(1.749331, qubits[1], qubits[2]),
    #     rzz(1.749331, qubits[2], qubits[3]),
    #     rzz(1.749331, qubits[0], qubits[3])
    # ])
    #
    # # 添加第二组RX门
    # circuit.append([cirq.rx(0.86014)(qubits[i]) for i in range(4)])
    #############

    ###########
    # 三比特例子
    # q0, q1, q2, q3 = cirq.LineQubit.range(4)
    # # qbits = cirq.LineQubit.range(num)
    # circuit = cirq.Circuit(
    #     # cirq.H(q) for q in qbits
    #     cirq.X(q0),
    #     cirq.H(q1),
    #     cirq.CNOT(q3, q2),
    #     # cirq.CNOT(q1, q2),
    #     # cirq.H(q2)
    # )
    ##############

    ######################
    ##### 创建 10 个 qubit
    # qubits = cirq.LineQubit.range(num)
    #
    # ##### 构建电路
    # circuit = cirq.Circuit()
    #
    # #### 步骤 1：每个 qubit 一个 H 门
    # circuit += [cirq.H(q) for q in qubits]
    #
    # ##### 步骤 2：链式 CNOT（q0→q1→q2→...→q9）
    # circuit += [cirq.CNOT(qubits[i], qubits[i + 1]) for i in range(num-1)]
    #
    # ##### 步骤 3：最后一个 qubit 加 H
    # circuit.append(cirq.H(qubits[-1]))
    ########################

    ##################
    ####两整数加法器
    # 创建 10 个连续的 LineQubit：q[0] 到 q[9]
    # qubits = cirq.LineQubit.range(num)
    #
    # circuit = cirq.Circuit()
    #
    # # 追加对应的门操作
    # circuit.append(cirq.X(qubits[1]))
    # circuit.append(cirq.X(qubits[2]))
    # circuit.append(cirq.X(qubits[3]))
    # circuit.append(cirq.X(qubits[4]))
    #
    # circuit.append(cirq.CNOT(qubits[0], qubits[6]))
    # circuit.append(cirq.CCNOT(qubits[3], qubits[6], qubits[7]))
    # circuit.append(cirq.CNOT(qubits[3], qubits[6]))
    # circuit.append(cirq.CCNOT(qubits[1], qubits[7], qubits[8]))
    # circuit.append(cirq.CNOT(qubits[1], qubits[7]))
    # circuit.append(cirq.CCNOT(qubits[4], qubits[7], qubits[8]))
    # circuit.append(cirq.CNOT(qubits[4], qubits[7]))
    # circuit.append(cirq.CCNOT(qubits[2], qubits[8], qubits[9]))
    # circuit.append(cirq.CNOT(qubits[2], qubits[8]))
    # circuit.append(cirq.CCNOT(qubits[5], qubits[8], qubits[9]))
    # circuit.append(cirq.CNOT(qubits[5], qubits[8]))
    ###################

    ####################
    # 量子相位估计
    # qubits = cirq.LineQubit.range(5)
    # q = qubits  # 便于与原始标号一致
    #
    # # 构建量子线路
    # circuit = cirq.Circuit()
    #
    # # 单比特门
    # circuit.append(cirq.H(q[0]))
    # circuit.append(cirq.H(q[1]))
    # circuit.append(cirq.H(q[2]))
    # circuit.append(cirq.H(q[3]))
    # circuit.append(cirq.X(q[4]))
    #
    # # 多次 CPHASE 操作（角度为 0.785398 ≈ π/4）
    # theta = 0.785398
    # circuit.append(cirq.CZPowGate(exponent=theta / np.pi)(q[0], q[4]))
    # circuit.append(cirq.CZPowGate(exponent=theta / np.pi)(q[1], q[4]))
    # circuit.append(cirq.CZPowGate(exponent=theta / np.pi)(q[1], q[4]))
    # circuit.append(cirq.CZPowGate(exponent=theta / np.pi)(q[2], q[4]))
    # circuit.append(cirq.CZPowGate(exponent=theta / np.pi)(q[2], q[4]))
    # circuit.append(cirq.CZPowGate(exponent=theta / np.pi)(q[2], q[4]))
    # circuit.append(cirq.CZPowGate(exponent=theta / np.pi)(q[2], q[4]))
    # circuit.append(cirq.CZPowGate(exponent=theta / np.pi)(q[3], q[4]))
    # circuit.append(cirq.CZPowGate(exponent=theta / np.pi)(q[3], q[4]))
    # circuit.append(cirq.CZPowGate(exponent=theta / np.pi)(q[3], q[4]))
    # circuit.append(cirq.CZPowGate(exponent=theta / np.pi)(q[3], q[4]))
    # circuit.append(cirq.CZPowGate(exponent=theta / np.pi)(q[3], q[4]))
    # circuit.append(cirq.CZPowGate(exponent=theta / np.pi)(q[3], q[4]))
    # circuit.append(cirq.CZPowGate(exponent=theta / np.pi)(q[3], q[4]))
    # circuit.append(cirq.CZPowGate(exponent=theta / np.pi)(q[3], q[4]))
    #
    # # swap门
    # circuit.append(cirq.SWAP(q[1], q[2]))
    # circuit.append(cirq.SWAP(q[0], q[3]))
    #
    # # 接下来的H和cphase系列
    # circuit.append(cirq.H(q[0]))
    # circuit.append(cirq.CZPowGate(exponent=-1.570796 / np.pi)(q[0], q[1]))
    # circuit.append(cirq.H(q[1]))
    # circuit.append(cirq.CZPowGate(exponent=-1.570796 / np.pi)(q[1], q[2]))
    # circuit.append(cirq.CZPowGate(exponent=-0.785398 / np.pi)(q[0], q[2]))
    # circuit.append(cirq.H(q[2]))
    # circuit.append(cirq.CZPowGate(exponent=-1.570796 / np.pi)(q[2], q[3]))
    # circuit.append(cirq.CZPowGate(exponent=-0.785398 / np.pi)(q[1], q[3]))
    # circuit.append(cirq.CZPowGate(exponent=-0.392699 / np.pi)(q[0], q[3]))
    # circuit.append(cirq.H(q[3]))
    #####################

    # circuit, amp = simulate_cirq_amplitude(20, "0"*20)
    print("=== CIRCUIT ===")
    print(circuit)
    print("\n=== CIRCUIT FINAL STATE ===\n")
    # print(amp)
    # print(circuit)
    # 模拟器
    simulator = cirq.Simulator()
    result = simulator.simulate(circuit)

    # 获取末态向量
    final_state = result.final_state_vector

    # 打印所有 basis state 的振幅
    # print("\ncirq结果所有末态的振幅（basis |000⟩ ~ |111⟩）：")
    num_qubits = num
    # qState = "0"*num
    # qState = format(489, f'0{num_qubits}b')
    # qState = "01001"
    # qState = "11100"
    qState = "01001"
    for i, amp in enumerate(final_state):
        ###########
        # if amp != 0:
        #     # 只打印非零振幅的基态
        #     print("非零振幅的基态：\n")
        #     print(f"{i} \n")
        #     bitstring = format(i, f'0{num_qubits}b')
        #     print(f"|{bitstring}⟩ : amplitude = {amp}")
        #     observe_state = i
        #     qState = format(observe_state, "0{}b".format(num))
        #     #################
        bitstring = format(i, f'0{num_qubits}b')
        print(f"|{bitstring}⟩ : amplitude = {amp}")
    # bitstring = format(qState, f'0{num_qubits}b')
    # print(f"|{qState}⟩ : amplitude = {final_state[0]}")

    # simulate_tensor_graph_amplitude(circuit, 20)
    reversec_qstate = qState

    tg = build_tensor_graph_from_circuit(circuit)
    tg.set_initial_state_from_bitstring("0"*num)
    tg.set_final_state_from_bitstring(qState)

    scheduler = TensorGraphScheduler(tg)
    scheduler.run()
    used_vertices = set()
    for edge in scheduler.graph.tensor_edges:
        used_vertices.update(edge.input_vertices + edge.output_vertices)

    qubit_used = sorted({v[0] for v in used_vertices})
    print(f"✅ 最终参与路径的 qubit 数组: {qubit_used}")

    print("\n=== FINAL EDGE SUMMARY ===")
    scheduler.summary()
    print(scheduler.compute_amplitude_from_tensor_graph())

