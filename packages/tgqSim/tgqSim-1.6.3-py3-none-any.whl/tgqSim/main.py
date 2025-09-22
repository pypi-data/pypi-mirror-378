from circuit.quantum_circuit import QuantumCircuit
from gate.operation import Operation
from gate.bit import QuantumRegister, Qubit
import numpy as np
from circuit.decompose.compiler import transpile
from gate.single_gate import SingleGate
from gate.double_gate import DoubleGate
from gate.multi_gate import MQGate
from copy import deepcopy

import cirq

def RxxGate(theta: float, x: float =0.0) -> np.ndarray:
    """
    Rxx gate matrix.
    """
    return np.array([[np.cos(theta / 2), x, x, -1j * np.sin(theta / 2)],
                     [x, np.cos(theta / 2), -1j * np.sin(theta / 2), x],
                     [x, -1j * np.sin(theta / 2), np.cos(theta / 2), x],
                     [-1j * np.sin(theta / 2), x, x, np.cos(theta / 2)]])

if __name__ == '__main__':
    # 创建一个量子寄存器
    num_qubits = 4
    qreg = QuantumRegister(size=num_qubits, name="qreg")

    # 创建一个线路的实例
    circuit = QuantumCircuit(num_qubits=num_qubits, qreg=qreg)

    # 构建线路
    # 0: ─H──@──@────────────────M─────
    #        │  │                ║
    # 1: ─X──X──RxGate(0.79, 0)──╫──M──
    #           │                ║  ║
    # 2: ───────RxGate(0.79, 0)──╫──╫──
    #                            ║  ║
    # 3: ────────────────────────╫──╫──
    #                            ║  ║
    # c: ════════════════════════╩══╩══
    #                            1  0
    # 添加常见门直接使用方法
    circuit.h(qreg[0])
    circuit.x(qreg[1])
    circuit.cnot(qreg[0], qreg[1])
    CRxxGate = Operation(name="RxGate", on_qubits=[qreg[1], qreg[2]], matrix=RxxGate, num_qubits=2, theta=np.pi / 4, x=0).control_by(qreg[0])
    # 不常见的门或自定义门，直接通过append加入
    circuit.append(CRxxGate)

    # 增加测量位，将q0测量结果放在经典比特1号位置；将q1测量结果放在经典比特0号位置；
    circuit.measure(target_qubit=[qreg[0], qreg[1]], classical_register=[1, 0])

    # 打印线路
    print("Quantum Circuit:")
    print(circuit)

    # 线路基本信息
    print("线路图的数量：")
    print(f"circuit.num_gate: {circuit.num_gate}")
    print(f"circuit.num_sgate: {circuit.num_sgate}")
    print(f"circuit.num_dgate : {circuit.num_dgate}")
    print(f"circuit.classical_register: {circuit.classical_register}")
    print(f"circuit.num_qubits: {circuit.num_qubits}")

    # 获取仅包含双比特门组成的线路
    double_gate_circuit = circuit.filter_two_qubit_gates()
    print("only containe two qubite gate:")
    print(double_gate_circuit)

    # 对线路中所有的量子门进行遍历以及获取gate相关的信息
    for gate in circuit:
        print(f"gate.name: {gate.name}")
        print(f"作用的比特位信息：")
        print(gate.on_qubits)
        print("获取通过control_by的控制位信息:")
        print(gate.ctrl_qubits)
        print("获取量子门对应的矩阵：")
        print(gate.params)
        if isinstance(gate, SingleGate) or isinstance(gate, MQGate):
            print("会有target_qubit获取作用的比特信息")
            print(gate.target_qubit)
        else:
            print("会有target_qubit获取作用的比特信息")
            print(gate.target_qubit)
            print("会有control_qubit获取作用的比特信息")
            print(gate.control_qubit)
        print()

    # 可直接判断当前门是否在线路图中，注意，不单单是判断门的名称，量子门作用在不同的比特位都是不同的门
    print(circuit[0] in circuit)

    # 可以通过len获取线路中量子门的个数
    print(f"The number of gate in current quantum circuit: {len(circuit)}")

    # 将线路中所有的H门作用到qreg[3]上
    print("old quantum circuit:")
    print(circuit)
    for gate in circuit:
        if gate.name.upper() == 'H':
            gate.on_qubits = [qreg[3]]
            print(gate.on_qubits)
            print(gate.display_name)
    print("new quantum circuit:")
    print(circuit)

    # 将两个线路融合在一起，注意测量门不融合，以左边为主
    qreg1 = QuantumRegister(3)
    cir = QuantumCircuit(3, qreg=qreg1)
    cir.h(qreg1[0])
    cir.s_dag(qreg1[2])
    cir.cnot(control_qubit=qreg1[0], target_qubit=qreg1[2])
    cir.measure([qreg[0], qreg[2]], classical_register=[0, 1])
    # 输出：
    # 0: ─H───@──M─────
    #         │  ║
    # 1: ─────┼──╫─────
    #         │  ║
    # 2: ─S†──X──╫──M──
    #            ║  ║
    # c: ════════╩══╩══
    #            0  1
    print(cir)
    # print(cir.display_list)
    # cir.show_quantum_circuit()

    circuit.extend(cir=cir)
    # 0: ────@──@────────────────H───@──M─────
    #        │  │                    │  ║
    # 1: ─X──X──RxGate(0.79, 0)──────┼──╫──M──
    #           │                    │  ║  ║
    # 2: ───────RxGate(0.79, 0)──S†──X──╫──╫──
    #                                   ║  ║
    # 3: ─H─────────────────────────────╫──╫──
    #                                   ║  ║
    # c: ═══════════════════════════════╩══╩══
    #                                   1  0
    print("融合后的线路图:")
    print(circuit)
    
    original_circuit = deepcopy(circuit)

    # print(circuit.display_list)

    # 芯片拓扑结构
    chip_topology = np.ones(shape=(circuit.num_qubits, circuit.num_qubits), dtype=np.int8)

    transpiled_circuit, _, _ = transpile(
        circuit=circuit,
        basis_double_qubit_gate=["cz"],
        basis_single_qubit_gate=["x", "y", "rx", "ry", "rz", "sx"],
        chip_topology=chip_topology,
        starting_physical_qubit_num=circuit.num_qubits
    )

    # print("transpiled circuit: ")
    # print(transpiled_circuit)
    # print(circuit)

    # 测试
    print("original circuit by cirq:")
    cirq_circuit = cirq.Circuit()
    qubit = cirq.LineQubit.range(num_qubits)
    for gate in original_circuit:
        if gate.name.upper() == 'X':
            cirq_circuit.append(cirq.X(qubit[gate.on_qubits[0].index()]))
        elif gate.name.upper() == 'H':
            cirq_circuit.append(cirq.H(qubit[gate.on_qubits[0].index()]))
        elif gate.name.upper() == 'CNOT':
            cirq_circuit.append(cirq.CNOT(qubit[gate.on_qubits[0].index()], qubit[gate.on_qubits[1].index()]))
        elif gate.name.upper() == 'S_DAG':
            cirq_circuit.append(cirq.S(qubit[gate.on_qubits[0].index()])**-1)
        else:
            # print(gate.name)
            matrix = gate.matrix
            # print(matrix)
            # print(gate.on_qubits)
            rxGate = cirq.MatrixGate(matrix=matrix)
            ctrl_rxGate = cirq.ControlledGate(rxGate, num_controls=len(gate.ctrl_qubits))
            cirq_circuit.append(ctrl_rxGate(qubit[gate.ctrl_qubits[0].index()], qubit[gate.on_qubits[0].index()], qubit[gate.on_qubits[1].index()]))
    print("original circuit by cirq:")
    print(cirq_circuit)
    
    # 0: ───────@───@───────────────────────────────────────────────────────H──────@───
    #           │   │                                                              │
    #           │   ┌                                                   ┐          │
    #           │   │0.924+0.j    0.   +0.j    0.   +0.j    0.   -0.383j│          │
    # 1: ───X───X───│0.   +0.j    0.924+0.j    0.   -0.383j 0.   +0.j   │──────────┼───
    #               │0.   +0.j    0.   -0.383j 0.924+0.j    0.   +0.j   │          │
    #               │0.   -0.383j 0.   +0.j    0.   +0.j    0.924+0.j   │          │
    #               └                                                   ┘          │
    #               │                                                              │
    # 2: ───────────#2──────────────────────────────────────────────────────S^-1───X───

    # 3: ───H──────────────────────────────────────────────────────────────────────────

    # 拆解后线路的构建(cirq)
    cir = cirq.Circuit()
    for gate in transpiled_circuit:
        if gate.name.upper() == 'RZ':
            cir.append(cirq.rz(gate.theta)(qubit[gate.on_qubits[0].index()]))
        elif gate.name.upper() == 'SQRT_X':
            cir.append(cirq.XPowGate(exponent=0.5)(qubit[gate.on_qubits[0].index()]))
        elif gate.name.upper() == 'CZ':
            cir.append(cirq.CZ(qubit[gate.on_qubits[0].index()], qubit[gate.on_qubits[1].index()]))
        else:
            raise ValueError(f"The gate is not in base gate, {gate.name}")
    # print("拆解后的线路图(cirq):")
    # print(cir)
    
    sim = cirq.Simulator()
    original_result = sim.simulate(program=cirq_circuit).final_state_vector
    transpile_result = sim.simulate(program=cir).final_state_vector
    
    print("原始线路图运行结果：")
    # print(original_result)
    # [ 0.        +0.j  0.        +0.j  0.        +0.j  0.        +0.j
    #   0.49999997+0.j  0.49999997+0.j  0.        +0.j  0.        +0.j
    #   0.        +0.j  0.        +0.j -0.        +0.j -0.        +0.j
    #   0.        +0.j  0.        +0.j  0.49999997+0.j  0.49999997+0.j]
    
    print("拆解后的线路图运行结果：")
    print(transpile_result)
    # 这个拆分出来线路的模拟出来的结果
    # 差了一个整体相位
    # [ 8.9562050e-08+1.2117219e-07j  8.9562050e-08+1.2117219e-07j
    #   3.6878493e-08-5.2683529e-09j  3.6878493e-08-5.2683538e-09j
    #   3.5355237e-01-3.5355264e-01j  3.5355237e-01-3.5355264e-01j
    #  -1.2644054e-07-4.2146848e-08j -1.2644054e-07-4.2146848e-08j
    #   1.6858739e-07+1.0536714e-08j  1.6858739e-07+1.0536710e-08j
    #  -4.2146844e-08+9.4830398e-08j -4.2146844e-08+9.4830398e-08j
    #   4.2146844e-08-4.2146844e-08j  4.2146844e-08-4.2146844e-08j
    #   3.5355246e-01-3.5355246e-01j  3.5355246e-01-3.5355246e-01j]