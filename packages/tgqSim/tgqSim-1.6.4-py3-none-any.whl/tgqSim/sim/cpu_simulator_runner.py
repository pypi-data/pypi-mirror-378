from tgqSim.circuit.quantum_circuit import QuantumCircuit
from tgqSim.kernel.SingleGate import ActOn_State as SingleAct
from tgqSim.kernel.DoubleGate import ActOn_State as DoubleAct
from tgqSim.kernel.TripleGate import ActOn_State as TripleAct
import numpy as np

def run_with_cpu_device(circuit: QuantumCircuit) -> np.ndarray:
    state = np.zeros(2 ** circuit.num_qubits, dtype=complex)
    state[0] = 1.0
    for gate in circuit:
        # print(f"name: {gate.name}, matrix: {gate.matrix}")
        # qargs = [qb for qb in gate.target_qubits]
        if gate.matrix.shape == (2, 2):
            state = SingleAct(state, circuit.num_qubits, gate.matrix, gate.target_qubits, gate.ctrl_qubits)
        elif gate.matrix.shape == (4, 4):
            state = DoubleAct(state, circuit.num_qubits, gate.matrix, gate.target_qubits, gate.ctrl_qubits)
        elif gate.matrix.shape == (8, 8):
            state = TripleAct(state, circuit.num_qubits, gate.matrix, gate.target_qubits, gate.ctrl_qubits)
        else:
            raise ValueError("Unsupported gate matrix shape.")
        # print(state)
        # print("\n\n")
    return state