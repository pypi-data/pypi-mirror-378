from tgqSim.circuit import QuantumCircuit

import numpy as np
from typing import List

def run_with_gpu_device(circuit: QuantumCircuit, gpuId: List[int]) -> np.ndarray:...