import numpy as np
from gate.bit import QuantumRegister
from circuit.quantum_circuit import QuantumCircuit
from QuantumSimulator_v2 import QuantumSimulator
from device.noise_models_v2 import DepolarizingNoiseModel

# 构建寄存器和电路
qreg = QuantumRegister(size=2)
qc = QuantumCircuit(2, qreg)
q0, q1 = qreg[0], qreg[1]

# Bell 态线路
qc.h(q0)
qc.cnot(q0, q1)
qc.h(q1)

# for gate in qc.circuit:
#     print(f"门: {gate.name}, 作用于量子比特: {[qb.index() for qb in gate.on_qubits]}, 矩阵：{gate.matrix}， 矩阵的数据类型: {type(gate.matrix)}")
# 应用退极化噪声（概率 0.2）
noise_model = DepolarizingNoiseModel(error_rate=0.7)

# 创建模拟器
simulator = QuantumSimulator(noise_model=noise_model)

# 执行模拟，获取采样结果
result = simulator.execute(qc, shots=1000)
print("带噪声后的测量结果分布：")
print(result)
