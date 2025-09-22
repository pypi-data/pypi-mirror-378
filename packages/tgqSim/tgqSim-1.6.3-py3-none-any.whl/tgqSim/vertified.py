import numpy as np
import cirq
from test_code import get_transpiler_circuit

circuit = get_transpiler_circuit()
print("After transpiler quantum circuit: ")
print(circuit)

qubit = cirq.LineQubit.range(4)
cir = cirq.Circuit()
# cir.append(cirq.X(qubit[0]))
# cir.append(cirq.X(qubit[1]))
for gate in circuit:
    if gate.name.upper() == 'RZ':
        cir.append(cirq.rz(gate.theta)(qubit[gate.on_qubits[0].index()]))
    elif gate.name.upper() == 'SQRT_X':
        cir.append(cirq.XPowGate(exponent=0.5)(qubit[gate.on_qubits[0].index()]))
    elif gate.name.upper() == 'CZ':
        cir.append(cirq.CZ(qubit[gate.on_qubits[0].index()], qubit[gate.on_qubits[1].index()]))
    else:
        raise ValueError(f"The gate is not in base gate, {gate.name}")

print(cir)

sim = cirq.Simulator()
result = sim.simulate(program=cir)
print("拆解后的模拟结果：")
print(result.final_state_vector)

# 对比试验
circuit_real = cirq.Circuit()
circuit_real.append(cirq.H(qubit[0]))
circuit_real.append(cirq.X(qubit[1]))
circuit_real.append(cirq.H(qubit[2]))
circuit_real.append(cirq.CNOT(qubit[0], qubit[1]))
circuit_real.append(cirq.H(qubit[3]))
ch = cirq.ControlledGate(cirq.H, num_controls=1)
circuit_real.append(ch(qubit[3], qubit[0]))
print(circuit_real)
result = sim.simulate(program=circuit_real)
print("原始线路图运行结果：")
print(result.final_state_vector)
