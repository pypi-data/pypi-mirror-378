from tgqSim.gate.instruction import Instruction
from tgqSim.gate.bit import QuantumRegister
from tgqSim.gate.single_gate import *
from tgqSim.gate.double_gate import *
from tgqSim.gate.multi_gate import *
from tgqSim.utils.visualization import to_text_diag
from tgqSim.utils.tgq_expection import TgqSimError
from tgqSim.utils import draw_circuit_tools as tools

from typing import Union, List, Optional
from matplotlib import pyplot as plt
from typing import List, Union, Callable, Dict

class CircuitError(TgqSimError):
    pass

class QuantumCircuit:
    # __slots__ = ['_num_qubits', '_circuit', "_display_list", "_qreg", "_measure_qubits", '_classical_register']
    def __init__(self, num_qubits: int) -> None:
        self._num_qubits:int = num_qubits
        self._circuit:List[Gate] = []
        self._display_list:List[dict] = []
        # self._qreg = qreg
        self._measure_qubits:List[int] = []
        self._classical_register:List[int] = []
        self._num_sgate:int = 0  # number of single gates
        self._num_dgate:int = 0  # number of double gates
        self._num_mgate:int = 0  # number of multi gates
        self.is_decomposed = False  # 是否已经被分解过，默认未分解
    
    @property
    def num_qubits(self):
        return self._num_qubits
    
    @property
    def circuit(self):
        return self._circuit

    @property
    def display_list(self):
        return self._display_list
    
    @property
    def measure_qubits(self):
        return self._measure_qubits
    
    @property
    def classical_register(self):
        return self._classical_register
    
    @property
    def num_sgate(self):
        return self._num_sgate
    
    @property
    def num_dgate(self):
        return self._num_dgate
    @property
    def num_mgate(self):
        return self._num_mgate
    
    @property
    def num_gate(self):
        return len(self._circuit)

    def __str__(self):
        """
        Return a string representation of the quantum circuit.
        """
        # display_list = []
        # for gate in self._circuit:
        #     display_list.append(gate.display_name)
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
    
    def __len__(self):
        """
        Return the length of the quantum circuit.
        """
        return len(self._circuit)
    
    def __contains__(self, item: Gate):  
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
        """Update display for a specific gate"""
        if gate in self._circuit:
            index = self._circuit.index(gate)
            self._display_list[index] = gate.display_name
        
    def index(self, item: Gate) -> int:
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
        # for qbit in gate.on_qubits:
        #     if qbit not in self._qreg:
        #         raise ValueError(f"int {qbit} is not part of the quantum register.")
        self._circuit.append(gate)
        self._display_list.append(gate.display_name)
        gate._parent_circuit = self
        
        # print(f"length of gate.ctrl_qubits: {len(gate.ctrl_qubits)}")
        
        if gate.num_qubits == 1:
            self._num_sgate += 1
        elif gate.num_qubits == 2:
            self._num_dgate += 1
        else:
            self._num_mgate += 1
        
        return self
    
    def extend(self, cir: 'QuantumCircuit') -> 'QuantumCircuit':
        """
        Extend the quantum circuit with another quantum circuit.
        """
        # todo: 里面存在比特位不同的问题
        if not isinstance(cir, QuantumCircuit):
            raise TypeError("gate must be an instance of QuantumCircuit")
        if self._num_qubits < cir._num_qubits:
            self._num_qubits = cir._num_qubits
            # self._qreg.resize(cir._num_qubits)
        self._circuit.extend(cir._circuit)
        # self._measure_qubits = list(set(self._measure_qubits).union(set(cir._measure_qubits)))
        # for c in cir._classical_register:
        #     if c not in self._classical_register:
        #         self._classical_register.append(c)
        left_gate, left_measure = [], []
        right_gate = []
        for gate_display in self._display_list:
            if 'M' in gate_display.values():
                left_measure.append(gate_display)
            else:
                left_gate.append(gate_display)
        for gate_display in cir._display_list:
            if 'M' not in gate_display.values():
                right_gate.append(gate_display)
        # print(f"left_measure: {left_measure}, right_measure: {right_measure}")
        left_gate.extend(right_gate)
        left_gate.extend(left_measure)
        self._display_list = left_gate
        
        self._num_sgate += cir.num_sgate
        self._num_dgate += cir.num_dgate
        self._num_mgate += cir.num_mgate
        
        return self
    
    def measure(self, target_qubit: Union[int, List[int]], classical_register: Optional[List[int]] = None):
        if isinstance(target_qubit, list):
            self._measure_qubits = target_qubit
            for i, qbit in enumerate(target_qubit):
                self._display_list.append({qbit: "M"})
                self._classical_register.append(i)
        else:
            self._measure_qubits = [target_qubit]
            self._display_list.append({target_qubit: "M"})
            self._classical_register = [0]
        
        if classical_register is not None:
            if isinstance(classical_register, list):
                if len(classical_register) != len(set(classical_register)):
                    raise ValueError("Classical register must be unique.")
            length = len(target_qubit) if isinstance(target_qubit, list) else 1
            if len(classical_register) != length:
                raise ValueError("Length of classical register must be equal to the number of target qubits.")
            self._classical_register = classical_register
    
    def add_qubits(self, number_qubits: int):
        self._num_qubits += number_qubits
        # self._qreg += number_qubits
        
    def filter_two_qubit_gates(self) -> 'QuantumCircuit':    
        """
        Filter out two-qubit gates from the circuit.
        """
        # new_circuit = QuantumCircuit(self._num_qubits, self._qreg)
        new_circuit = QuantumCircuit(self._num_qubits)
        for gate in self._circuit:
            if gate.num_qubits == 2:
                new_circuit.append(gate)
        return new_circuit
    
    def reset_qc(self, from_circuit: List[Gate]):  # 是否应该更改循环中append方法？self.append(gate)
        self._circuit = []
        self._display_list = []
        self._num_sgate = 0  # number of single gates
        self._num_dgate = 0  # number of double gates
        self._num_mgate = 0  # number of multi gates
        
        for gate in from_circuit:
            self.append(gate)
            # self._display_list.append(gate.display_name)
            # self._circuit.append(gate)
    
    # def compose(self, other: 'QuantumCircuit', qubits: List[int]) -> 'QuantumCircuit':
    #     for gate in other:
    #         if gate.num_qubits != len(qubits):
    #             raise ValueError("Number of qubits in the other circuit must match the number of qubits provided.")
    #         max_qubit_index = max(gate.on_qubits).index()
    #         if max_qubit_index >= self._num_qubits:
    #             raise ValueError("Qubit index out of range.")
    #         gate.on_qubits = qubits
    #         self.append(gate)
    
    def compose(self, other: 'QuantumCircuit', qubits: List[int]) -> 'QuantumCircuit':
        for gate in other:
            # if gate.num_qubits != len(qubits): 应该对每个门进行判断和修改比特情况
            #     raise ValueError("Number of qubits in the other circuit must match the number of qubits provided.")
            max_qubit_index = max(gate.on_qubits)
            if max_qubit_index >= self._num_qubits:
                raise ValueError("Qubit index out of range.")
            if isinstance(gate, MCUGate):
                new_control_qubits = [qubits[i] for i in gate.control_qubits]
                new_target_qubits = [qubits[i] for i in gate.target_qubits]
                gate.reset_qubits(new_control_qubits, new_target_qubits)
            else:
                new_qubits = [qubits[i] for i in gate.on_qubits]
                gate.reset_qubits(new_qubits)
            self.append(gate)
    
    def show_quantum_circuit(self, plot_labels=True, **kwargs):
        """Use Matplotlib to plot a quantum circuit.
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
        # print(f"nq={number_qubits}, nt={nt}")
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
        Apply Double U gate to the target qubit.
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

    def mu(self, on_qubits: List[int], mat: np.ndarray):
        """
        Apply Double U gate to the target qubit.
        """
        mu_gate = MU(on_qubits, mat)
        return self.append(mu_gate)
    
    def mcu(self, target: Union[str, np.ndarray, Callable[..., np.ndarray]],
                  control_qubits: Union[int, List[int]],
                  target_qubits: Union[int, List[int]],
                  display_name: Union[Dict, None] = None, 
                  *args, **kwargs):
        """
        Apply Double U gate to the target qubit.
        """
        mcu_gate = MCUGate(target, control_qubits, target_qubits, display_name, *args, **kwargs)
        return self.append(mcu_gate)