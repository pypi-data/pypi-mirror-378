from typing import List, Optional
from gate.instruction import Instruction
from gate.bit import Qubit
from circuit.quantum_circuit import QuantumCircuit

class _Measurement:
    """Internal class to represent a measurement operation as a 'gate'."""
    def __init__(self, qubit):
        self.name = "M"
        self._on_qubits = [qubit]

    @property
    def on_qubits(self):
        return self._on_qubits

class Moment:
    """
    A Moment represents a set of quantum gates (including measurements)
    that can be executed in parallel (i.e., acting on disjoint qubits).
    """
    def __init__(self, gates: Optional[List[Instruction]] = None):
        self._gates: List = list(gates) if gates else []
        self._qubit_set = set()

    def add_gate(self, gate) -> None:
        self._gates.append(gate)
        for qb in gate.on_qubits:
            self._qubit_set.add(qb)

    def __iter__(self):
        """
        Return an iterator over the gates in this moment.
        """
        return iter(self._gates)

    def __len__(self):
        """
        Return the number of gates in this moment.
        """
        return len(self._gates)

    def __repr__(self):
        """
        Return a string representation of the Moment for debugging.
        """
        return f"Moment({self._gates})"

    def has_conflict(self, gate) -> bool:
        return any(qb in self._qubit_set for qb in gate.on_qubits)

    def __str__(self) -> str:
        if not self._gates:
            return ""
        parts = []
        for gate in self._gates:
            name = gate.name if hasattr(gate, 'name') else "M"
            qubit_labels = [f"q{qb}" for qb in gate.on_qubits]
            parts.append(f"{name}({','.join(qubit_labels)})")
        return " ".join(parts)

class MomentManager:
    """
    Builds a strictly ordered list of Moments from a circuit.
    Each moment holds gates that act on disjoint qubits and preserve gate order.
    """
    @staticmethod
    def from_circuit(circuit: QuantumCircuit) -> List[Moment]:
        moments: List[Moment] = []

        def add_gate_to_moment(gate):
            if not moments or moments[-1].has_conflict(gate):
                new_moment = Moment()
                new_moment.add_gate(gate)
                moments.append(new_moment)
            else:
                moments[-1].add_gate(gate)

        for gate in circuit.circuit:
            add_gate_to_moment(gate)

        for q in circuit.measure_qubits:
            meas_op = _Measurement(q)
            add_gate_to_moment(meas_op)

        return moments



def test_moment_schedule():
    from gate.bit import QuantumRegister
    from gate.single_gate import X, Y, Z
    from gate.double_gate import CNOT
    # qreg = QuantumRegister(2)
    # q0 = qreg[0]
    # q1 = qreg[1]

    qc = QuantumCircuit(2)

    qc.append(X(0))             # Moment 0
    qc.append(CNOT(0, 1))      # Moment 1
    qc.append(Y(1))             # Moment 2
    qc.append(Z(0))             # Moment 2
    qc.append(X(1))             # Moment 3
    qc.append(CNOT(0, 1))      # Moment 4
    qc.measure([0, 1])         # Moment 5

    moments = MomentManager.from_circuit(qc)

    for i, moment in enumerate(moments):
        print(f"Moment {i}: {moment}")

if __name__ == "__main__":
    test_moment_schedule()