from noise_models_v2 import *
from typing import Union

def parse_noise(noise_type: str, gate_pos: int, error_rate: Union[float, list]):
    """
    根据噪声类型与错误率生成噪声门。
    返回格式: (gate_pos, (gate_name,))
    若未触发噪声则返回 None
    """
    if noise_type == "bit_flip":
        gate = bit_flip(error_rate)
    elif noise_type == "asymmetric_depolarization":
        gate = asymmetric_depolarization(error_rate)
    elif noise_type == "depolarize":
        gate = depolarize(error_rate)
    elif noise_type == "phase_flip":
        gate = phase_flip(error_rate)
    elif noise_type == "phase_damp":
        gate = phase_damp(error_rate)
    elif noise_type == "amplitude_damp":
        gate = amplitude_damp(error_rate)
    else:
        raise ValueError(f"Unsupported noise type: {noise_type}")

    if gate is None:
        return None
    return (gate_pos, (gate,))
