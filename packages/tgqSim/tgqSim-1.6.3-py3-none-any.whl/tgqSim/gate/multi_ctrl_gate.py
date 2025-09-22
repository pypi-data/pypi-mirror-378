import numpy as np
from gate.instruction import MCUGate
from gate.gate_matrix import name_matrix_mapping, GateType

class CX(MCUGate):
    """
    CNOT gate (also known as Controlled-NOT gate).
    It flips the state of the target qubit if the control qubit is in state |1>.
    """

    def __init__(self, control_qubit: int, target_qubit: int) -> None:
        # if control_qubit < target_qubit:
        #     super().__init__(target="x", control_qubits=control_qubit, target_qubits=target_qubit,
        #                      theta=None, params=name_matrix_mapping[GateType.CNOT_CS])
        # else:
        #     super().__init__(target="x", control_qubits=control_qubit, target_qubits=target_qubit,
        #                      theta=None, params=name_matrix_mapping[GateType.CNOT_CB])
        super().__init__(
            target="x",
            control_qubits=control_qubit,
            target_qubits=target_qubit
        )
        self._name = "CX"
        # self._target_qubit = [target_qubit]
        # self._ctrl_qubits = [control_qubit]
        self._data = (self._name, self._on_qubits, self._params)
        self._display_name = {control_qubit: "@", target_qubit: "X"}

    def inverse(self) -> MCUGate:
        return CX(self.control_qubits[0], self.target_qubits[0])


CNOT = CX  # Alias for CX gate


class CZ(MCUGate):
    """
    CZ gate (also known as Controlled-Z gate).
    It adds a phase of π to the target qubit if the control qubit is in state |1>.
    """

    def __init__(self, control_qubit: int, target_qubit: int) -> None:
        super().__init__(target="z", control_qubits=control_qubit, target_qubits=target_qubit)
        self._name = "CZ"
        # self._target_qubit = [target_qubit]
        # self._ctrl_qubits = [control_qubit]
        self._data = (self._name, self._on_qubits, self._params)
        self._display_name = {control_qubit: "@", target_qubit: "Z"}

    def inverse(self) -> MCUGate:
        return CZ(self.control_qubits[0], self.target_qubits[0])


class CP(MCUGate):
    """
    CP gate (also known as Controlled-Phase gate).
    It adds a phase to the target qubit if the control qubit is in state |1>.
    """

    def __init__(self, control_qubit: int, target_qubit: int, theta: float) -> None:
        super().__init__(target='rp', control_qubits=control_qubit, target_qubits=target_qubit,
                         theta=theta)
        self._name = "CP"
        self._theta = theta
        self._data = (self._name, self._on_qubits, self._params)
        self._display_name = {control_qubit: "@", target_qubit: f"P({round(theta, 2)})"}

    @property
    def theta(self) -> float:
        return self._theta

    def inverse(self) -> MCUGate:
        return CP(self.control_qubits[0], self.target_qubits[0], -self._theta)


class CCX(MCUGate):
    """
    CCX gate (also known as Toffoli gate).
    It flips the state of the target qubit if both control qubits are in state |1>.
    """
    def __init__(self, ctrl_qubit1: int, ctrl_qubit2: int, target_qubit: int) -> None:
        super().__init__(target="x", control_qubits=[ctrl_qubit1, ctrl_qubit2], target_qubits=target_qubit,
                             theta=None, params=name_matrix_mapping[GateType.CCX])
        self._name = "CCX"
        self._data = (self._name, self._on_qubits, self._params)
        self._display_name = {ctrl_qubit1: "@", ctrl_qubit2: "@", target_qubit: "X"}
    
    def inverse(self) -> MCUGate:
        return CCX(self._ctrl_qubits[0], self._ctrl_qubits[1], self._target_qubits[0])

class CSWAP(MCUGate):
    """
    CSWAP gate (also known as Fredkin gate).
    It swaps the states of the target qubit and the swap qubit if the control qubit is in state |1>.
    """
    def __init__(self, ctrl_qubit: int, target_qubit1: int, target_qubit2: int) -> None:
        super().__init__(target=name_matrix_mapping[GateType.SWAP], control_qubits=ctrl_qubit, target_qubits=[target_qubit1, target_qubit2],
                             theta=None, params=name_matrix_mapping[GateType.CSWAP])
        self._name = "CSWAP"
        self._data = (self._name, self._on_qubits, self._params)
        self._display_name = {ctrl_qubit: "@", target_qubit1: "x", target_qubit2: "x"}
    
    def inverse(self) -> MCUGate:
        return CSWAP(self._ctrl_qubits[0], self._target_qubits[0], self._target_qubits[1])

TOFFOLI = CCX   # Alias for CCX gate
FREDKIN = CSWAP # Alias for CSWAP gate

