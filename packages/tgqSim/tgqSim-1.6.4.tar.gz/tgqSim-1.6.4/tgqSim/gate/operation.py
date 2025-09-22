from tgqSim.gate.instruction import Gate
from tgqSim.gate.bit import QuantumRegister, Qubit
import tgqSim.utils.unitary as unitary

from typing import Union, List, Callable
import numpy as np

class Operation(Gate):
    def __init__(self, name: str, 
                 on_qubits: Union[Qubit, List[Qubit], QuantumRegister], 
                 matrix: Union[np.ndarray, Callable[..., np.ndarray]],
                 num_qubits: int, 
                 *args, **kwargs) -> None:
        self._args = args
        self._kwargs = kwargs
        self._matrix = self._validate_matrix(matrix)
        super().__init__(name=name, on_qubits=on_qubits, matrix=self._matrix, num_qubits=num_qubits)
        self._display_name = self._get_display_name()
        
    @property
    def target_qubit(self):
        return self._on_qubits
    
    @property
    def control_qubit(self):
        return self._ctrl_qubits
    
    def _to_matrix(self, matrix) -> np.ndarray:
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
        return matrix