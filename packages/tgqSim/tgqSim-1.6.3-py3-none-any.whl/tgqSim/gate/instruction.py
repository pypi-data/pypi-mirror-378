from typing import Union, List
import numpy as np
# from gate.bit import Qubit
import copy
from utils.unitary import is_unitary_matrix
# from gate.multi_ctrl_gate import MCUGate
from scipy.linalg import block_diag
from utils.tgq_expection import TgqSimError
from gate.gate_matrix import *
from typing import List, Union, Callable, Dict

ZERO_GATE = np.array([[1, 0], [0, 0]], dtype=np.complex128)  # |0><0|
ONE_GATE = np.array([[0, 0], [0, 1]], dtype=np.complex128)  # |1><1|


class Instruction:
    __slots__ = ['_name', '_on_qubits', '_matrix', '_params', '_data']

    def __init__(self, name: str,
                 on_qubits: Union[int, List[int]],
                 matrix: Union[np.ndarray, None] = None) -> None:
        self._name = name
        self._matrix = matrix
        self._params = matrix
        self._on_qubits = on_qubits if isinstance(on_qubits, list) else [on_qubits]
        self._data = (self._name, self._on_qubits, self._params)
        if not is_unitary_matrix(self._matrix):
            raise ValueError(f"The matrix for gate {self._name} is not unitary.")

    @property
    def name(self):
        return self._name

    @property
    def params(self) -> np.ndarray:
        return self._params

    @property
    def matrix(self) -> np.ndarray:
        return self._matrix

    @property
    def data(self) -> tuple:
        return self._data

    def __getitem__(self, index):
        return self._data[index]  # 实现索引访问

    def __repr__(self):
        return f"({', '.join(map(repr, self._data))})"  # 友好显示
    
    def upload_params(self):
        pass
            

