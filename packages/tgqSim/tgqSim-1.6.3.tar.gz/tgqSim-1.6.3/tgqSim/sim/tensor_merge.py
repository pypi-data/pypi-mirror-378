import numpy as np

def fuse_edges(edge1: dict, edge2: dict) -> dict:
    """
    融合两个边，要求它们的阶数相同、顶点顺序一致，对应张量元素点乘。

    Args:
        edge1 (dict): 边1，包含 'vertices' 和 'tensor'。
        edge2 (dict): 边2，结构与边1相同。

    Raises:
        ValueError: 若两边阶数不同或顶点顺序不同。
        TypeError: 若tensor不是np.ndarray类型。

    Returns:
        dict: 融合后的新边（vertices不变，tensor为点乘结果）。
    """
    # 顶点序列必须一致
    if edge1["vertices"] != edge2["vertices"]:
        raise ValueError("两个边的顶点顺序不一致，无法融合")

    tensor1 = edge1["tensor"]
    tensor2 = edge2["tensor"]

    # 类型检查
    if not isinstance(tensor1, np.ndarray) or not isinstance(tensor2, np.ndarray):
        raise TypeError("边的 tensor 必须为 numpy.ndarray 类型")

    # 阶数检查
    if tensor1.shape != tensor2.shape:
        raise ValueError(f"两个边的张量阶数不同，tensor1.shape={tensor1.shape}, tensor2.shape={tensor2.shape}")

    # 融合：逐元素点乘
    fused_tensor = tensor1 * tensor2

    return {
        "vertices": edge1["vertices"],
        "tensor": fused_tensor
    }


if __name__ == "__main__":
    edge1 = {
        "vertices": [(0, 0), (1, 0)],
        "tensor": np.array([1, 2, 3, 4])
    }
    edge2 = {
        "vertices": [(0, 0), (1, 0)],
        "tensor": np.array([10, 20, 30, 40])
    }

    fused = fuse_edges(edge1, edge2)
    print(fused)
    # 输出: {'vertices': [(0, 0), (1, 0)], 'tensor': array([10, 40, 90, 160])}
