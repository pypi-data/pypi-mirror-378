import random
from typing import Union

class NoiseModel:
    """抽象噪声模型类"""
    def noisy_operation(self, gate):
        return [gate]

# todo 所有比特上都加噪声，目前是只在该门作用的第0号比特上加噪声
class DepolarizingNoiseModel(NoiseModel):
    def __init__(self, error_rate: float):
        self.error_rate = error_rate

    def noisy_operation(self, gate):
        from gate.single_gate import X, Y, Z
        from random import random, choice
        if random() < self.error_rate:
            noise_gate = choice([X, Y, Z])
            return [gate, noise_gate(gate.on_qubits[0])]
        return [gate]

class BitFlipNoiseModel(NoiseModel):
    def __init__(self, error_rate: float):
        self.error_rate = error_rate

    def noisy_operation(self, gate):
        from gate.single_gate import X
        if random.random() < self.error_rate:
            return [gate, X(gate.on_qubits[0])]
        return [gate]

class PhaseFlipNoiseModel(NoiseModel):
    def __init__(self, error_rate: float):
        self.error_rate = error_rate

    def noisy_operation(self, gate):
        from gate.single_gate import Z
        if random.random() < self.error_rate:
            return [gate, Z(gate.on_qubits[0])]
        return [gate]

class AsymmetricDepolarizingNoiseModel(NoiseModel):
    def __init__(self, error_rates: Union[list, tuple]):
        if len(error_rates) != 3:
            raise ValueError("Length of error_rates must be 3")
        self.error_rates = error_rates

    def noisy_operation(self, gate):
        from gate.single_gate import X, Y, Z
        rand = random.random()
        if rand < self.error_rates[0]:
            return [gate, X(gate.on_qubits[0])]
        elif rand < sum(self.error_rates[:2]):
            return [gate, Y(gate.on_qubits[0])]
        elif rand < sum(self.error_rates):
            return [gate, Z(gate.on_qubits[0])]
        return [gate]

class AmplitudeDampingNoiseModel(NoiseModel):
    def __init__(self, error_rate: float):
        self.error_rate = error_rate

    def noisy_operation(self, gate):
        # placeholder for amplitude damping
        from gate.single_gate import X
        if random.random() < self.error_rate:
            return [gate, X(gate.on_qubits[0])]
        return [gate]

class PhaseDampingNoiseModel(NoiseModel):
    def __init__(self, error_rate: float):
        self.error_rate = error_rate

    def noisy_operation(self, gate):
        # placeholder for phase damping
        from gate.single_gate import Z
        if random.random() < self.error_rate:
            return [gate, Z(gate.on_qubits[0])]
        return [gate]