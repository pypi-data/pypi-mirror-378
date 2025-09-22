from tgqSim.gate.gate_matrix import name_matrix_mapping, GateType
from tgqSim.gate.instruction import Gate
import tgqSim.utils.unitary as unitary

from typing import Union, Callable, List
import numpy as np


class SingleGate(Gate):
    """
    X gate (also known as NOT gate or Pauli-X gate).
    It flips the state of a qubit.
    """
    def __init__(self, name: str, on_qubits: int,
                 matrix: Union[np.ndarray, Callable[..., np.ndarray]], 
                 *args, **kwargs) -> None:
        self._args = args
        self._kwargs = kwargs
        # self._target_qubit = target_qubit
        matrix = self._validate_matrix(matrix)
        super().__init__(name=name, on_qubits=on_qubits, matrix=matrix, num_qubits=1)
        # self._target_qubit = self.on_qubits[0]
    
    @property
    def target_qubit(self) -> int:
        return self._on_qubits[0]
    
    def _to_matrix(self, matrix) -> np.ndarray:  #怎么检查是不是2*2的
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
        if len(matrix) != 2:
            raise ValueError("输入的Matrix应该为2*2矩阵")
        return matrix
    
    def reset_qubits(self, new_on_qubits: Union[int, List[int]]) -> 'SingleGate':
        if isinstance(new_on_qubits, list) and len(new_on_qubits) != 1:
            raise ValueError("重置比特只能输入1个数字")
        self._on_qubits = [new_on_qubits] if isinstance(new_on_qubits, int) else new_on_qubits
        tmpDisplayName = list(self._display_name.values())[0]
        self._display_name = {self._on_qubits[0]: tmpDisplayName}
        if self._parent_circuit is not None:
            self._parent_circuit._update_gate_display(self)
        self._data = (self._name, self._on_qubits, self._params)
        return self

class X(SingleGate):
    """
    X gate (also known as NOT gate or Pauli-X gate).
    It flips the state of a qubit.
    """
    def __init__(self, target_qubit: int) -> None:
        super().__init__(name="X", on_qubits=target_qubit, matrix=name_matrix_mapping[GateType.X])
        self._display_name = {target_qubit: "X"}
    
    def inverse(self) -> SingleGate:
        return X(self.target_qubit)


class Y(SingleGate):
    """
    Y gate (also known as Pauli-Y gate).
    It flips the state of a qubit and adds a phase of π/2.
    """
    def __init__(self, target_qubit: int) -> None:
        super().__init__(name="Y", on_qubits=target_qubit, matrix=name_matrix_mapping[GateType.Y])
        self._display_name = {target_qubit: "Y"}
    
    def inverse(self) -> SingleGate:
        return Y(self.target_qubit)

class Z(SingleGate):
    """
    Z gate (also known as Pauli-Z gate).
    It adds a phase of π to the state of a qubit.
    """
    def __init__(self, target_qubit: int) -> None:
        super().__init__(name="Z", on_qubits=target_qubit, matrix=name_matrix_mapping[GateType.Z])
        self._display_name = {target_qubit: "Z"}
    
    def inverse(self) -> SingleGate:
        return Z(self.target_qubit)

class SQRT_X(SingleGate):
    """
    SQRT_X gate (also known as Square Root of X gate).
    It is a square root of the X gate.
    """
    def __init__(self, target_qubit: int) -> None:
        super().__init__(name="SQRT_X", on_qubits=target_qubit, matrix=name_matrix_mapping[GateType.SQRT_X])
        self._display_name = {target_qubit: "X^½"}
    
    def inverse(self) -> SingleGate:
        return SQRT_X_DAG(self.target_qubit)

class SQRT_X_DAG(SingleGate):
    """
    SQRT_X_DAG gate (also known as Square Root of X-dagger gate).
    It is the inverse of the SQRT_X gate.
    """
    def __init__(self, target_qubit: int) -> None:
        super().__init__(name="SQRT_X_DAG", on_qubits=target_qubit, matrix=name_matrix_mapping[GateType.SQRT_X_DAG])
        self._display_name = {target_qubit: "X^½†"}
    
    def inverse(self) -> SingleGate:
        return SQRT_X(self.target_qubit)

class RX(SingleGate):
    """
    RX gate (also known as Rotation around X axis).
    It rotates the state of a qubit around the X axis by a specified angle.
    """
    def __init__(self, target_qubit: int, theta: float) -> None:
        super().__init__(name="RX", on_qubits=target_qubit, matrix=name_matrix_mapping[GateType.RX], theta=theta)
        self._display_name = {target_qubit: f"Rx({round(theta, 2)})"}
        self._theta = theta
    
    @property
    def theta(self):
        return self._theta
    
    def inverse(self) -> SingleGate:
        return RX(self.target_qubit, -self.theta)


