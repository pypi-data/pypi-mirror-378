from typing import Union, List, Optional
from gate.bit import Bit, QuantumRegister
from gate.instruction import Instruction
from gate.single_gate import *
from gate.double_gate import *
from gate.multi_gate import *
from utils.visualization import to_text_diag
from utils.tgq_expection import TgqSimError
from utils import draw_circuit_tools as tools
from matplotlib import pyplot as plt
import numpy as np
from circuit.moment import Moment

class CircuitError(TgqSimError):
    pass

class QuantumCircuit:
    """
    QuantumCircuit represents a quantum circuit as an ordered sequence of gates (instructions)
    and also as layers (moments) of parallel gates.
    """
    def __init__(self, num_qubits: int = 0
                 # , qreg: Optional[QuantumRegister] = None, bits: Optional[List[Bit]] = None
                 ):
        """
        Initialize the QuantumCircuit.
        :param num_qubits: Number of quantum bits to initialize (ignored if bits or qreg are provided).
        :param qreg: Optional QuantumRegister to initialize the circuit with.
        :param bits: Optional list of Bit (or int) objects to initialize the circuit with.
        """
        # Initialize quantum bits
        # if qreg is not None and isinstance(qreg, list) and bits is None:
        #     # If qreg is provided as a list of bits (compatibility for positional usage)
        #     bits = qreg
        #     qreg = None
        # if bits is not None:
        #     self._bits = bits
        #     self._num_qubits = len(bits)
        #     self._qreg = None
        # elif qreg is not None:
        #     # Use provided QuantumRegister and its qubits
        #     self._qreg = qreg
        #     try:
        #         # If qreg is iterable
        #         self._bits = [qb for qb in qreg]
        #     except TypeError:
        #         # Fallback: treat qreg as single object (not expected)
        #         self._bits = []
        #     self._num_qubits = len(self._bits)
        # else:
        #     # Create a new QuantumRegister with given number of qubits
        #     self._qreg = QuantumRegister(num_qubits) if num_qubits > 0 else QuantumRegister(0)
        #     try:
        #         self._bits = [qb for qb in self._qreg]
        #     except TypeError:
        #         # In case QuantumRegister is not iterable, create Bit list
        #         self._bits = [Bit(i) for i in range(num_qubits)]
        #     self._num_qubits = len(self._bits)
        # Initialize lists for circuit, moments, display, measurement and counters
        self._circuit: List[Instruction] = []
        self._moments: List[Moment] = []
        self._display_list: List[dict] = []
        self._measure_qubits: List[int] = []
        self._classical_register: List[int] = []
        self._num_sgate: int = 0
        self._num_dgate: int = 0
        self._num_mgate: int = 0
        self.is_decomposed = False
        self._noisy_circuit = None

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

    def __str__(self) -> str:
        """
        Return a string representation of the quantum circuit.
        """
        return to_text_diag(gates=self._display_list, width=self._num_qubits, classical_bits=self._classical_register)

    def __getitem__(self, index: int):
        """
        Get the gate at the specified index.
        """
        if index >= len(self):
            raise IndexError("Index out of range.")
        if index < 0:
            index += len(self)
        return self._circuit[index]

    def __len__(self) -> int:
        """
        Return the length of the quantum circuit.
        """
        return len(self._circuit)

    def __contains__(self, item: Instruction) -> bool:
        """
        Check if the item is in the quantum circuit.
        """
        return item in self._circuit

    def __iter__(self):
        """
        Return an iterator for the quantum circuit.
        """
        for gate in self._circuit:
            yield gate

    def __copy__(self):
        return self

    def __deepcopy__(self, memo=None):
        """
        Return a deep copy of the quantum circuit.
        """
        if len(self) == 0:
            return self
        new_circuit = type(self).__new__(type(self))
        new_circuit.__dict__.update(self.__dict__)
        return new_circuit

    def _update_gate_display(self, gate):
        """
        Update display for a specific gate.
        """
        if gate in self._circuit:
            index = self._circuit.index(gate)
            self._display_list[index] = gate.display_name

    def index(self, item: Instruction) -> int:
        """
        Return the index of the item in the quantum circuit.
        """
        if item not in self._circuit:
            raise ValueError("Item not found in the circuit.")
        return self._circuit.index(item)

    def append(self, gate: Instruction):
        """
        Append a gate to the quantum circuit.
        """
        if not isinstance(gate, Instruction):
            raise TypeError("gate must be an instance of Instruction")
        # Attempt to place gate in an existing moment without conflict
        new_bits = set()
        if hasattr(gate, 'bits'):
            new_bits = set(gate.bits)
        elif hasattr(gate, '_bits'):
            new_bits = set(gate._bits)
        else:
            for attr in ('_bit', '_bit0', '_bit1', '_bit2', '_control', '_target', '_control_bit', '_target_bit'):
                if hasattr(gate, attr):
                    val = getattr(gate, attr)
                    if isinstance(val, list):
                        new_bits.update(val)
                    else:
                        new_bits.add(val)
        added_to_moment = False
        for moment in self._moments:
            # Collect all bits used in this moment
            moment_bits = set()
            for g in moment:
                if hasattr(g, 'bits'):
                    moment_bits |= set(g.bits)
                elif hasattr(g, '_bits'):
                    moment_bits |= set(g._bits)
                else:
                    for attr in ('_bit', '_bit0', '_bit1', '_bit2', '_control', '_target', '_control_bit', '_target_bit'):
                        if hasattr(g, attr):
                            val = getattr(g, attr)
                            if isinstance(val, list):
                                moment_bits.update(val)
                            else:
                                moment_bits.add(val)
            if new_bits.isdisjoint(moment_bits):
                # No conflict, add to this moment
                try:
                    moment.add_gate(gate)
                except AttributeError:
                    # If moment has no add_gate (should not happen if Moment from moment.py)
                    moment._gates.append(gate)
                added_to_moment = True
                break
        if not added_to_moment:
            # Create a new moment for this gate
            new_moment = Moment()
            try:
                new_moment.add_gate(gate)
            except AttributeError:
                new_moment._gates.append(gate)
            self._moments.append(new_moment)
        # Append gate to sequential list and update display
        self._circuit.append(gate)
        self._display_list.append(gate.display_name)
        # Set parent circuit reference
        if hasattr(gate, '_parent_circuit'):
            gate._parent_circuit = self
        # Update gate counts
        if hasattr(gate, 'num_qubits'):
            nq = gate.num_qubits
        else:
            # Fallback: infer number of qubits from involved bits
            nq = len(new_bits) if new_bits else 0
        if nq == 1:
            self._num_sgate += 1
        elif nq == 2:
            self._num_dgate += 1
        else:
            self._num_mgate += 1
        return self

    def append_moment(self, moment: Moment):
        """
        Append a Moment (layer of gates) to the quantum circuit.
        """
        # Insert the moment as a new parallel layer at the end
        self._moments.append(moment)
        # Append all gates in the moment to the sequential list and update display and counts
        for gate in moment:
            self._circuit.append(gate)
            self._display_list.append(gate.display_name)
            if hasattr(gate, '_parent_circuit'):
                gate._parent_circuit = self
            # Update counters
            nq = gate.num_qubits if hasattr(gate, 'num_qubits') else (len(gate.bits) if hasattr(gate, 'bits') else 0)
            if nq == 1:
                self._num_sgate += 1
            elif nq == 2:
                self._num_dgate += 1
            else:
                self._num_mgate += 1
        return self

    def show_moments(self):
        """
        Output the structure of each moment (layer) in the circuit.
        Each moment is listed with the gates it contains.
        """
        for idx, moment in enumerate(self._moments):
            gate_strs = []
            for gate in moment:
                # Determine gate name
                if hasattr(gate, 'name'):
                    gate_name = gate.name
                else:
                    gate_name = gate.__class__.__name__
                # Determine qubits/bits the gate acts on
                bit_labels = []
                if hasattr(gate, 'bits'):
                    bits_list = list(gate.bits)
                elif hasattr(gate, '_bits'):
                    bits_list = list(gate._bits)
                else:
                    bits_list = []
                    for attr in ('_bit', '_bit0', '_bit1', '_bit2', '_control', '_target', '_control_bit', '_target_bit'):
                        if hasattr(gate, attr):
                            val = getattr(gate, attr)
                            if isinstance(val, list):
                                bits_list.extend(val)
                            else:
                                bits_list.append(val)
                for bit in bits_list:
                    if hasattr(bit, 'name'):
                        bit_label = bit.name
                    elif hasattr(bit, 'index'):
                        bit_label = f"q{bit.index}"
                    else:
                        bit_label = str(bit)
                    bit_labels.append(bit_label)
                bits_str = ", ".join(bit_labels)
                gate_str = f"{gate_name}({bits_str})" if bits_str else f"{gate_name}"
                gate_strs.append(gate_str)
            print(f"Moment {idx}: " + ", ".join(gate_strs))

    @property
    def circuit_diag(self):
        # Alias for display list used in visualization
        return self._display_list

    def show_quantum_circuit(self, plot_labels=True, **kwargs):
        """
        Use Matplotlib to plot a quantum circuit.
        kwargs    Can override plot_parameters
        """
        labels = []
        inits = {}
        for i in range(self.num_qubits):
            labels.append(f"q_{i}")
            inits[f"q_{i}"] = i
        plot_params = dict(scale=1.0, fontsize=14.5, linewidth=2.0,
                           control_radius=0.05, not_radius=0.15,
                           swap_delta=0.08, label_buffer=0.8,
                           rectangle_delta=0.3, box_pad=0.2)
        plot_params.update(kwargs)
        scale = plot_params['scale']
        # Create labels from gates. This will become slow if there are a lot
        #  of gates, in which case move to an ordered dictionary
        if not labels:
            labels = []
            for i, gate in tools.enumerate_gates(self.circuit_diag, schedule=True):
                for label in gate[1:]:
                    if label not in labels:
                        labels.append(label)
        number_qubits = len(labels)
        nt = 1.5 * len(self.display_list)
        # 存储横坐标
        wire_grid = np.arange(0.0, number_qubits * scale, scale, dtype=float)
        # 存储纵坐标
        gate_grid = np.arange(0.0, scale * nt, scale, dtype=float)
        gate_grid_index = [0.0 for _ in range(number_qubits)]
        # print(gate_grid_index)
        fig, ax = tools.setup_figure(number_qubits, nt, gate_grid, wire_grid, plot_params)
        # measured = tools.measured_wires(self.circuit_diag, labels, schedule=True)
        if plot_labels:
            tools.draw_labels(ax, number_qubits, inits, gate_grid, wire_grid, plot_params, 'k')
        gate_grid_index = tools.draw_gates(ax, self.display_list, gate_grid_index, wire_grid, plot_params, number_qubits)
        tools.draw_wires(ax, number_qubits, [0.0, max(gate_grid_index)], wire_grid, plot_params, 'k')
        # fig.canvas.mpl_connect('resize_event', tools.update_fontsize)
        plt.show()

    def extend(self, cir: 'QuantumCircuit'):
        """
        Extend the quantum circuit with another quantum circuit.
        """
        if not isinstance(cir, QuantumCircuit):
            raise TypeError("cir must be an instance of QuantumCircuit")
        # If needed, expand the number of qubits to accommodate the other circuit
        if self._num_qubits < cir.num_qubits:
            if self._qreg is not None:
                # Resize existing quantum register
                try:
                    self._qreg.resize(cir.num_qubits)
                except AttributeError:
                    # If no resize method, add qubits to qreg
                    self._qreg += (cir.num_qubits - self._num_qubits)
                # Update internal bits list
                self._bits = [qb for qb in self._qreg]
            else:
                # Add new Bit objects to internal list
                for i in range(cir.num_qubits - self._num_qubits):
                    new_index = len(self._bits)
                    self._bits.append(Bit(new_index))
            self._num_qubits = cir.num_qubits
        # Append all gates from other circuit sequentially
        self._circuit.extend(cir._circuit)
        # Merge display_list, keeping measurements at the end
        left_gate = []
        left_measure = []
        for gate_display in self._display_list:
            if 'M' in gate_display.values():
                left_measure.append(gate_display)
            else:
                left_gate.append(gate_display)
        right_gate = []
        for gate_display in cir._display_list:
            if 'M' not in gate_display.values():
                right_gate.append(gate_display)
        # Combine displays: existing gates, then new gates, then existing measurements
        self._display_list = left_gate + right_gate + left_measure
        # Update gate counts
        self._num_sgate += cir.num_sgate
        self._num_dgate += cir.num_dgate
        self._num_mgate += cir.num_mgate
        # Append moments for the new gates (each gate in its own new moment to preserve sequential order)
        for gate in cir._circuit:
            new_moment = Moment()
            try:
                new_moment.add_gate(gate)
            except AttributeError:
                new_moment._gates.append(gate)
            self._moments.append(new_moment)
        return self

    def measure(self, target_qubit: Union[int, List[int]], classical_register: Optional[List[int]] = None):
        if isinstance(target_qubit, list):
            # Measure multiple qubits
            self._measure_qubits = target_qubit
            for i, qbit in enumerate(target_qubit):
                # Append measurement to display list for each qubit
                idx = qbit.index() if callable(getattr(qbit, "index", None)) else qbit.index
                self._display_list.append({idx: "M"})
                self._classical_register.append(i)
        else:
            # Measure a single qubit
            self._measure_qubits = [target_qubit]
            idx = target_qubit.index() if callable(getattr(target_qubit, "index", None)) else target_qubit.index
            self._display_list.append({idx: "M"})
            self._classical_register = [0]
        # If a specific classical register mapping is provided
        if classical_register is not None:
            if isinstance(classical_register, list):
                if len(classical_register) != len(set(classical_register)):
                    raise ValueError("Classical register must be unique.")
            length = len(target_qubit) if isinstance(target_qubit, list) else 1
            if len(classical_register) != length:
                raise ValueError("Length of classical register must be equal to the number of target qubits.")
            self._classical_register = classical_register

    def add_qubits(self, number_qubits: int):
        # Increase the number of qubits in the circuit
        if number_qubits <= 0:
            return
        if self._qreg is not None:
            # If using a QuantumRegister, increase its size
            try:
                self._qreg.resize(self._num_qubits + number_qubits)
            except AttributeError:
                # If no resize, use addition
                self._qreg += number_qubits
            # Update internal bits list to include new qubits
            self._bits = [qb for qb in self._qreg]
        else:
            # Create and append new Bit objects
            for i in range(number_qubits):
                new_index = len(self._bits)
                self._bits.append(Bit(new_index))
        # Update the count of qubits
        self._num_qubits += number_qubits

    def filter_two_qubit_gates(self) -> 'QuantumCircuit':
        """
        Filter out two-qubit gates from the circuit.
        """
        # Create a new QuantumCircuit with the same qubits
        if self._qreg is not None:
            new_circuit = QuantumCircuit(self._num_qubits, self._qreg)
        else:
            new_bits = [qb for qb in self._bits]
            new_circuit = QuantumCircuit(self._num_qubits, bits=new_bits)
        for gate in self._circuit:
            if hasattr(gate, 'num_qubits') and gate.num_qubits == 2:
                new_circuit.append(gate)
        return new_circuit

    def reset_qc(self, from_circuit: List[Instruction]):
        # Reset the circuit and load gates from an existing list of gates
        self._circuit = []
        self._display_list = []
        self._moments = []
        # Reset counters
        self._num_sgate = 0
        self._num_dgate = 0
        self._num_mgate = 0
        # Append all gates from the provided list
        for gate in from_circuit:
            self.append(gate)

    def compose(self, other: 'QuantumCircuit', qubits: List[int]) -> 'QuantumCircuit':
        for gate in other:
            if hasattr(gate, 'num_qubits') and gate.num_qubits != len(qubits):
                raise ValueError("Number of qubits in the other circuit must match the number of qubits provided.")
            # Ensure target qubits indices are within range
            max_qubit_index = max(q.index() if callable(getattr(q, "index", None)) else q.index for q in (gate.on_qubits if hasattr(gate, 'on_qubits') else []))
            if max_qubit_index is not None and max_qubit_index >= self._num_qubits:
                raise ValueError("qubit index out of range.")
            # Map the gate's qubits to the provided qubits
            if hasattr(gate, 'on_qubits'):
                gate.on_qubits = qubits
            elif hasattr(gate, '_bits'):
                gate._bits = qubits
            else:
                # If gate uses different attributes, map each one
                for attr in ('_bit', '_bit0', '_bit1', '_bit2', '_control', '_target', '_control_bit', '_target_bit'):
                    if hasattr(gate, attr):
                        setattr(gate, attr, qubits[0] if len(qubits) == 1 else qubits[:len(qubits)])
                        break
            # Append the modified gate to this circuit
            self.append(gate)
        return self

    def with_noise(self, noise_model, save=False):
        """Return a new circuit with noise gates injected using the provided noise model."""
        if noise_model is None:
            return self

        from gate.instruction import Instruction  # 防止循环引用

        noisy_circuit = QuantumCircuit(self.num_qubits, bits=self._bits.copy())

        for gate in self._circuit:
            # 原始门及其所有注入的噪声门都作为 Instruction
            noisy_gates = noise_model.noisy_operation(gate)
            for g in noisy_gates:
                if not isinstance(g, Instruction):
                    raise TypeError("Injected gate must be of type Instruction.")
                noisy_circuit.append(g)
        if save:
            self._noisy_circuit = noisy_circuit
        return noisy_circuit

    @property
    def noisy_circuit(self):
        return getattr(self, '_noisy_circuit', None)

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
        Apply SX gate to the target qubit.
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
        Apply S gate to the target qubit.
        """
        s_dag_gate = S_DAG(target_qubit)
        return self.append(s_dag_gate)

    def t_dag(self, target_qubit: int):
        """
        Apply T gate to the target qubit.
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
        Apply SQRT_X gate to the target qubit.
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
