from tgqSim.gate.instruction import Gate
from tgqSim.gate.bit import Qubit
from tgqSim.utils.tgq_expection import TgqSimError
from tgqSim.gate.multi_ctrl_gate import *
import tgqSim.utils.unitary as unitary

from typing import Union, Callable, List
import numpy as np


class MQGate(Gate):
    """
    MQGate is a class that represents a quantum gate that operates on multi-qubits.
    """
    def __init__(self, name: str, matrix: Union[np.ndarray, Callable[..., np.ndarray]], 
                 on_qubits: List[Qubit], *args, **kwargs) -> None:
        self._args = args
        self._kwargs = kwargs
        # self._target_qubit = self._get_on_qubits(on_qubits)
        on_qubits = self._get_on_qubits(on_qubits)
        num_qubits = len(on_qubits)
        matrix = self._validate_matrix(matrix, num_qubits)
        super().__init__(name=name, on_qubits=on_qubits, matrix=matrix, num_qubits=num_qubits)
    
    @property
    def target_qubit(self) -> List[int]:
        return self._on_qubits
    
    def _to_matrix(self, matrix: Union[np.ndarray, Callable[..., np.ndarray]]) -> np.ndarray:
        if not isinstance(matrix, np.ndarray):
            matrix_func = matrix
        if len(self._args) > 0:
            return matrix_func(*self._args)
        elif len(self._kwargs) > 0:
            return matrix_func(**self._kwargs)
        else:
            return matrix
    
    def _validate_matrix(self, matrix, num_qubits):
        matrix = self._to_matrix(matrix)
        if not unitary.is_unitary_matrix(matrix):
            raise ValueError("输入的Matrix不是酉矩阵")
        gate_dim = 2 ** num_qubits
        if len(matrix) != gate_dim:
            raise ValueError(f"输入的Matrix应该为{gate_dim} * {gate_dim}矩阵")
        return matrix
    
    def _get_on_qubits(self, on_qubits: List[int]) -> List[int]:
        qubits_set = set(on_qubits)
        if len(qubits_set) != len(on_qubits):
            raise TgqSimError("Qubits should be unique.")
        return on_qubits
    
    def reset_qubits(self, new_on_qubits: List[int]) -> 'MQGate':
        tmp_on_qubits = self._get_on_qubits(new_on_qubits)
        if len(tmp_on_qubits) != self._num_qubits:
            raise TgqSimError("重置比特时应该保证比特数不变.")
        self._on_qubits = tmp_on_qubits
        # self._matrix = self._to_matrix()
        tmp = {}
        for i, val in enumerate(self._display_name.values()):
            tmp[new_on_qubits[i]] = val
        self._display_name = tmp
        self._data = (self._name, self._on_qubits, self._params)
        return self

# class CCX(MQGate):
#     """
#     CCX gate (also known as Toffoli gate).
#     It flips the state of the target qubit if both control qubits are in state |1>.
#     """
#     def __init__(self, ctrl_qubit1: int, ctrl_qubit2: int, target_qubit: int) -> None:
#         super().__init__(name="CCX", matrix=name_matrix_mapping[GateType.CCX], on_qubits=[ctrl_qubit1, ctrl_qubit2, target_qubit])
#         self._display_name = {ctrl_qubit1: "@", ctrl_qubit2: "@", target_qubit: "X"}
    
#     def inverse(self) -> MQGate:
#         return CCX(self._on_qubits[0], self._on_qubits[1], self._on_qubits[2])

# class CSWAP(MQGate):
#     """
#     CSWAP gate (also known as Fredkin gate).
#     It swaps the states of the target qubit and the swap qubit if the control qubit is in state |1>.
#     """
#     def __init__(self, ctrl_qubit: int, swap_qubit: int, target_qubit: int) -> None:
#         super().__init__(name="CSWAP", matrix=name_matrix_mapping[GateType.CSWAP], on_qubits=[ctrl_qubit, swap_qubit, target_qubit])
#         self._display_name = {ctrl_qubit: "@", swap_qubit: "x", target_qubit: "x"}
    
#     def inverse(self) -> MQGate:
#         return CSWAP(self._on_qubits[0], self._on_qubits[1], self._on_qubits[2])



class MU(MQGate):
    """
    MU gate (multi-qubit gate).
    It is a universal double-qubit gate that can represent any double-qubit operation.
    """

    def __init__(self, on_qubits: List[int], matrix: np.ndarray) -> None:
        super().__init__(name="MU", matrix=matrix, on_qubits=on_qubits)
        self._display_name = {}
        for q in self._on_qubits:
            self._display_name[q] = 'MU'

    def inverse(self) -> MQGate:
        return MU(self._on_qubits, self._matrix.conjugate().T)