class RY(SingleGate):
    """
    RY gate (also known as Rotation around Y axis).
    It rotates the state of a qubit around the Y axis by a specified angle.
    """
    def __init__(self, target_qubit: int, theta: float) -> None:
        super().__init__(name="RY", on_qubits=target_qubit, matrix=name_matrix_mapping[GateType.RY], theta=theta)
        self._display_name = {target_qubit: f"Ry({round(theta, 2)})"}
        self._theta = theta
    
    @property
    def theta(self):
        return self._theta
    
    def inverse(self) -> SingleGate:
        return RY(self.target_qubit, -self.theta)

class RZ(SingleGate):
    """
    RZ gate (also known as Rotation around Z axis).
    It rotates the state of a qubit around the Z axis by a specified angle.
    """
    def __init__(self, target_qubit: int, theta: float) -> None:
        super().__init__(name="RZ", on_qubits=target_qubit, matrix=name_matrix_mapping[GateType.RZ], theta=theta)
        # print("inclass: ", type(target_qubit))
        self._display_name = {target_qubit: f"Rz({round(theta, 2)})"}
        self._theta = theta
    
    @property
    def theta(self):
        return self._theta
    
    def inverse(self) -> SingleGate:
        return RZ(self.target_qubit, -self.theta)

class H(SingleGate):
    """
    H gate (also known as Hadamard gate).
    It creates superposition by transforming |0> to (|0> + |1>) / √2 and |1> to (|0> - |1>) / √2.
    """
    def __init__(self, target_qubit: int) -> None:
        super().__init__(name="H", on_qubits=target_qubit, matrix=name_matrix_mapping[GateType.H])
        self._display_name = {target_qubit: "H"}
    
    def inverse(self) -> SingleGate:
        return H(self.target_qubit)

class S(SingleGate):
    """
    S gate (also known as Phase gate).
    It adds a phase of π/2 to the state of a qubit.
    """
    def __init__(self, target_qubit: int) -> None:
        super().__init__(name="S", on_qubits=target_qubit, matrix=name_matrix_mapping[GateType.S])
        self._display_name = {target_qubit: "S"}
    
    def inverse(self) -> SingleGate:
        return S_DAG(self.target_qubit)

class S_DAG(SingleGate):
    """
    S_DAG gate (also known as S-dagger or S-inverse gate).
    It adds a phase of -π/2 to the state of a qubit.
    """
    def __init__(self, target_qubit: int) -> None:
        super().__init__(name="S_DAG", on_qubits=target_qubit, matrix=name_matrix_mapping[GateType.S_DAG])
        self._display_name = {target_qubit: "S†"}
    
    def inverse(self) -> SingleGate:
        return S(self.target_qubit)

class T(SingleGate):
    """
    T gate (also known as T-gate or π/8 gate).
    It adds a phase of π/4 to the state of a qubit.
    """
    def __init__(self, target_qubit: int) -> None:
        super().__init__(name="T", on_qubits=target_qubit, matrix=name_matrix_mapping[GateType.T])
        self._display_name = {target_qubit: "T"}
    
    def inverse(self) -> SingleGate:
        return T_DAG(self.target_qubit)

class T_DAG(SingleGate):
    """
    T_DAG gate (also known as T-dagger or T-inverse gate).
    It adds a phase of -π/4 to the state of a qubit.
    """
    def __init__(self, target_qubit: int) -> None:
        super().__init__(name="T_DAG", on_qubits=target_qubit, matrix=name_matrix_mapping[GateType.T_DAG])
        self._display_name = {target_qubit: "T†"}
    
    def inverse(self) -> SingleGate:
        return T(self.target_qubit)


class U(SingleGate):
    """
    U gate (also known as U3 gate).
    It is a universal single-qubit gate that can represent any single-qubit operation.
    """
    def __init__(self, target_qubit: int, matrix: np.ndarray) -> None:
        super().__init__(name="U", on_qubits=target_qubit, matrix=matrix)
        self._display_name = {target_qubit: "UGate"}
    
    def inverse(self) -> SingleGate:
        return U(self.target_qubit, self._matrix.conjugate().T)


if __name__ == "__main__":
    # Example Usage
    x_gate = X(target_qubit=0)
    print(x_gate)
