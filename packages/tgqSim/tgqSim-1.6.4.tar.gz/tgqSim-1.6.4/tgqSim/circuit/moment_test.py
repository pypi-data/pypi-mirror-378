from gate.bit import QuantumRegister
from gate.single_gate import X, Y, Z
from gate.double_gate import CNOT
from circuit.quantum_circuit_v3 import QuantumCircuit
from circuit.moment import Moment

# 初始化量子比特

# 创建线路
qc = QuantumCircuit(3)

# 构造 Moment 0：X(q0), Y(q2)
moment0 = Moment()
moment0.add_gate(X(0))
moment0.add_gate(Y(2))
qc.append_moment(moment0)
# qc.append(X(q0))  # 保持circuit结构同步
# qc.append(Y(q2))

# 构造 Moment 1：CNOT(q0, q1)
moment1 = Moment()
moment1.add_gate(CNOT(0, 1))
qc.append_moment(moment1)
# qc.append(CNOT(q0, q1))

# 构造 Moment 2：Z(q2)
moment2 = Moment()
moment2.add_gate(CNOT(2, 1))
qc.append_moment(moment2)
# qc.append(Z(q2))

# 构造 Moment 3：测量
# qc.measure([q0, q1, q2])

# 打印线路按层结构
print(qc)
