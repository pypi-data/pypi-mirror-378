import time
import numpy as np
from collections import defaultdict
from build_tensor_from_gates_v3 import UndirectedTensorGraph, TensorEdge
from tensor_downscale import EdgeReducer
from tensor_upscale_v2 import TensorUpscaler
from tensor_merge import  fuse_edges


class TensorGraphScheduler:
    def __init__(self, graph: UndirectedTensorGraph):
        self.graph = graph
        self.edge_id_map = {e.id: e for e in graph.tensor_edges}

    def run(self):
        print("\n▶ 开始执行 fixed value 降阶阶段")
        self._fixed_value_reduce_all()
        print("\n▶ 开始执行边融合调度")
        self._fuse_edges_recursive()
        return self.graph.tensor_edges

    def _fixed_value_reduce_all(self):
        for edge in self.graph.tensor_edges:
            all_vertices = edge.input_vertices + edge.output_vertices
            index = list(range(len(all_vertices)))
            fixed = {
                i: self.graph.boundary_vertex_state[v]
                for i, v in enumerate(all_vertices)
                if v in self.graph.boundary_vertex_state
            }

            if not fixed:
                edge.vertex_index_order = all_vertices
                continue

            print(f"\n[固定值降阶] Edge {edge.id}；这条边的张量矩阵：{edge.tensor}")
            print(f"  原始顶点: {all_vertices}")
            fixed_readable = {all_vertices[i]: val for i, val in fixed.items()}
            print(f"  固定点位: {fixed_readable}")

            reducer = EdgeReducer(index, edge.tensor)
            new_index, new_tensor, _ = reducer.fixed_value_reduce(fixed)
            new_vertices = [all_vertices[i] for i in new_index]
            print(f"  降阶后顶点: {new_vertices}, 新张量大小: {len(new_tensor)}；新的张量矩阵：{new_tensor}")

            n_input = len(edge.input_vertices)
            new_inputs = [all_vertices[i] for i in new_index if i < n_input]
            new_outputs = [all_vertices[i] for i in new_index if i >= n_input]

            # edge.update_tensor_without_refreshing(new_tensor, len(new_index))
            # edge.update_vertices_without_refreshing(new_inputs, new_outputs)
            edge.vertex_index_order = new_vertices


    def _try_local_downscale_before_fusion(self, edge1: TensorEdge, edge2: TensorEdge, threshold: int):
        """
        在融合 edge1 和 edge2 之前尝试对它们的共享顶点进行局部降阶。
        如果两条边的顶点总数超过阈值 threshold，则对共享顶点执行降阶。
        该操作不会改变原有边的 ID。
        """
        # 计算两条边的总顶点数量
        total_vertices = len(
            set(edge1.input_vertices + edge1.output_vertices + edge2.input_vertices + edge2.output_vertices))
        print(f"\n[降阶检测] Edge1 ID: {edge1.id}，Edge2 ID: {edge2.id}")
        print(
            f"  Edge1 顶点数：{len(edge1.input_vertices + edge1.output_vertices)}，Edge2 顶点数：{len(edge2.input_vertices + edge2.output_vertices)}，总计：{total_vertices}，阈值：{threshold}")

        # 找到共享顶点集合
        shared_vertices = set(edge1.input_vertices + edge1.output_vertices) & set(
            edge2.input_vertices + edge2.output_vertices)

        if total_vertices <= threshold and shared_vertices:
            print("  ⏩ 未超过阈值，不进行降阶")
            # 未超过阈值，不进行任何降阶
            return False

        if not shared_vertices:
            # 没有共享顶点，无法进行局部降阶
            print("  ⏩ 没有共享顶点，无法进行降阶")
            return True

        # 将共享顶点集合转换为列表，供 EdgeReducer 使用
        shared_list = list(shared_vertices)

        # 分别对 edge1 和 edge2 执行降阶
        for edge in (edge1, edge2):
            # 使用 EdgeReducer 对当前边的张量沿共享顶点进行降阶（求和消除这些维度）
            print(f"\n  ➤ 降阶前 Edge {edge.id}，顶点：{edge.input_vertices + edge.output_vertices}， 张量：{edge.tensor}")
            reducer = EdgeReducer(edge.input_vertices + edge.output_vertices, edge.tensor)
            print(f"\n  ➤ 降阶降掉的顶点：{shared_list}")
            new_vertices, new_tensor, _ = reducer.reduce(shared_list)
            print(f"  ➤ 降阶后顶点：{new_vertices}，新张量：{new_tensor}, binmap: {_}")
            # todo 要调整一下顺序
            sorted_indices = [v for v in new_vertices if v in edge.input_vertices] + [v for  v in new_vertices if v in edge.output_vertices]
            new_tensor = self._rearrange_tensor_order(new_vertices, new_tensor, sorted_indices)
            print(f"\n  ➤ 降阶后 Edge {edge.id}，新顶点：{new_vertices}")
            # 根据原始输入/输出顶点列表划分新的顶点列表
            original_input_set = set(edge.input_vertices)
            original_output_set = set(edge.output_vertices)
            print(f"  原始输入顶点集合：{original_input_set}；原始输出顶点集合：{original_output_set}")
            new_input_vertices = [v for v in new_vertices if v in original_input_set]
            new_output_vertices = [v for v in new_vertices if v in original_output_set]
            print(f"  新输入顶点集合：{new_input_vertices}；新输出顶点集合：{new_output_vertices}")
            # 更新当前边的顶点列表和张量，而不刷新 ID（保持边 ID 不变）
            edge.update_vertices_without_refreshing(new_input_vertices, new_output_vertices)
            edge.update_tensor_without_refreshing(new_tensor, len(new_vertices))

            print(f"  ✅ 降阶后 Edge {edge.id}，新顶点：{edge.input_vertices + edge.output_vertices}")
            print(f"  ✅ 新张量：{new_tensor}")
            print(f"  ✅ 新张量长度：{len(new_tensor)}")
        return True

    def _fuse_edges_recursive(self):
        round_num = 0
        while True:
            round_num += 1
            print(f"\n▶ 融合调度第 {round_num} 轮")
            pairs = self._find_all_fusable_pairs()
            # pair_list = self._find_all_fusable_pairs()
            if not pairs:
                print("\n✅ 所有可融合边已处理完毕，图结构收敛")
                break

            visited_ids = set()
            # 因为每次只融合一对，这里直接取第一对
            # edge1, edge2 = pair_list[0]
            for edge1, edge2 in pairs:
                if edge1.id not in self.edge_id_map or edge2.id not in self.edge_id_map:
                    continue
                if (edge1.id, edge2.id) in visited_ids or (edge2.id, edge1.id) in visited_ids:
                    continue
                # # 尝试局部降阶
                # todo 还要再论证一下这个局部降阶的逻辑
                # processed = self._try_local_downscale_before_fusion(edge1, edge2, threshold=10)
                # if processed:
                #     print(f"✅ 边 {edge1.id} 和 {edge2.id} 已降阶，跳过融合")
                #     visited_ids.add((edge1.id, edge2.id))
                #     continue
                # print(f"🔄 边 {edge1.id} 和 {edge2.id} 未降阶，继续进行融合")
                self._fuse_pair(edge1, edge2)
                visited_ids.add((edge1.id, edge2.id))
            # if edge1.id not in self.edge_id_map or edge2.id not in self.edge_id_map:
            #     continue  # 如果其中任何一条边已经不在了（被融合过），跳过本轮
            # self._fuse_pair(edge1, edge2)
        if len(self.graph.tensor_edges) != 1:
            print(f"⚠️ 模拟未收敛！剩余张量边数: {len(self.graph.tensor_edges)}")
            for edge in self.graph.tensor_edges:
                print(f"  ➤ Edge {edge.id}: input={edge.input_vertices}, output={edge.output_vertices}, len={len(edge.tensor)}")

    def _find_all_fusable_pairs(self):
        pairs = []
        # 将当前边按 moment_no 从小到大排序（None 当作无限大处理）。
        # edge_list = sorted(self.edge_id_map.values(),
        #                    key=lambda e: e.moment_no if e.moment_no is not None else float('inf'))
        # 遍历排序后的边列表，寻找第一对共享顶点的边
        edge_list = list(self.edge_id_map.values())
        for i in range(len(edge_list)):
            # e1 = edge_list[i]
            for j in range(i + 1, len(edge_list)):
                e1, e2 = edge_list[i], edge_list[j]
                # e2 = edge_list[j]
                shared = set(e1.input_vertices + e1.output_vertices) & set(e2.input_vertices + e2.output_vertices)
                if shared:
                    pairs.append((e1, e2))
                print(f"  边 {e1.id} 和边 {e2.id} 的共享顶点: {shared}")
        return pairs

    @staticmethod
    def _rearrange_tensor_order(new_index, new_tensor, sorted_index):
        """
        Reorder the reduced tensor according to the input and output order of the edges. 用于调整降阶后的张量矩阵顺序
        Args:
        new_index (list or np.ndarray): The reduced index of the tensor.
        new_tensor (list): The reduced tensor values.
        sorted_index (list): The desired sorted order of tensor indices.
        Returns:
            list: The reordered tensor values.
        """
        # todo: 把newtensor按照new edge的input+output顺序重排
        sorted_mapping = {}
        sorted_tensor = new_tensor.copy()
        print("  new_index:", new_index, "sorted_index:", sorted_index)
        if len(new_index) > 0:
            # 寻找位置
            pos_in_new_index = []
            for ele in sorted_index:
                if ele in new_index:
                    if isinstance(new_index, np.ndarray):
                        pos_in_new_index.append(int(np.where(new_index == ele)[0][0]))
                    else:
                        pos_in_new_index.append(new_index.index(ele))
                else:
                    raise ValueError("left_index包含所有的right_index的元素")
            # 组建mapping
            for i, ele in enumerate(new_tensor):
                index_bin = format(i, f'0{len(new_index)}b')
                index_bin_new = "".join([index_bin[i] for i in pos_in_new_index])
                sorted_mapping[index_bin_new] = ele

            for i in range(2 ** len(sorted_index)):
                i_binary = format(i, f'0{len(sorted_index)}b')
                # index_bin = "".join([i_binary[i] for i in pos_in_new_index])
                sorted_tensor[i] = sorted_mapping[i_binary]
        return sorted_tensor


    def _fuse_pair(self, edge1: TensorEdge, edge2: TensorEdge):
        print(f"\n[边融合] 正在融合 {edge1.id} + {edge2.id}")
        v1_actual = edge1.input_vertices + edge1.output_vertices
        v2_actual = edge2.input_vertices + edge2.output_vertices
        v_union = list(dict.fromkeys(v1_actual + v2_actual))
        shared = list(set(v1_actual) & set(v2_actual))

        # 检查shared点在edge1和edge2中的分别在input还是output，如果在某条边的input中，那么这条边应该是边二，因为它在融合的右侧
        # 确保融合时的正确顺序：左侧边在前
        # todo 这里可能不能用any，而是去看最左的点，最左的概念可以看这个点横跨的两个边的moment，哪个moment早哪个就是最左的点；那么最左的点在谁的output谁就是边1
        # 使用 vertex_moment_map 确定共享顶点中最左的
        min_moment = float('inf')
        leftmost_vertex = None

        for vertex in shared:
            if vertex in self.graph.vertex_moment_map:
                moments = self.graph.vertex_moment_map[vertex]
                left_moment = moments[0] if moments[0] is not None else float('inf')
                right_moment = moments[1] if moments[1] is not None else float('inf')

                # 找到 moment 更小的那个
                if left_moment < right_moment and left_moment < min_moment:
                    min_moment = left_moment
                    leftmost_vertex = vertex
                elif right_moment < left_moment and right_moment < min_moment:
                    min_moment = right_moment
                    leftmost_vertex = vertex

        print(f"  共享顶点：{shared}；最左顶点：{leftmost_vertex}；moment：{min_moment}")
        # 根据最左顶点判断顺序
        if leftmost_vertex:
            if leftmost_vertex in edge2.output_vertices:
                edge1, edge2 = edge2, edge1
            # moments = self.graph.vertex_moment_map[leftmost_vertex]
            # print(f"  最左顶点的moment：{moments}")
            # if moments[0] is not None and moments[1] is not None:
            #     if moments[0] < moments[1]:
            #         # 最左顶点在左侧边的输出中
            #         if leftmost_vertex in edge2.input_vertices:
            #             edge1, edge2 = edge2, edge1
            #     else:
            #         # 最左顶点在右侧边的输入中
            #         if leftmost_vertex in edge1.input_vertices:
            #             edge1, edge2 = edge2, edge1
            # elif moments[0] is not None and moments[1] is None:
            #     # 仅有左侧 moment，说明这个顶点是左边的输出
            #     if leftmost_vertex in edge2.input_vertices:
            #         edge1, edge2 = edge2, edge1
            # elif moments[1] is not None and moments[0] is None:
            #     # 仅有右侧 moment，说明这个顶点是右边的输入
            #     if leftmost_vertex in edge1.input_vertices:
            #         edge1, edge2 = edge2, edge1
        # if edge1.moment_no <= edge2.moment_no:
        #     pass
        # else:
        #     edge1, edge2 = edge2, edge1
        print(f"  边1融合前的顶点集合：input: {edge1.input_vertices} output: {edge1.output_vertices}；边1的moment序号： {edge1.moment_no}")
        print(f"  边2融合前的顶点集合：input: {edge2.input_vertices} output: {edge2.output_vertices}；边2的moment序号： {edge2.moment_no}")

        map1 = [v_union.index(v) for v in v1_actual]
        map2 = [v_union.index(v) for v in v2_actual]
        # target_index = list(range(len(v_union)))
        target_index = v_union.copy()
        print(f"  目标索引：{target_index}；边1的映射：{v1_actual}；边2的映射：{v2_actual}；共享顶点集合：{shared}")

        up1 = TensorUpscaler(edge1.input_vertices + edge1.output_vertices, target_index, edge1.tensor).upscale()
        up2 = TensorUpscaler(edge2.input_vertices + edge2.output_vertices, target_index, edge2.tensor).upscale()

        #######
        print(f"  升阶后 up1 shape: {np.shape(up1)}, 升阶后的矩阵：{up1}")
        print(f"  升阶后 up2 shape: {np.shape(up1)}, 升阶后的矩阵：{up2}")

        edge_up_1 = {"vertices": v_union, "tensor": np.array(up1)}
        edge_up_2 = {"vertices": v_union, "tensor": np.array(up2)}
        fused = fuse_edges(edge_up_1, edge_up_2)
        # fused = fuse_edges(target_index, up1, , edge_up_2)
        ##########

        # if len(shared) == len(v_union) or len(shared) == 0:
        if len(shared) == 0:
            new_tensor = fused["tensor"].tolist()
            new_index = v_union
        else:
            print(f"  待降阶的顶点集合：{v_union}；待降阶的张量矩阵：{fused['tensor'].tolist()}; 待去掉的顶点集合：{shared}")
            reducer = EdgeReducer(v_union, fused["tensor"].tolist())
            new_index, new_tensor, _ = reducer.reduce(shared)
            print(f"  降阶后顶点集合：{new_index}；降阶后张量矩阵：{new_tensor}; 降阶后去掉的顶点集合：{_}")
        # # todo: 把newtensor按照new edge的input+output顺序重排
        sorted_index = [v for v in new_index if v in edge1.input_vertices or v in edge2.input_vertices] + [v for v in new_index if v in edge1.output_vertices or v in edge2.output_vertices]
        sorted_tensor = self._rearrange_tensor_order(new_index, new_tensor, sorted_index)
        # todo: 把newtensor按照new edge的input+output顺序重排
        # sorted_index = [v for v in new_index if v in edge1.input_vertices or v in edge2.input_vertices] + [v for v in new_index if v in edge1.output_vertices or v in edge2.output_vertices]
        # sorted_mapping = {}
        # sorted_tensor = new_tensor.copy()  # 先复制一份，后续会根据mapping进行重排
        # print("  new_index:", new_index, "sorted_index:", sorted_index)
        # if len(new_index) > 0:
        #     # 寻找位置
        #     pos_in_new_index = []
        #     for ele in sorted_index:
        #         if ele in new_index:
        #             if isinstance(new_index, np.ndarray):
        #                 pos_in_new_index.append(int(np.where(new_index == ele)[0][0]))
        #             else:
        #                 pos_in_new_index.append(new_index.index(ele))
        #         else:
        #             raise ValueError("left_index包含所有的right_index的元素")
        #     # 组建mapping
        #     for i, ele in enumerate(new_tensor):
        #         index_bin = format(i, f'0{len(new_index)}b')
        #         index_bin_new = "".join([index_bin[i] for i in pos_in_new_index])
        #         sorted_mapping[index_bin_new] = ele
        #
        #     for i in range(2 ** len(sorted_index)):
        #         i_binary = format(i, f'0{len(sorted_index)}b')
        #         # index_bin = "".join([i_binary[i] for i in pos_in_new_index])
        #         sorted_tensor[i] = sorted_mapping[i_binary]

        new_edge = TensorEdge(
            input_vertices=[v for v in new_index if v in edge1.input_vertices or v in edge2.input_vertices],
            output_vertices=[v for v in new_index if v in edge1.output_vertices or v in edge2.output_vertices],
            tensor=sorted_tensor,
            rank=len(new_index),
            moment_no=min(edge1.moment_no, edge2.moment_no)
        )
        print(f"  融合后id: {new_edge.id}；新的张量矩阵：{sorted_tensor};新的顶点集合：{new_edge.input_vertices + new_edge.output_vertices}")
        self.graph.tensor_edges.append(new_edge)
        self.edge_id_map[new_edge.id] = new_edge

        self.graph.tensor_edges = [e for e in self.graph.tensor_edges if e.id not in [edge1.id, edge2.id]]
        del self.edge_id_map[edge1.id]
        del self.edge_id_map[edge2.id]


    def compute_amplitude_from_tensor_graph(self):
        result = 1.0 + 0j
        print("\n[最终振幅计算] 正在累乘所有张量:")
        for edge in self.graph.tensor_edges:
            print(f"Edge {edge.id}: vertices = {edge.input_vertices} → {edge.output_vertices}, tensor = {edge.tensor}")
            if isinstance(edge.tensor, list):
                value = edge.tensor[0]
            elif hasattr(edge.tensor, 'shape'):
                value = edge.tensor.item() if edge.tensor.size == 1 else edge.tensor[0]
            else:
                value = edge.tensor
            print(f"  使用值: {value}")
            result *= value
        print(f"\n🎯 最终路径振幅 = {result}")
        return result

    def summary(self):
        print("\n📌 当前张量边结构：")
        for edge in self.graph.tensor_edges:
            print(f"Edge {edge.id}: {edge.input_vertices} -> {edge.output_vertices}, "
                  f"rank={edge.rank}, len={len(edge.tensor)}, tensor={edge.tensor}")