class Gate(Instruction):
    def __init__(self, name: str,
                 on_qubits: Union[int, List[int]],
                 matrix: np.ndarray,
                 num_qubits: int
                 ) -> None:
        super().__init__(name=name, on_qubits=on_qubits, matrix=matrix)
        self._display_name = {}
        self._num_qubits = num_qubits
        self._ctrl_qubits = list()
        self._target_qubits = [on_qubits] if isinstance(on_qubits, int) else on_qubits
        self._parent_circuit = None

    # @property
    # def num_qbits(self) -> int:
    #     return self._num_qubits

    def __setattr__(self, name: str, value: Union[int, List[int]]) -> None:
        super().__setattr__(name, value)

    @property
    def display_name(self) -> dict:
        return self._display_name

    @property
    def on_qubits(self) -> List[int]:
        return self._on_qubits

    @on_qubits.setter
    def on_qubits(self, qubit: Union[int, List[int]]) -> None:
        # print("Setting on_qubits to:", qubit)
        if isinstance(qubit, int):
            self._on_qubits = [qubit]
            self._display_name = {qubit: self._display_name.values()[0]}
        elif isinstance(qubit, list):
            self._on_qubits = qubit
            tmp = {}
            for i, val in enumerate(self._display_name.values()):
                tmp[qubit[i]] = val
            self._display_name = tmp
        else:
            raise ValueError("on_qubits must be a Qubit or a list of Qubits.")
        if self._parent_circuit is not None:
            self._parent_circuit._update_gate_display(self)

    @property
    def num_qubits(self) -> int:
        return self._num_qubits

    @property
    def ctrl_qubits(self) -> list:
        return self._ctrl_qubits
    
    @property
    def target_qubits(self):
        return self._target_qubits

    # def control_by(self, control_qubits: int) -> 'Gate':  # xnj:如果对一个单比特门用control by方法，返回依旧是一个单门类？是否还需要考虑加List[int]？
    #     if control_qubits in self._on_qubits:
    #         raise ValueError("Control qubit cannot be one of the target qubits.")
    #     # self.ctrl_qbit.append(ctrl_qbit)
    #     self._ctrl_qubits.append(control_qubits)
    #     self._display_name[control_qubits] = '@'
    #     self._on_qubits.append(control_qubits)
    #     self._num_qubits += 1
    #     self._params = self._update_params()
    #     # qubits = [self._on_qubits[i].index() for i in range(len(self._on_qubits))]
    #     self._data = (self._name, self._on_qubits, self._params)
    #     return self

    def control_by(self, control_qubits: int) -> 'Gate':
        if control_qubits in self._on_qubits:
            raise ValueError("Control qubit cannot be one of the target qubits.")
        # self.ctrl_qbit.append(ctrl_qbit)
        self._ctrl_qubits.append(control_qubits)
        self._display_name[control_qubits] = '@'
        self._on_qubits.append(control_qubits)
        # self._num_qubits += 1
        # self._params = self._update_params()
        # # qubits = [self._on_qubits[i].index() for i in range(len(self._on_qubits))]
        # self._data = (self._name, self._on_qubits, self._params)
        return MCUGate(self._matrix, self._ctrl_qubits, self._target_qubits, self._display_name)

        # if control_qubits in self._on_qubits:
        #     raise ValueError("Control qubit cannot be one of the target qubits.")
        # # self.ctrl_qbit.append(ctrl_qbit)
        # self._ctrl_qubits.append(control_qubits)
        # self._display_name[control_qubits] = '@'
        # self._on_qubits.append(control_qubits)
        # on_qubits_set = set(self._on_qubits)
        # control_qubit_set = set(self._ctrl_qubits)
        # target_qubit_list = list(on_qubits_set.difference(control_qubit_set))
        # self._num_qubits += 1
        # self._params = self._update_params()
        # # qubits = [self._on_qubits[i].index() for i in range(len(self._on_qubits))]
        # self._data = (self._name, self._on_qubits, self._params)
        # if len(self._ctrl_qubits) == 1:
        #     from gate.double_gate import CUlibrary
        #     if self._name in CUlibrary:
        #         return CUlibrary[self._name](self._ctrl_qubits[0], target_qubit_list[0])
                
        # return self

    def _update_params(self):
        if self.num_qubits == 2:
            mcu_matrix = np.eye(2 ** self._num_qubits, dtype=np.complex128)
            on_qubits_set = set(self._on_qubits)
            control_qubit_set = set(self._ctrl_qubits)
            target_qubit_list = list(on_qubits_set.difference(control_qubit_set))
            index_str, need_change_index = ["1" for _ in range(self._num_qubits)], []
            length_target = len(target_qubit_list)
            for i in range(2 ** length_target):
                i_binary_str = format(i, f'0{length_target}b')
                for i, bin_str in enumerate(i_binary_str):
                    index_str[target_qubit_list[i]] = bin_str
                need_change_index.append(int(''.join(index_str), 2))
            x, y = np.meshgrid(need_change_index, need_change_index)
            mcu_matrix[x, y] = self._matrix
            return mcu_matrix
        else:
            return self._matrix

    def _params_display(self, original_params: tuple) -> tuple:
        tmp_tuple = ()
        for ele in original_params:
            if isinstance(ele, (int, float, complex)):
                tmp_tuple += (round(ele, 2),)
            else:
                tmp_tuple += (ele,)
        return tmp_tuple

    def _get_display_name(self) -> dict:
        display_name = {}
        if len(self._args) != 0:
            if len(self._args) > 1:
                display_params = self._params_display(self._args)
                display_model = f"{self._name}{display_params}"
            elif len(self._args) == 1:
                display_model = f"{self._name}{self._args}".replace(",", "")
        elif len(self._kwargs) != 0:
            display_model = f"{self._name}({', '.join([str(round(ele, 2)) for ele in self._kwargs.values()])})"
        else:
            display_model = f"{self._name}"

        if isinstance(self._on_qubits, int):
            display_name[self._on_qubits] = display_model
        else:
            for ele in self._on_qubits:
                display_name[ele] = display_model

        return display_name

    def reset_qubits(self, target_qubits: List[int]) -> None:
        pass

    def inverse(self) -> 'Gate':
        # Inverse operation logic
        pass


