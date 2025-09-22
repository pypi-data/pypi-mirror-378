from gate.instruction import Instruction, Gate
from gate.single_gate import *
from gate.double_gate import *
from gate.multi_gate import *
from utils.visualization import to_text_diag
from typing import Union, List, Optional
from utils.tgq_expection import TgqSimError
from utils import draw_circuit_tools as tools
from matplotlib import pyplot as plt
import numpy as np
from circuit.moment import Moment, MomentManager, _Measurement

"""
QuantumCircuitV3 模块:
1. 保留 QuantumCircuit 基础接口与结构, 使用 int 表示比特索引, 兼容现有门结构.
2. 集成 Moment 特性: 支持自动将门归类进互不冲突的并行执行时刻 (Moment).
   可通过 `moment_mode=True` 启用自动门分组, 也支持显式调用 append_moment(moment) 添加自定义 Moment.
3. 支持 NoiseModel 接口: 可设置全局噪声模型 (set_noise_model(model)),
   在每次 append 门时根据模型自动注入噪声门 (model.noisy_operation).
"""

class CircuitError(TgqSimError):
    """量子电路相关错误异常类"""
    pass

class QuantumCircuit:
    """
    A quantum circuit supporting Moments and NoiseModel.
    Maintains a similar interface to QuantumCircuit, using int indices for qubits.
    """
    def __init__(self, num_qubits: int, moment_mode: bool = False) -> None:
        """
        Initialize the quantum circuit with the given number of qubits.
        :param num_qubits: The number of qubits in the circuit.
        :param moment_mode: If True, automatically organize gates into disjoint moments.
        """
        self._num_qubits: int = num_qubits
        self._circuit: List[Instruction] = []
        self._display_list: List[dict] = []
        self._moments: List[Moment] = []
        self._measure_qubits: List[int] = []
        self._classical_register: List[int] = []
        self._num_sgate: int = 0
        self._num_dgate: int = 0
        self._num_mgate: int = 0
        self._noise_model = None
        self._moment_mode: bool = moment_mode

    # Basic properties
    @property
    def num_qubits(self) -> int:
        return self._num_qubits

    @property
    def circuit(self) -> List[Instruction]:
        return self._circuit

    @property
    def display_list(self) -> List[dict]:
        return self._display_list

    @property
    def measure_qubits(self) -> List[int]:
        return self._measure_qubits

    @property
    def classical_register(self) -> List[int]:
        return self._classical_register

    @property
    def num_sgate(self) -> int:
        return self._num_sgate

    @property
    def num_dgate(self) -> int:
        return self._num_dgate

    @property
    def num_mgate(self) -> int:
        return self._num_mgate

    @property
    def num_gate(self) -> int:
        return len(self._circuit)

    def __len__(self) -> int:
        """Return the number of gates (quantum instructions) in the circuit."""
        return len(self._circuit)

    def __getitem__(self, index: int) -> Instruction:
        """Get the gate/instruction at the specified index."""
        if index >= len(self._circuit) or index < -len(self._circuit):
            raise IndexError("Index out of range.")
        return self._circuit[index]

    def __iter__(self):
        """Iterate over the gates/instructions in the circuit."""
        return iter(self._circuit)

    def __contains__(self, item: Instruction) -> bool:
        """Check if the given gate/instruction is present in the circuit."""
        return item in self._circuit

    def __copy__(self):
        # Shallow copy (QuantumCircuitV3 is mutable, so return self for simplicity)
        return self

    def __deepcopy__(self, memo=None):
        """
        Return a copy of the quantum circuit.
        (Note: This creates a shallow copy of internal lists for efficiency.)
        """
        if len(self) == 0:
            return self
        new_circuit = type(self).__new__(type(self))
        new_circuit.__dict__.update(self.__dict__)
        return new_circuit

    def __str__(self) -> str:
        """Return a string diagram representation of the quantum circuit."""
        return to_text_diag(gates=self._display_list, width=self._num_qubits, classical_bits=self._classical_register)

    def append(self, gate: Instruction) -> 'QuantumCircuit':
        """
        Append a quantum gate/instruction to the circuit.
        If a noise model is set, noise operations from the model will be automatically appended after the gate.
        """
        if not isinstance(gate, Instruction):
            raise TypeError("gate must be an instance of Instruction")
        # Validate qubit indices
        if hasattr(gate, 'on_qubits'):
            for q in gate.on_qubits:
                if q < 0 or q >= self._num_qubits:
                    raise CircuitError(f"Qubit index {q} is out of range.")
        # Determine operations to add (apply noise model if present)
        ops_to_add = [gate]
        if self._noise_model is not None:
            ops_to_add = self._noise_model.noisy_operation(gate)
            if not isinstance(ops_to_add, list):
                ops_to_add = [ops_to_add]
        for op in ops_to_add:
            if not isinstance(op, Instruction):
                raise TypeError("Appended object is not a quantum Instruction.")
            # Append to linear circuit list
            self._circuit.append(op)
            # Mark parent circuit reference if applicable
            if hasattr(op, '_parent_circuit'):
                op._parent_circuit = self
            # Update gate counts
            if hasattr(op, '_num_qubits'):
                if op._num_qubits == 1:
                    self._num_sgate += 1
                elif op._num_qubits == 2:
                    self._num_dgate += 1
                else:
                    self._num_mgate += 1
            # Add to moment structure and display list
            if self._moment_mode:
                # Start a new moment if no moments exist or if op conflicts with last moment
                if not self._moments or self._moments[-1].has_conflict(op):
                    new_moment = Moment([op])
                    self._moments.append(new_moment)
                    # Add a new entry to display list for this moment
                    if isinstance(op, Gate):
                        self._display_list.append(op.display_name.copy())
                    else:
                        disp = {q: (op.name if hasattr(op, 'name') else "?") for q in (op.on_qubits if hasattr(op, 'on_qubits') else [])}
                        self._display_list.append(disp)
                else:
                    # Add to current moment (no qubit overlap with last moment)
                    self._moments[-1].add_gate(op)
                    # Update the last display entry with this gate's symbol(s)
                    if isinstance(op, Gate):
                        for q, sym in op.display_name.items():
                            self._display_list[-1][q] = sym
                    else:
                        for q in (op.on_qubits if hasattr(op, 'on_qubits') else []):
                            self._display_list[-1][q] = (op.name if hasattr(op, 'name') else "?")
            else:
                # Sequential mode: each op is a new moment on its own
                new_moment = Moment([op])
                self._moments.append(new_moment)
                if isinstance(op, Gate):
                    self._display_list.append(op.display_name.copy())
                else:
                    disp = {q: (op.name if hasattr(op, 'name') else "?") for q in (op.on_qubits if hasattr(op, 'on_qubits') else [])}
                    self._display_list.append(disp)
        return self

    def append_moment(self, moment: Moment) -> 'QuantumCircuit':
        """
        Append a pre-defined Moment (a set of gates on disjoint qubits) to the circuit as the next time step.
        """
        if not isinstance(moment, Moment):
            raise TypeError("moment must be an instance of Moment")
        if len(moment) == 0:
            return self
        # Validate qubit indices and gate types in the moment
        for gate in moment:
            if hasattr(gate, 'on_qubits'):
                for q in gate.on_qubits:
                    if q < 0 or q >= self._num_qubits:
                        raise CircuitError(f"Qubit index {q} is out of range.")
            if not isinstance(gate, Instruction):
                raise TypeError("Moment contains a non-Instruction element.")
        # Append each gate in the moment to the circuit list and update counts
        for gate in moment:
            self._circuit.append(gate)
            if hasattr(gate, '_parent_circuit'):
                gate._parent_circuit = self
            if hasattr(gate, '_num_qubits'):
                if gate._num_qubits == 1:
                    self._num_sgate += 1
                elif gate._num_qubits == 2:
                    self._num_dgate += 1
                else:
                    self._num_mgate += 1
        # Add the Moment to the moments list as a new time step (do not merge with previous moment)
        self._moments.append(moment)
        # Combine display info for all gates in the moment into one entry
        combined_entry: dict = {}
        for gate in moment:
            if isinstance(gate, Gate):
                for q, sym in gate.display_name.items():
                    combined_entry[q] = sym
            else:
                name = gate.name if hasattr(gate, 'name') else "Op"
                for q in (gate.on_qubits if hasattr(gate, 'on_qubits') else []):
                    combined_entry[q] = "M" if name == "M" else name
        self._display_list.append(combined_entry)
        return self

    def measure(self, target_qubit: Union[int, List[int]], classical_register: Optional[List[int]] = None) -> None:
        """
        Measure the specified qubit(s), recording results in classical registers.
        If multiple qubits are specified, each is measured (with optional classical register mapping).
        """
        if isinstance(target_qubit, list):
            # Measuring multiple qubits
            self._measure_qubits = target_qubit[:]
            self._classical_register = []
            if self._moment_mode:
                # Group all measurements into one moment (parallel measurement)
                combined = {}
                for i, qbit in enumerate(target_qubit):
                    combined[qbit] = "M"
                    self._classical_register.append(i)
                self._display_list.append(combined)
                meas_moment = Moment()
                for qbit in target_qubit:
                    meas_moment.add_gate(_Measurement(qbit))
                self._moments.append(meas_moment)
            else:
                # Sequential measurement (each qubit measured in a separate moment)
                for i, qbit in enumerate(target_qubit):
                    self._display_list.append({qbit: "M"})
                    self._classical_register.append(i)
                    meas_moment = Moment()
                    meas_moment.add_gate(_Measurement(qbit))
                    self._moments.append(meas_moment)
            # Validate and set classical register if provided
            if classical_register is not None:
                if not isinstance(classical_register, list):
                    raise ValueError("Classical register must be provided as a list.")
                if len(classical_register) != len(set(classical_register)):
                    raise ValueError("Classical register must be unique.")
                length = len(target_qubit)
                if len(classical_register) != length:
                    raise ValueError("Length of classical register must equal number of target qubits.")
                self._classical_register = classical_register
        else:
            # Measuring a single qubit
            qbit = target_qubit
            self._measure_qubits = [qbit]
            if self._moment_mode:
                self._display_list.append({qbit: "M"})
                self._classical_register = [0]
                meas_moment = Moment()
                meas_moment.add_gate(_Measurement(qbit))
                self._moments.append(meas_moment)
            else:
                self._display_list.append({qbit: "M"})
                self._classical_register = [0]
                meas_moment = Moment()
                meas_moment.add_gate(_Measurement(qbit))
                self._moments.append(meas_moment)
            if classical_register is not None:
                if not isinstance(classical_register, list):
                    raise ValueError("Classical register must be provided as a list.")
                if len(classical_register) != len(set(classical_register)):
                    raise ValueError("Classical register must be unique.")
                if len(classical_register) != 1:
                    raise ValueError("Length of classical register must equal number of target qubits.")
                self._classical_register = classical_register

    def set_noise_model(self, noise_model) -> 'QuantumCircuit':
        """
        Set a global noise model for this circuit.
        The noise_model should have a method noisy_operation(gate) -> List[Instruction].
        """
        if noise_model is not None and not hasattr(noise_model, "noisy_operation"):
            raise TypeError("Noise model must have a noisy_operation method.")
        self._noise_model = noise_model
        return self

    @property
    def moments(self) -> List[Moment]:
        """Return the list of Moment objects representing the circuit (including measurements)."""
        return self._moments

    def get_moments(self) -> List[Moment]:
        """Compute the moment structure from the current circuit (gates grouped into disjoint moments)."""
        return MomentManager.from_circuit(self)

    def show_quantum_circuit(self, plot_labels: bool = True, **kwargs) -> None:
        """Display a diagram of the quantum circuit using Matplotlib."""
        labels = []
        inits = {}
        for i in range(self._num_qubits):
            labels.append(f"q_{i}")
            inits[f"q_{i}"] = i
        plot_params = dict(scale=1.0, fontsize=14.5, linewidth=2.0,
                           control_radius=0.05, not_radius=0.15,
                           swap_delta=0.08, label_buffer=0.8,
                           rectangle_delta=0.3, box_pad=0.2)
        plot_params.update(kwargs)
        scale = plot_params['scale']
        if not labels:
            labels = []
            for _, gate in tools.enumerate_gates(self.circuit_diag, schedule=True):
                for label in gate[1:]:
                    if label not in labels:
                        labels.append(label)
        number_qubits = len(labels)
        nt = 1.5 * len(self.display_list)
        wire_grid = np.arange(0.0, number_qubits * scale, scale, dtype=float)
        gate_grid = np.arange(0.0, scale * nt, scale, dtype=float)
        gate_grid_index = [0.0 for _ in range(number_qubits)]
        fig, ax = tools.setup_figure(number_qubits, nt, gate_grid, wire_grid, plot_params)
        if plot_labels:
            tools.draw_labels(ax, number_qubits, inits, gate_grid, wire_grid, plot_params, 'k')
        gate_grid_index = tools.draw_gates(ax, self.display_list, gate_grid_index, wire_grid, plot_params, number_qubits)
        tools.draw_wires(ax, number_qubits, [0.0, max(gate_grid_index)], wire_grid, plot_params, 'k')
        plt.show()

    def x(self, target_qubit: int):
        """
        Apply X gate to the target qubit.
        """
        x_gate = X(target_qubit)
        return self.append(x_gate)

    def y(self, target_qubit: int):
        """
        Apply Y gate to the target qubit.
        """
        y_gate = Y(target_qubit)
        return self.append(y_gate)

    def z(self, target_qubit: int):
        """
        Apply Z gate to the target qubit.
        """
        z_gate = Z(target_qubit)
        return self.append(z_gate)

    def sx(self, target_qubit: int):
        """
        Apply SX gate to the target qubit.
        """
        sx_gate = SQRT_X(target_qubit)
        return self.append(sx_gate)

    def sxdg(self, target_qubit: int):
        """
        Apply SX† gate to the target qubit.
        """
        sxdg_gate = SQRT_X_DAG(target_qubit)
        return self.append(sxdg_gate)

    def h(self, target_qubit: int):
        """
        Apply H gate to the target qubit.
        """
        h_gate = H(target_qubit)
        return self.append(h_gate)

    def rx(self, target_qubit: int, theta: float):
        """
        Apply RX gate to the target qubit.
        """
        rx_gate = RX(target_qubit, theta)
        return self.append(rx_gate)

    def ry(self, target_qubit: int, theta: float):
        """
        Apply RY gate to the target qubit.
        """
        ry_gate = RY(target_qubit, theta)
        return self.append(ry_gate)

    def rz(self, target_qubit: int, theta: float):
        """
        Apply RZ gate to the target qubit.
        """
        rz_gate = RZ(target_qubit, theta)
        return self.append(rz_gate)

    def t(self, target_qubit: int):
        """
        Apply T gate to the target qubit.
        """
        t_gate = T(target_qubit)
        return self.append(t_gate)

    def s(self, target_qubit: int):
        """
        Apply S gate to the target qubit.
        """
        s_gate = S(target_qubit)
        return self.append(s_gate)

    def s_dag(self, target_qubit: int):
        """
        Apply S† gate to the target qubit.
        """
        s_dag_gate = S_DAG(target_qubit)
        return self.append(s_dag_gate)

    def t_dag(self, target_qubit: int):
        """
        Apply T† gate to the target qubit.
        """
        t_dag_gate = T_DAG(target_qubit)
        return self.append(t_dag_gate)

    def sqrt_x(self, target_qubit: int):
        """
        Apply SQRT_X gate to the target qubit.
        """
        sqrt_x_gate = SQRT_X(target_qubit)
        return self.append(sqrt_x_gate)

    def sqrt_x_dag(self, target_qubit: int):
        """
        Apply SQRT_X† gate to the target qubit.
        """
        sqrt_x_dag_gate = SQRT_X_DAG(target_qubit)
        return self.append(sqrt_x_dag_gate)

    def u(self, target_qubit: int, mat: np.ndarray):
        """
        Apply U gate to the target qubit.
        """
        u_gate = U(target_qubit, matrix=mat)
        return self.append(u_gate)

    def cnot(self, control_qubit: int, target_qubit: int):
        """
        Apply CNOT gate with control qubit and target qubit.
        """
        cnot_gate = CNOT(control_qubit, target_qubit)
        return self.append(cnot_gate)

    def cz(self, control_qubit: int, target_qubit: int):
        """
        Apply CZ gate with control qubit and target qubit.
        """
        cz_gate = CZ(control_qubit, target_qubit)
        return self.append(cz_gate)

    def swap(self, qubit1: int, qubit2: int):
        """
        Apply SWAP gate with two qubits.
        """
        swap_gate = SWAP(qubit1, qubit2)
        return self.append(swap_gate)

    def cp(self, control_qubit: int, target_qubit: int, theta: float):
        """
        Apply CP gate with control qubit and target qubit.
        """
        cp_gate = CP(control_qubit, target_qubit, theta)
        return self.append(cp_gate)

    def iswap(self, qubit1: int, qubit2: int):
        """
        Apply ISWAP gate with control qubit and target qubit.
        """
        iswap_gate = ISWAP(qubit1, qubit2)
        return self.append(iswap_gate)

    def syc(self, qubit1: int, qubit2: int):
        """
        Apply SYC gate with control qubit and target qubit.
        """
        syc_gate = SYC(qubit1, qubit2)
        return self.append(syc_gate)

    def rxx(self, qubit1: int, qubit2: int, theta: float):
        """
        Apply RXX gate with control qubit and target qubit.
        """
        rxx_gate = RXX(qubit1, qubit2, theta)
        return self.append(rxx_gate)

    def ryy(self, qubit1: int, qubit2: int, theta: float):
        """
        Apply RYY gate with control qubit and target qubit.
        """
        ryy_gate = RYY(qubit1, qubit2, theta)
        return self.append(ryy_gate)

    def rzz(self, qubit1: int, qubit2: int, theta: float):
        """
        Apply RZZ gate with control qubit and target qubit.
        """
        rzz_gate = RZZ(qubit1, qubit2, theta)
        return self.append(rzz_gate)

    def du(self, qubit1: int, qubit2: int, mat: np.ndarray):
        """
        Apply U gate to the target qubit.
        """
        du_gate = DU(qubit1, qubit2, mat)
        return self.append(du_gate)

    def ccx(self, control_qubit1: int, control_qubit2: int, target_qubit: int):
        """
        Apply CCX gate with two control qubits and one target qubit.
        """
        ccx_gate = CCX(control_qubit1, control_qubit2, target_qubit)
        return self.append(ccx_gate)

    def cswap(self, control_qubit: int, target_qubit1: int, target_qubit2: int):
        """
        Apply CSWAP gate with control qubit and two target qubits.
        """
        cswap_gate = CSWAP(control_qubit, target_qubit1, target_qubit2)
        return self.append(cswap_gate)
