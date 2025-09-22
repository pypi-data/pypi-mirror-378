from tgqSim.gate.instruction import Gate
from tgqSim.gate.gate_matrix import name_matrix_mapping, GateType
from tgqSim.utils.tgq_expection import TgqSimError
from tgqSim.gate.multi_ctrl_gate import *
import tgqSim.utils.unitary as unitary

from typing import Union, Callable, List
import numpy as np


class DoubleGate(Gate):
    """
    DoubleGate is a class that represents a quantum gate that operates on two qubits.
    """

    def __init__(self, name: str, matrix: Union[np.ndarray, Callable[..., np.ndarray]],
                 on_qubits: List[int],
                 *args, **kwargs) -> None:
        self._args = args
        self._kwargs = kwargs
        matrix = self._validate_matrix(matrix)
        on_qubits = self._get_on_qubits(on_qubits)
        super().__init__(name=name, on_qubits=on_qubits, matrix=matrix, num_qubits=2)
        # self._control_qubit = self.on_qubits[0]
        # self._target_qubit = self.on_qubits[1]

    @property
    def control_qubit(self) -> int:
        return self._on_qubits[0]

    @property
    def target_qubit(self) -> int:
        return self._on_qubits[1]

    def _to_matrix(self, matrix: Union[np.ndarray, Callable[..., np.ndarray]]) -> np.ndarray:
        if not isinstance(matrix, np.ndarray):
            matrix_func = matrix
        if len(self._args) > 0:
            return matrix_func(*self._args)
        elif len(self._kwargs) > 0:
            return matrix_func(**self._kwargs)
        else:
            return matrix

    def _validate_matrix(self, matrix):
        matrix = self._to_matrix(matrix)
        if not unitary.is_unitary_matrix(matrix):
            raise ValueError("输入的Matrix不是酉矩阵")
        if len(matrix) != 4:
            raise ValueError("输入的Matrix应该为4*4矩阵")
        return matrix

    def _get_on_qubits(self, on_qubits: List[int]) -> List[int]:
        qubits_set = set(on_qubits)
        if len(qubits_set) != len(on_qubits):
            raise TgqSimError("Qubits should be unique.")
        if len(on_qubits) != 2:
            raise TgqSimError("Double Gate should have two qubits.")
        return on_qubits

    def reset_qubits(self, new_on_qubits: List[int]) -> 'DoubleGate':
        self._on_qubits = self._get_on_qubits(new_on_qubits)
        tmp = {}
        for i, val in enumerate(self._display_name.values()):
            tmp[new_on_qubits[i]] = val
        self._display_name = tmp
        self._data = (self._name, self._on_qubits, self._params)
        return self


# class CX(DoubleGate):
#     """
#     CNOT gate (also known as Controlled-NOT gate).
#     It flips the state of the target qubit if the control qubit is in state |1>.
#     """

#     def __init__(self, control_qubit: int, target_qubit: int) -> None:
#         if control_qubit < target_qubit:
#             super().__init__(name="CX", matrix=name_matrix_mapping[GateType.CNOT_CS],
#                              on_qubits=[control_qubit, target_qubit])
#         else:
#             super().__init__(name="CX", matrix=name_matrix_mapping[GateType.CNOT_CB],
#                              on_qubits=[control_qubit, target_qubit])
#         self._display_name = {control_qubit: "@", target_qubit: "X"}

#     def inverse(self) -> DoubleGate:
#         return CX(self.control_qubit, self.target_qubit)


# class CZ(DoubleGate):
#     """
#     CZ gate (also known as Controlled-Z gate).
#     It adds a phase of π to the target qubit if the control qubit is in state |1>.
#     """

#     def __init__(self, control_qubit: int, target_qubit: int) -> None:
#         super().__init__(name="CZ", matrix=name_matrix_mapping[GateType.CZ], on_qubits=[control_qubit, target_qubit])
#         self._display_name = {control_qubit: "@", target_qubit: "Z"}

#     def inverse(self) -> DoubleGate:
#         return CZ(self.control_qubit, self.target_qubit)


class SWAP(DoubleGate):
    """
    SWAP gate.
    It swaps the states of two qubits.
    """

    def __init__(self, qubit1: int, qubit2: int) -> None:
        super().__init__(name="SWAP", matrix=name_matrix_mapping[GateType.SWAP], on_qubits=[qubit1, qubit2])
        self._display_name = {qubit1: "x", qubit2: "x"}

    def inverse(self) -> DoubleGate:
        return SWAP(self.control_qubit, self.target_qubit)


# class CP(DoubleGate):
#     """
#     CP gate (also known as Controlled-Phase gate).
#     It adds a phase to the target qubit if the control qubit is in state |1>.
#     """

