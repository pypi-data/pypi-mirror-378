import numpy as np
from itertools import product
from typing import List


def MultiControlled_ActOn_State(psi: np.ndarray,
                                num_qubits: int,
                                matrix: np.ndarray,
                                control_pos: List[int],
                                target_pos: List[int]) -> np.ndarray:
    """
    多控制门执行逻辑：仅当 control_pos 对应 qubit 全为 1 时，对 target_pos 应用 matrix
    :param psi: 原始状态向量
    :param num_qubits: 总 qubit 数
    :param matrix: 要施加的门（形如 2x2 或 4x4）
    :param control_pos: 控制比特索引列表
    :param target_pos: 目标比特索引列表（支持单/双比特门）
    :return: 更新后的 psi
    """

    assert len(target_pos) in (1, 2), "目前仅支持作用于 1 或 2 个目标位"
    dim = 2 ** len(target_pos)
    assert matrix.shape == (dim, dim), f"目标门矩阵维度应为 {dim}x{dim}"

    # 控制比特掩码，用于 (i & control_mask) == control_mask 判断控制条件
    control_mask = sum([1 << c for c in control_pos])

    # 目标比特位：按升序排列，用于构造 i0/i1/...
    sorted_targets = sorted(target_pos)
    base_shifts = [1 << t for t in sorted_targets]  # 例如 [2, 8] 表示 q1 和 q3
    basis_offset_list = []
    for bits in product([0, 1], repeat=len(sorted_targets)):
        offset = sum(b << s for b, s in zip(bits, base_shifts))
        basis_offset_list.append(offset)

    # 生成所有需要扫描的基础索引块
    for i in range(2 ** num_qubits):
        # 判断当前 basis 状态是否满足控制条件
        if (i & control_mask) != control_mask:
            continue

        # 获取子态索引
        base_index = i
        for t in target_pos:
            base_index &= ~(1 << t)  # 抹掉目标位

        indices = [base_index + offset for offset in basis_offset_list]
        amps = np.array([psi[j] for j in indices])
        new_amps = matrix @ amps
        for j, val in zip(indices, new_amps):
            psi[j] = val

    return psi
