# schedule
from typing import List, Union, Dict

from tgqSim.circuit.quantum_circuit import QuantumCircuit
from tgqSim.gate.instruction import Instruction


def schedule(
        circuit: Union[QuantumCircuit, List[Instruction]],
        duration: Dict[str, float] = {'rz': 0.0, 'sx': 20.0, 'cz': 60.0, 'cx': 60.0, 'iswap': 60.0},
        method: str = 'schedule_with_layer',
        ) -> Dict[int, List[List[Instruction]]]:...