#     def __init__(self, control_qubit: int, target_qubit: int, theta: float) -> None:
#         super().__init__(name="CP", matrix=name_matrix_mapping[GateType.CP], on_qubits=[control_qubit, target_qubit],
#                          theta=theta)
#         self._display_name = {control_qubit: "@", target_qubit: f"P({round(theta, 2)})"}
#         self._theta = theta

#     @property
#     def theta(self) -> float:
#         return self._theta

#     def inverse(self) -> DoubleGate:
#         return CP(self.control_qubit, self.target_qubit, --self.theta)


class ISWAP(DoubleGate):  # xnj: 在这边加个逆门？算了
    """
    ISWAP gate.
    It swaps the states of two qubits and adds a phase of π/2.
    """

    def __init__(self, control_qubit: int, target_qubit: int) -> None:
        super().__init__(name="ISWAP", matrix=name_matrix_mapping[GateType.ISWAP],
                         on_qubits=[control_qubit, target_qubit])
        self._display_name = {control_qubit: "ISWAP", target_qubit: "ISWAP"}

    def inverse(self) -> DoubleGate:
        return DU(self.control_qubit, self.target_qubit, np.array([[1, 0, 0, 0], [0, 0, -1j, 0], [0, -1j, 0, 0], [0, 0, 0, 1]], dtype=np.complex128))
    # ISWAP(self.control_qubit, self.target_qubit)


class RXX(DoubleGate):
    """
    RXX gate.
    It applies a rotation around the X axis to two qubits.
    """

    def __init__(self, control_qubit: int, target_qubit: int, theta: float) -> None:
        super().__init__(name="RXX", matrix=name_matrix_mapping[GateType.RXX], on_qubits=[control_qubit, target_qubit],
                         theta=theta)
        self._display_name = {control_qubit: f"RXX({round(theta, 2)})", target_qubit: f"RXX({round(theta, 2)})"}
        self._theta = theta

    @property
    def theta(self) -> float:
        return self._theta

    def inverse(self) -> DoubleGate:
        return RXX(self.control_qubit, self.target_qubit, --self.theta)


class RYY(DoubleGate):
    """
    RYY gate.
    It applies a rotation around the Y axis to two qubits.
    """

    def __init__(self, control_qubit: int, target_qubit: int, theta: float) -> None:
        super().__init__(name="RYY", matrix=name_matrix_mapping[GateType.RYY], on_qubits=[control_qubit, target_qubit],
                         theta=theta)
        self._display_name = {control_qubit: f"RYY({round(theta, 2)})", target_qubit: f"RYY({round(theta, 2)})"}
        self._theta = theta

    @property
    def theta(self) -> float:
        return self._theta

    def inverse(self) -> DoubleGate:
        return RYY(self.control_qubit, self.target_qubit, --self.theta)


class RZZ(DoubleGate):
    """
    RZZ gate.
    It applies a rotation around the Z axis to two qubits.
    """

    def __init__(self, control_qubit: int, target_qubit: int, theta: float) -> None:
        super().__init__(name="RZZ", matrix=name_matrix_mapping[GateType.RZZ], on_qubits=[control_qubit, target_qubit],
                         theta=theta)
        self._display_name = {control_qubit: f"RZZ({round(theta, 2)})", target_qubit: f"RZZ({round(theta, 2)})"}
        self._theta = theta

    @property
    def theta(self) -> float:
        return self._theta

    def inverse(self) -> DoubleGate:
        return RZZ(self.control_qubit, self.target_qubit, --self.theta)


class DU(DoubleGate):
    """
    DU gate (double-qubit gate).
    It is a universal double-qubit gate that can represent any double-qubit operation.
    """

    def __init__(self, control_qubit: int, target_qubit: int, matrix: np.ndarray) -> None:
        super().__init__(name="DU", matrix=matrix, on_qubits=[control_qubit, target_qubit])
        self._display_name = {control_qubit: "DUGate", target_qubit: "DUGate"}

    def inverse(self) -> DoubleGate:
        return DU(self.control_qubit, self.target_qubit, self._matrix.conjugate().T)


class SYC(DoubleGate):
    """
    SYC gate.
    It is a controlled-Y gate with a phase of -π/6.
    """

    def __init__(self, control_qubit: int, target_qubit: int) -> None:
        super().__init__(name="SYC", matrix=name_matrix_mapping[GateType.SYC], on_qubits=[control_qubit, target_qubit])
        self._display_name = {control_qubit: "SYC", target_qubit: "SYC"}

    def inverse(self) -> DoubleGate:
        return DU(self.control_qubit, self.target_qubit, np.array([[1, 0, 0, 0], [0, 0, 1j, 0], [0, 1j, 0, 0], [0, 0, 0, np.exp(1j * np.pi / 6)]], dtype=np.complex128))

CUlibrary = {'X': CX, 'Z': CZ}
