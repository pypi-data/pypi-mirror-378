from typing import List, Dict, Tuple, Union
import itertools

class EdgeReducer:
    def __init__(self, vertices: List[int], tensor: List[Union[float, complex]]):
        self.vertices = vertices
        self.rank = len(vertices)
        assert len(tensor) == 2 ** self.rank, "Tensor length must match 2^len(vertices)"
        self.tensor = tensor
        self.original_bin_map = self._build_bin_map()

    def _build_bin_map(self) -> Dict[str, Union[float, complex]]:
        bin_map = {}
        for idx in range(2 ** self.rank):
            bin_key = format(idx, f'0{self.rank}b')
            bin_map[bin_key] = self.tensor[idx]
        return bin_map

    def fixed_value_reduce(self, fixed_vertex_values: Dict[int, int]) -> Tuple[List[int], List[Union[float, complex]], Dict[str, Union[float, complex]]]:
        """
        确定值降阶：只移除固定值的顶点，其它顶点保留。
        :param fixed_vertex_values: 如 {3: 1}
        :return: (保留顶点, 降阶后张量, 二进制映射)
        """
        # 保留下来的顶点和对应索引
        keep_indices = [i for i, v in enumerate(self.vertices) if v not in fixed_vertex_values]
        keep_vertices = [self.vertices[i] for i in keep_indices]
        fixed_indices = {i: fixed_vertex_values[v] for i, v in enumerate(self.vertices) if v in fixed_vertex_values}

        reduced_tensor = []
        reduced_bin_map = {}

        import itertools
        for bits in itertools.product("01", repeat=len(keep_indices)):
            full_key = ['0'] * self.rank
            for ki, bi in zip(keep_indices, bits):
                full_key[ki] = bi
            for fi, val in fixed_indices.items():
                full_key[fi] = str(val)
            full_key_str = "".join(full_key)
            val = self.original_bin_map[full_key_str]
            reduced_tensor.append(val)
            reduced_bin_map["".join(bits)] = val

        return keep_vertices, reduced_tensor, reduced_bin_map

    def reduce(self, remove_vertices: List) -> Tuple[
        List[int], List[Union[float, complex]], Dict[str, Union[float, complex]]]:
        keep_indices = [i for i, v in enumerate(self.vertices) if v not in remove_vertices]
        remove_indices = [i for i, v in enumerate(self.vertices) if v in remove_vertices]
        keep_vertices = [self.vertices[i] for i in keep_indices]

        reduced_tensor = []
        reduced_bin_map = {}

        for bits in itertools.product("01", repeat=len(keep_indices)):
            sum_val = 0.0
            for rem_bits in itertools.product("01", repeat=len(remove_indices)):
                full_key = ['0'] * self.rank
                for ki, bi in zip(keep_indices, bits):
                    full_key[ki] = bi
                for ri, rb in zip(remove_indices, rem_bits):
                    full_key[ri] = rb
                full_key_str = "".join(full_key)
                sum_val += self.original_bin_map[full_key_str]
            key_str = "".join(bits)
            reduced_tensor.append(sum_val)
            reduced_bin_map[key_str] = sum_val

        return keep_vertices, reduced_tensor, reduced_bin_map

if __name__ == "__main__":
    import numpy as np
    # # 测试示例：Edge(1,2,3)，仅移除顶点3（值为1），不移除其他非确定顶点
    # vertices = [1, 2, 3]
    # tensor = [5, 6, 14, 16, 15, 18, 28, 32]
    # reducer = EdgeReducer(vertices, tensor)

    # 仅做确定值降阶（3 已知为 1）
    # keep_vertices, reduced_tensor, reduced_map = reducer.fixed_value_reduce(fixed_vertex_values={2:0})
    # print(keep_vertices, reduced_tensor, reduced_map)

    vertices = [1, 2, 3, 4]
    tensor = [1/np.sqrt(2), 0, 0, 1 / np.sqrt(2), 0, 0, 0, 0, 1/np.sqrt(2), 0, 0, 1 / np.sqrt(2), 0, 0, 0, 0]
    reducer = EdgeReducer(vertices, tensor)
    keep_vertices, reduced_tensor, reduced_map = reducer.reduce([2])
    print(keep_vertices, reduced_tensor, reduced_map)