class MCUGate(Gate):
    """
    Description: 构建MCU gate的参数为，name,matrix， control qubits，target qubits
    target是指受控之前的矩阵，例如一个Controlled CNOT门，那么这个matrix就是CNOT的矩阵；这个参数也可以是字符串，例如'h'
    """
    def __init__(self, target: Union[str, np.ndarray, Callable[..., np.ndarray]],
                 control_qubits: Union[int, List[int]],
                 target_qubits: Union[int, List[int]],
                 display_name: Union[Dict, None] = None, 
                 *args, **kwargs) -> None:
        """_summary_

        Args:
            target (Union[str, np.ndarray, Callable[..., np.ndarray]]):
               存在三种情形：
                  1. 传递字符串：这个字符串仅仅支持框架目前支持的门序列；
                  2. 传递不含参数的矩阵：量子门对应的矩阵，不含参数
                  3. 传递含参数的矩阵：量子门对应的矩阵，含参数，通过args或者kwargs传递参数
            control_qubits (Union[int, List[int]]): 控制比特序列
            target_qubits (Union[int, List[int]]): 受控比特序列
            display_name (Union[Dict, None], optional): 线路展示. Defaults to None.
        """
        on_qubits = self._get_on_qubits(control_qubits, target_qubits)
        # self._num_qubits = len(self._on_qubits)
        # self._matrix = params
        # print("args:", kwargs)
        target_matrix = self._get_target(target, target_qubits, *args, **kwargs)
        super().__init__(name=self.__class__.name, on_qubits=on_qubits, matrix=target_matrix, num_qubits=len(on_qubits))
        # self._num_qubits = len(on_qubits)
        self._name = 'MCU'
        # super().__init__(name=self.__class__.name, on_qubits=on_qubits, matrix=target_matrix, num_qubits=len(on_qubits))
        self._ctrl_qubits = control_qubits if isinstance(control_qubits, list) else [control_qubits]
        self._target_qubits = target_qubits if isinstance(target_qubits, list) else [target_qubits]
        self._params = self._update_params()
        # self._params = self._get_params() if params is None else params
        self._display_name = {}
        if display_name is not None:
            self._display_name = display_name
        else:
            gateName = "MCU" if not isinstance(target, str) else target.upper()
            self._data = (gateName, self._on_qubits, self._params)
            for q in self._ctrl_qubits:
                self._display_name[q] = '@'
            for q in self._target_qubits:
                self._display_name[q] = gateName
        self._data = (self._name, self._on_qubits, self._params)
        # self._display_name = {q:  for q in self._on_qubits}
    
    @property
    def control_qubits(self) -> List[int]:
        return self._ctrl_qubits

    @property
    def target_qubits(self) -> List[int]:
        return self._target_qubits
    
    @property
    def num_qubits(self) -> int:
        return self._num_qubits
    
    @property
    def display_name(self) -> Dict[int, str]:
        return self._display_name
    
    @property
    def ctrl_qubits(self):
        return self._ctrl_qubits
    
    @property
    def on_qubits(self):
        return self._on_qubits

    @on_qubits.setter
    def on_qubits(self, qubit: Union[int, List[int]]) -> None:
        # print("Setting on_qubits to:", qubit)
        if isinstance(qubit, int):
            self._on_qubits = [qubit]
            self._display_name = {qubit: self._display_name.values()[0]}
        elif isinstance(qubit, list):
            self._on_qubits = qubit
            tmp = {}
            for i, val in enumerate(self._display_name.values()):
                tmp[qubit[i]] = val
            self._display_name = tmp
        else:
            raise ValueError("on_qubits must be a Qubit or a list of Qubits.")
        if self._parent_circuit is not None:
            self._parent_circuit._update_gate_display(self)
    # def _get_on_qubits(self, on_qubits: List[int]) -> List[int]:  # xnj: 需要检查一下控制比特和目标比特是否重叠
    #     qubits_set = set(on_qubits)
    #     if len(qubits_set) != len(on_qubits):
    #         raise TgqSimError("Qubits should be unique.")
    #     return on_qubits

    # def reset_qubit(self, new_on_qubits: List[int]) -> 'MCUGate':  # xnj:是不是得改成重设控制比特和目标比特
    #     self._target_qubit = self._get_on_qubits(new_on_qubits)
    #     self._on_qubits = self._get_on_qubits(new_on_qubits)
    #     # self._matrix = self._to_matrix()
    #     return self
    
    def control_by(self, control_qubit: int):
        if control_qubit in self._on_qubits:
            raise ValueError("Control qubit cannot be one of the target qubits.")
        self._on_qubits.append(control_qubit)
        self._ctrl_qubits.append(control_qubit)
        self._num_qubits += 1
        self._display_name[control_qubit] = '@'
        self._params = self._update_params()
        self._data = (self._name, self._on_qubits, self._params)
        return self
    
    def upload_params(self):
        num_qubits = len(self._on_qubits)
        if num_qubits >= 3:
            length_ctrl_qubits = len(self._ctrl_qubits)
            length_target_qubits = len(self._target_qubits)
            if length_ctrl_qubits + length_target_qubits != num_qubits:
                raise ValueError("The sum of control qubits and target qubits must be equal total qubits")
            if self._matrix.shape != (2**length_target_qubits, 2**length_target_qubits):
                raise ValueError("The shape of target matrix must be same to 2^number_of_target_qubits")
            self._params = np.eye(2**num_qubits, 2**num_qubits, dtype=np.complex128)
            axis_id = list(range(2**num_qubits - 2**length_target_qubits, 2**num_qubits))
            x, y = np.meshgrid(axis_id, axis_id)
            self._params[x, y] = self._matrix
            self._data = (self._name, self._on_qubits, self._params)
        return self
        
    def _update_params(self):
        if self._num_qubits == 2:
            # mcu_matrix = np.eye(2 ** self._num_qubits, dtype=np.complex128)
            # on_qubits_set = set(self._on_qubits)
            # control_qubit_set = set(self._ctrl_qubits)
            # target_qubit_list = list(on_qubits_set.difference(control_qubit_set))
            # index_str, need_change_index = ["1" for _ in range(self._num_qubits)], []
            # length_target = len(target_qubit_list)
            # for i in range(2 ** length_target):
            #     i_binary_str = format(i, f'0{length_target}b')
            #     for i, bin_str in enumerate(i_binary_str):
            #         index_str[target_qubit_list[i]] = bin_str
            #     need_change_index.append(int(''.join(index_str), 2))
            # x, y = np.meshgrid(need_change_index, need_change_index)
            # mcu_matrix[x, y] = self._matrix
            # return mcu_matrix
            if self._ctrl_qubits[0] < self._target_qubits[0]:
                mcu_matrix = np.kron(ZERO_GATE, I_GATE) + np.kron(ONE_GATE, self._matrix)
            else:
                mcu_matrix = np.kron(I_GATE, ZERO_GATE) + np.kron(self._matrix, ONE_GATE)
            return mcu_matrix
        else:
            return np.array([])

    def _get_on_qubits(self, control_qubits: Union[int, List[int]], target_qubits: Union[int, List[int]]) -> List[int]:
        control_qubits = control_qubits if isinstance(control_qubits, list) else [control_qubits]
        target_qubits = target_qubits if isinstance(target_qubits, list) else [target_qubits]
        control_qubits_set = set(control_qubits)
        target_qubits_set = set(target_qubits)
        if len(control_qubits) != len(control_qubits_set):
            raise TgqSimError("Control qubits should on different qubits.")
        if len(target_qubits) != len(target_qubits_set):
            raise TgqSimError("Target qubits should on different qubits.")
        if control_qubits_set.intersection(target_qubits_set):
            raise TgqSimError("Control qubits and target qubits should not intersect.")
        return control_qubits + target_qubits

    def _get_target(self, target, target_qubits, *args, **kwargs) -> np.ndarray:
        # print("get_target----kwargs:", kwargs)
        if isinstance(target, str):
            if target in SQGlibrary:
                matrix_params = SQGlibrary[target]
            elif target in SPaulibrary:
                if len(args) > 0:
                    matrix_params = SPaulibrary[target](*args)
                elif len(kwargs) > 0:
                    matrix_params = SPaulibrary[target](**kwargs)
            else:
                raise TypeError("Wrong gate name.")
        elif isinstance(target, np.ndarray):
            matrix_params = target
        else:
            if len(args) > 0:
                matrix_params = target(*args)
            elif len(kwargs) > 0:
                matrix_params = target(**kwargs)
        target_qubits = target_qubits if isinstance(target_qubits, list) else [target_qubits]
        target_dim = 2 ** len(target_qubits)
        if len(matrix_params) != target_dim:
            raise TgqSimError(f"Invalid number of qubits for target gate, there are {len(target_qubits)} target qubits, but the params is {len(matrix_params)} * {len(matrix_params)}.")
        return matrix_params

    def _get_params(self, matrix: np.ndarray) -> np.ndarray:
        if self._num_qubits == 2:
            if self._ctrl_qubits[0] < self._target_qubits[0]:
                updated_params = np.kron(ZERO_GATE, I_GATE) + np.kron(ONE_GATE, matrix)
            else:
                updated_params = np.kron(I_GATE, ZERO_GATE) + np.kron(matrix, ONE_GATE)
        else:
            control_dim = 2 ** len(self._ctrl_qubits)
            # target_dim = 2 ** len(self._target_qubits)
            matrix_I = np.eye(control_dim)
            updated_params = block_diag(matrix_I, matrix)

        return updated_params

    def reset_qubits(self, new_control_qubits: Union[int, List[int]], new_target_qubits: Union[int, List[int]]) -> 'MCUGate':
        tmp_ctrl_qubits = new_control_qubits if isinstance(new_control_qubits, list) else [new_control_qubits]
        tmp_target_qubits = new_target_qubits if isinstance(new_target_qubits, list) else [new_target_qubits]
        if len(tmp_ctrl_qubits) != len(self._ctrl_qubits) or len(tmp_target_qubits) != len(self._target_qubits):
            raise TgqSimError("重置比特时应该保证控制比特数和目标比特数不变.")
        self._on_qubits = self._get_on_qubits(tmp_ctrl_qubits, tmp_target_qubits)
        self._ctrl_qubits = tmp_ctrl_qubits
        self._target_qubits = tmp_target_qubits
        if self._num_qubits == 2:
            self._params = self._update_params()
        self._data = (self._name, self._on_qubits, self._params)
        # self._matrix = self._to_matrix()
        return self