# class MCUGate(Gate):
#     name = 'MCU'
#     """
#     Description: 构建MCU gate的参数为，name,matrix， control qubits，target qubits
#     target是指受控之前的矩阵，例如一个Controlled CNOT门，那么这个matrix就是CNOT的矩阵；这个参数也可以是字符串，例如'h'
#     """
#     def __init__(self, target: Union[str, np.ndarray, Callable[..., np.ndarray]],
#                  control_qubits: Union[int, List[int]],
#                  target_qubits: Union[int, List[int]],
#                  theta: Union[int, float, None] = None) -> None:
#         self._target = target
#         self._control_qubits = control_qubits if isinstance(control_qubits, list) else [control_qubits]
#         self._target_qubits = target_qubits if isinstance(target_qubits, list) else [target_qubits]
#         self._theta = theta
#         updated_matrix = self._get_matrix()
#         self._on_qubits = self._control_qubits + self._target_qubits
#         print(self._on_qubits)
#         super().__init__(name=self.__class__.name, on_qubits=self._on_qubits, matrix=updated_matrix, num_qubits=len(self._on_qubits))
#         self._display_name = {q: self.__class__.name for q in self._on_qubits}

#     def _get_on_qubits(self, on_qubits: List[int]) -> List[int]:
#         qubits_set = set(on_qubits)
#         if len(qubits_set) != len(on_qubits):
#             raise TgqSimError("Qubits should be unique.")
#         return on_qubits

#     # def reset_qubit(self, new_on_qubits: List[int]) -> 'MCUGate':  # xnj:是不是得改成重设控制比特和目标比特
#     #     self._target_qubit = self._get_on_qubits(new_on_qubits)
#     #     self._on_qubits = self._get_on_qubits(new_on_qubits)
#     #     # self._matrix = self._to_matrix()
#     #     return self

#     def reset_qubits(self, new_control_qubits: Union[int, List[int]], new_target_qubits: Union[int, List[int]]) -> 'MCUGate':  # xnj:是不是得改成重设控制比特和目标比特
#         self._control_qubits = new_control_qubits if isinstance(new_control_qubits, list) else [new_control_qubits]
#         self._target_qubit = new_target_qubits if isinstance(new_target_qubits, list) else [new_target_qubits]
#         self._on_qubits = self._get_on_qubits(new_on_qubits)
#         # self._matrix = self._to_matrix()
#         return self

#     def _get_matrix(self) -> np.ndarray:
#         if isinstance(self._target, str):
#             if self._target in SQGlibrary:
#                 matrix_params = SQGlibrary[self._target]
#             elif self._target in SPaulibrary and (isinstance(self._theta, float) or isinstance(self._theta, int)):
#                 matrix_params = SPaulibrary[self._target](self._theta)
#             else:
#                 # raise CircuitError("Wrong gate name.")
#                 raise TypeError("Wrong gate name.")
#         elif isinstance(self._target, np.ndarray):
#             matrix_params = self._target
#         else:
#             # raise CircuitError("Target should be a proper gate.")
#             raise TypeError("Target should be a proper gate.")
#         control_dim = 2 ** len(self._control_qubits)
#         target_dim = 2 ** len(self._target_qubits)

#         if len(matrix_params) != target_dim:
#             raise ValueError(
#                 f"Invalid number of qubits for target gate, there are {len(self._target_qubits)} target qubits, but the params is {len(matrix_params)} * {len(matrix_params)}.")
#         # check if the parameters are unitary
#         if not np.allclose(np.dot(matrix_params, matrix_params.conj().T), np.eye(target_dim), atol=1e-4):
#             raise ValueError("Parameters are not unitary.")

#         matrix_I_2 = I_GATE
#         num_qubits = len(self._control_qubits) + len(self._target_qubits)
#         q_dim = 2 ** (num_qubits)
#         matrix_I = np.eye(q_dim)
#         p_all_ctrl = np.array([1])
#         ctrl_matrix = np.array([1])
#         for i in range(len(self._control_qubits)):
#             cur_p_matrix = ONE_GATE
#             cur_u_matrix = matrix_I_2
#             p_all_ctrl = np.kron(p_all_ctrl, cur_p_matrix)
#             ctrl_matrix = np.kron(ctrl_matrix, cur_u_matrix)
#         p_all_ctrl = np.kron(p_all_ctrl, np.eye(target_dim))
#         cur_u_matrix = matrix_params
#         ctrl_matrix = np.kron(ctrl_matrix, cur_u_matrix)
#         mcu_matrix = matrix_I - p_all_ctrl + np.dot(p_all_ctrl, ctrl_matrix)
#         return mcu_matrix



if __name__ == "__main__":
    # Example usage
    def example_matrix(*args, **kwargs):
        return np.array([[0, 1], [1, 0]])

    qubits = [0,1,3]
    target_qubtis = [2]
    gate = MCUGate(target=example_matrix(), control_qubits=qubits, target_qubits=target_qubtis)
    print(gate)
    # print(gate.on_qubits)
    # print(gate.matrix)