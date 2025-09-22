import numpy as np
from typing import Union

class TensorUpscaler:
    def __init__(self, original_index: Union[list, np.ndarray], target_index: Union[list, np.ndarray],
                 original_matrix: Union[list, np.ndarray]):
        self.original_index = original_index
        self.target_index = target_index
        self.original_matrix = original_matrix
        self._validate()
        self.mapping = self._build_mapping()

    def _validate(self):
        if not (isinstance(self.original_index, (list, np.ndarray)) and
                isinstance(self.target_index, (list, np.ndarray)) and
                isinstance(self.original_matrix, (list, np.ndarray))):
            raise TypeError("original_index、target_index和original_matrix类型必须是list或者np.ndarray")

        if len(set(self.original_index)) != len(self.original_index) or \
           len(set(self.target_index)) != len(self.target_index):
            raise ValueError("索引中不能包含重复元素")

        if len(self.original_matrix) != 2 ** len(self.original_index):
            print(f"original_index: {self.original_index}, original_matrix: {self.original_matrix}")
            raise ValueError("original_matrix的长度必须等于2**len(original_index)")

        for ele in self.original_index:
            if ele not in self.target_index:
                raise ValueError("target_index必须包含所有original_index里的元素")

    def _build_mapping(self):
        mapping = {}
        for i, ele in enumerate(self.original_matrix):
            key = format(i, f'0{len(self.original_index)}b')
            mapping[key] = ele
        return mapping

    def upscale(self) -> Union[list, np.ndarray]:
        pos_in_target = [self.target_index.index(ele) if isinstance(self.target_index, list)
                         else int(np.where(self.target_index == ele)[0][0])
                         for ele in self.original_index]

        result = []
        for i in range(2 ** len(self.target_index)):
            bin_str = format(i, f'0{len(self.target_index)}b')
            key = ''.join(bin_str[j] for j in pos_in_target)
            result.append(self.mapping[key])

        if isinstance(self.original_matrix, np.ndarray):
            return np.array(result, dtype=np.complex128)
        return result


# Example usage
if __name__ == "__main__":
    upscaler = TensorUpscaler([1, 3, 6,2,4,7], [1, 3, 6,2,4,7, 5],
                              [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33,
                               34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64])
    result = upscaler.upscale()
    print(result)
