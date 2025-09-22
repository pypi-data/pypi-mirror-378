from backend.super_conducting import GJQ
from circuit.quantum_circuit import QuantumCircuit
from gate.single_gate import *
from gate.double_gate import *
from sim.QuantumSimulator_v2 import QuantumSimulator

import cirq

def reverse_binary_to_decimal(number: int, num_binary: int):
    number_bin = format(number, f"0{num_binary}b")
    print(number_bin)
    number_bin_reverse = number_bin[::-1]
    print(number_bin_reverse)
    return int(number_bin_reverse, 2)

def XGate(x: float) -> np.ndarray:
    return np.array([
        [0, x],
        [x, 0]
    ])

if __name__ == '__main__':
    # gjq = GJQ(token="eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ3YW5nemhpcWlhbmciLCJpc3MiOiIyMjcxNDY0OTc3NTc2NDY4NDgiLCJleHAiOjE3NTAzMDYxODgsImlhdCI6MTc1MDMwMjU4OCwianRpIjoid2FuZ3poaXFpYW5nX0owZXRvUCJ9.XPffB8ZFvrnEA8b38b9DQVO2l0xEpNMdwYwsbJER65I")
    # provider = gjq.get_provider()
    # backends = provider.backends()
    # print(backends)
    # if 0 == len(backends):
    #     raise ValueError("The is no avariable super conductor quantum computer...")
    # backend = provider.get_backend(backend_name=backends[0])
    # # backend.configures()
    # print(f"base_singlegates: {backend.base_singlegates}")
    # print(f"base_doubleates: {backend.base_doublegates}")
    # print(f"qubits: {backend.qubits}")
    # print(f"chip_topology:\n {backend.chip_topology}")
    # print(f"qubit_fidelity: {backend.qubit_fidelity}")
    # print(f"qubit_t1: {backend.qubit_t1}")
    # print(f"qubit_t2: {backend.qubit_t2}")
    # print(f"t1_mean: {backend.t1_mean}")
    # print(f"t2_mean: {backend.t2_mean}")

    # Test the transpiler with a simple quantum circuit
    num_qubits = 3
    
    circuit = QuantumCircuit(num_qubits=num_qubits)
    print(CX(0, 1).name)
    print(CX(0, 1).control_by(2).matrix)
    print(CX(0, 1).control_by(2).params)
    print(type(CX(0, 1)))
    if isinstance(CX(0, 1), MCUGate):
        print("Type of CX is MCUGate")
    else:
        print("Type of CX Gate is not MCUGate")
    
    if isinstance(X(0).control_by(1), MCUGate):
        print("Type of CX is MCUGate")
    else:
        print("Type of CX Gate is not MCUGate")
    
    print("The matrix of CX is:")
    print(X(0).control_by(1).matrix)
    print("The params of CX is:")
    print(X(0).control_by(1).params)
    print("The data of CX:")
    print(X(0).control_by(1).data)
    print()
    print("The matrix of CCX is:")
    print(X(0).control_by(1).control_by(2).matrix)
    print("The params of CCX is (before):")
    xgate = X(0).control_by(1).control_by(2)
    print(xgate.params)
    print("The params of CCX is (after):")
    print(xgate.upload_params().params)
    print("The data of CCX:")
    print(xgate.data)
    
    print()
    print("The matrix of CX is:")
    print(MCUGate(XGate, control_qubits=0, target_qubits=1, x=1).matrix)
    print("The params of CX is:")
    print(MCUGate(XGate, control_qubits=0, target_qubits=1, x=1).params)
    print("The data of CX:")
    print(MCUGate(XGate, control_qubits=0, target_qubits=1, x=1).data)
    
    
    circuit.h(0)
    circuit.x(1)
    circuit.cnot(0, 1)
    # circuit.append(H(0).control_by(1))
    ch = MCUGate("h", control_qubits=1, target_qubits=0)
    circuit.append(ch)
    circuit.append(H(0).control_by(1))
    circuit.append(H(2))
    circuit.rx(1, 0.35)
    # circuit.cp(1, 0, 0.35)
    circuit.measure([0, 1], [0, 1])
    print(circuit[0]._data)
    print(circuit)
    sim = QuantumSimulator(device="cpu")
    result = sim.run_statevector(circuit=circuit)
    print(result)
    # result = backend.run(original_circuit=circuit)
    # print(result)
    
    
    qubit = cirq.LineQubit.range(3)
    cir = cirq.Circuit()
    
    
    cir.append(cirq.H(qubit[0]))
    cir.append(cirq.X(qubit[1]))
    cir.append(cirq.CX(qubit[0], qubit[1]))
    ch = cirq.ControlledGate(cirq.H, num_controls=1)
    cir.append(ch(qubit[1], qubit[0]))
    cir.append(ch(qubit[1], qubit[0]))
    cir.append(cirq.H(qubit[2]))
    # cir.append(cirq.cphase(np.pi/4))
    cir.append(cirq.rx(0.35)(qubit[1]))
    print(cir)
    
    sim = cirq.Simulator()
    result = sim.simulate(program=cir)
    print("拆解后的模拟结果：")
    print(result.final_state_vector)
    
    # print(reverse_binary_to_decimal(11, 4))