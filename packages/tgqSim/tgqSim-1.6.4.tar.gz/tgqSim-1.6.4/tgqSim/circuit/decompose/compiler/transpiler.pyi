from typing import List, Union, Optional, Tuple, Dict
import numpy as np

from tgqSim.circuit.quantum_circuit import QuantumCircuit
from tgqSim.circuit.decompose.decompositon_methods import DecompositionMethod

def transpile(
        circuit: QuantumCircuit,
        basis_single_qubit_gate: List[str] = ['rz', 'sx'],
        basis_double_qubit_gate: List[str] = ['cx'],
        unitary_decomposition_used_double_qubit_gate: List[str] = ['cx'],
        decomposition_method: DecompositionMethod = DecompositionMethod.SHANNON,
        single_qubit_gate_reduction_level: int = 1,
        double_qubit_gate_reduction_method: str = 'all',
        backend: str = None,
        chip_topology: Union[np.ndarray, List[List[int]]] = None,
        starting_physical_qubit_num: Optional[int] = None,  # 不能超过线路的总比特数
        physical_qubit_fidelity: Optional[List[float]] = None,
        **kwargs
        ) -> Tuple[QuantumCircuit, List[int], Dict[int, int]]:...