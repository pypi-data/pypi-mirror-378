from tgqSim.circuit import QuantumCircuit

from typing import List
import numpy as np  

def run_with_dcu_device(circuit: QuantumCircuit, dcuId: List[int]) -> np.ndarray: ...