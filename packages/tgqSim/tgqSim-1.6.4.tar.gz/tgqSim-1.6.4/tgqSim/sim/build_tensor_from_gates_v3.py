import numpy as np
import networkx as nx
import hashlib
from typing import Any, Dict, List, Tuple

from tgqSim.circuit.quantum_circuit_v3 import QuantumCircuit


# 不基于cirq
class QubitKey:
    def __init__(self, label: Any, order: int = 0):
        self.label = label
        self.order = order

    def __hash__(self):
        return hash(self.label)

    def __eq__(self, other):
        return isinstance(other, QubitKey) and self.label == other.label

    def __lt__(self, other):
        return self.order < other.order

    def __repr__(self):
        return f"QubitKey({self.label})"


class TensorEdge:
    def __init__(self,
                 input_vertices: List[Tuple[QubitKey, int]],
                 output_vertices: List[Tuple[QubitKey, int]],
                 tensor: List[complex],
                 rank: int):
        self.input_vertices = input_vertices
        self.output_vertices = output_vertices
        self.tensor = tensor
        self.rank = rank

        self.before_ids = []
        self.after_ids = []
        self.id = self._generate_id()

    def _generate_id(self) -> str:
        content = str(self.input_vertices + self.output_vertices + self.tensor)
        return hashlib.sha256(content.encode()).hexdigest()[:8]  # 保留前8位

    def update_vertices(self,
                        new_input: List[Tuple[QubitKey, int]] = None,
                        new_output: List[Tuple[QubitKey, int]] = None):
        if new_input is not None:
            self.input_vertices = new_input
        if new_output is not None:
            self.output_vertices = new_output
        self._refresh_id()

    def update_tensor(self, new_tensor: List[complex], new_rank: int):
        self.tensor = new_tensor
        self.rank = new_rank
        self._refresh_id()

    def _refresh_id(self):
        self.id = self._generate_id()

    def merge_with(self, other: 'TensorEdge'):
        all_in = list(set(self.input_vertices + other.input_vertices))
        all_out = list(set(self.output_vertices + other.output_vertices))
        new_tensor = self.tensor + other.tensor  # 简化逻辑
        new_rank = len(all_in) + len(all_out)
        self.update_vertices(all_in, all_out)
        self.update_tensor(new_tensor, new_rank)


class UndirectedTensorGraph:
    def __init__(self):
        self.graph = nx.Graph()
        self.tensor_edges: List[TensorEdge] = []
        self.vertices = set()
        self.init_state: Dict[QubitKey, int] = {}
        self.final_state: Dict[QubitKey, int] = {}
        self.boundary_vertex_state: Dict[Tuple[QubitKey, int], int] = {}

    def add_vertex(self, vertex: Tuple[QubitKey, int]):
        self.graph.add_node(vertex)
        self.vertices.add(vertex)
        return vertex

    def add_tensor_edge_split(self, input_vertices, output_vertices, matrix: np.ndarray):
        all_vertices = input_vertices + output_vertices
        rank = len(all_vertices)
        tensor = matrix.flatten(order='F').tolist()
        edge = TensorEdge(input_vertices, output_vertices, tensor, rank)
        self.tensor_edges.append(edge)

        for i in range(len(all_vertices)):
            for j in range(i + 1, len(all_vertices)):
                self.graph.add_edge(all_vertices[i], all_vertices[j])

    def set_init_state(self, q: QubitKey, value: int):
        assert value in (0, 1), "初始态必须为0或1"
        self.init_state[q] = value

    def set_final_state(self, q: QubitKey, value: int):
        assert value in (0, 1), "末态必须为0或1"
        self.final_state[q] = value

    def mark_boundary_vertex_states(self):
        self.boundary_vertex_state = {}

        for q in self.init_state:
            init_vertex = (q, 0)
            self.boundary_vertex_state[init_vertex] = self.init_state[q]

        for q in self.final_state:
            final_index = max(v[1] for v in self.vertices if v[0] == q)
            final_vertex = (q, final_index)
            self.boundary_vertex_state[final_vertex] = self.final_state[q]

    def build_edge_connections(self):
        for edge in self.tensor_edges:
            edge.before_ids = []
            edge.after_ids = []

        n = len(self.tensor_edges)
        for i in range(n):
            ei = self.tensor_edges[i]
            out_i = set(ei.output_vertices)
            for j in range(n):
                if i == j:
                    continue
                ej = self.tensor_edges[j]
                in_j = set(ej.input_vertices)
                if out_i & in_j:
                    ei.after_ids.append(ej.id)
                    ej.before_ids.append(ei.id)

    def get_topological_order(self) -> List[TensorEdge]:
        edge_dependency_graph = nx.DiGraph()
        for edge in self.tensor_edges:
            edge_dependency_graph.add_node(edge.id)

        for edge_a in self.tensor_edges:
            out_a = set(edge_a.output_vertices)
            for edge_b in self.tensor_edges:
                if edge_a == edge_b:
                    continue
                in_b = set(edge_b.input_vertices)
                if out_a & in_b:
                    edge_dependency_graph.add_edge(edge_a.id, edge_b.id)

        try:
            sorted_ids = list(nx.topological_sort(edge_dependency_graph))
        except nx.NetworkXUnfeasible:
            raise RuntimeError("图中存在环，无法拓扑排序")

        id_to_edge = {edge.id: edge for edge in self.tensor_edges}
        return [id_to_edge[eid] for eid in sorted_ids]

    def summary(self):
        bvs = self.boundary_vertex_state
        return {
            "num_vertices": len(self.vertices),
            "vertices": [(str(v[0].label), v[1]) for v in sorted(self.vertices, key=lambda x: (x[0].order, x[1]))],
            "num_tensor_edges": len(self.tensor_edges),
            "tensor_edges": [ {
                    "id": edge.id,
                    "vertices": [
                        sorted([(str(v[0].label), v[1]) for v in edge.input_vertices], key=lambda x: x[0]),
                        sorted([(str(v[0].label), v[1]) for v in edge.output_vertices], key=lambda x: x[0])
                    ],
                    "rank": edge.rank,
                    "tensor": edge.tensor,
                    "before": edge.before_ids,
                    "after": edge.after_ids,
                    "vertex_state": {f"({str(v[0].label)},{v[1]})": bvs[v]
                                     for v in edge.input_vertices + edge.output_vertices
                                     if v in bvs}
                } for edge in self.tensor_edges
            ]
        }


# 示例构建器：兼容 QuantumCircuit_v3，构建张量图
def build_from_tgq_circuit(circuit: QuantumCircuit) -> UndirectedTensorGraph:
    """
    将 QuantumCircuitV3 转换为 UndirectedTensorGraph 图结构（支持 moment 和 int 型 qubit）。
    """
    tg = UndirectedTensorGraph()

    # 构造 qubit -> QubitKey 映射
    all_qubits = list(range(circuit.num_qubits))
    qmap: Dict[int, QubitKey] = {q: QubitKey(label=q, order=q) for q in all_qubits}

    # 顶点映射 vmap：每个 QubitKey 对应一组顶点，记录其历史（不同深度）
    vmap: Dict[QubitKey, List[Tuple[QubitKey, int]]] = {}
    for q in all_qubits:
        qk = qmap[q]
        v0 = (qk, 0)
        tg.add_vertex(v0)
        vmap[qk] = [v0]

    # 遍历 circuit 中的 moment 结构
    for moment in circuit.moments:
        gates = list(moment)
        # 确保按 qubit 索引稳定排序
        gates.sort(key=lambda g: min(g.on_qubits) if hasattr(g, 'on_qubits') else -1)

        for gate in gates:
            if not hasattr(gate, 'matrix') or gate.matrix is None:
                continue  # 跳过测量等非酉操作

            qubit_indices = gate.on_qubits  # List[int]
            qkeys = [qmap[q] for q in qubit_indices]
            matrix = gate.matrix

            # 输入顶点 vin：每个 qubit 上最新的顶点
            vin = [vmap[q][-1] for q in qkeys]
            # 输出顶点 vout：创建新顶点，深度 +1
            vout = [(q, vin[i][1] + 1) for i, q in enumerate(qkeys)]
            for v in vout:
                tg.add_vertex(v)
                vmap[v[0]].append(v)

            # 加入张量边
            tg.add_tensor_edge_split(vin, vout, matrix)

    # 构建边依赖、边界顶点
    tg.build_edge_connections()
    tg.mark_boundary_vertex_states()

    return tg



# 示例构建器：兼容 Cirq，构建张量图
def build_from_cirq_circuit(circuit) -> UndirectedTensorGraph:
    import cirq
    tg = UndirectedTensorGraph()
    all_qubits = sorted(list(circuit.all_qubits()), key=lambda q: q.x)
    qmap: Dict[cirq.Qid, QubitKey] = {q: QubitKey(q, q.x) for q in all_qubits}

    vmap: Dict[QubitKey, List[Tuple[QubitKey, int]]] = {}
    for q in qmap.values():
        v0 = (q, 0)
        tg.add_vertex(v0)
        vmap[q] = [v0]

    for moment in circuit:
        ops = list(moment.operations)
        ops.sort(key=lambda op: min(q.x for q in op.qubits))
        for op in ops:
            qs = [qmap[q] for q in op.qubits]
            matrix = cirq.unitary(op.gate)
            vin = [vmap[q][-1] for q in qs]
            vout = [(q, vin[i][1] + 1) for i, q in enumerate(qs)]
            for v in vout:
                tg.add_vertex(v)
                vmap[v[0]].append(v)
            tg.add_tensor_edge_split(vin, vout, matrix)

    tg.build_edge_connections()
    tg.mark_boundary_vertex_states()
    return tg

# 示例测试：
if __name__ == "__main__":
    # 基于tgqsim的线路
    # import tgqSim
    circuit = QuantumCircuit(3)
    circuit.h(0)
    circuit.cnot(0, 1)
    circuit.x(1)
    tg = build_from_tgq_circuit(circuit)

    # 获取结构摘要
    info = tg.summary()
    print("张量图结构摘要：")
    for k, v in info.items():
        if k != 'tensor_edges':
            print(f"{k}: {v}")
    print("共包含 tensor edges:", len(info["tensor_edges"]))

    # 拓扑排序后的边结构打印
    ordered_edges = tg.get_topological_order()
    print("拓扑排序后的张量边信息：")
    for edge in ordered_edges:
        print(f"{edge.id} -- rank {edge.rank} -- {len(edge.tensor)} elements")
    # # 构造一个简单电路：
    # import cirq
    # q0, q1, q2 = cirq.LineQubit.range(3)
    # circuit = cirq.Circuit(
    #     cirq.H(q0),  # 单比特门：作用于 q0（低位）
    #     cirq.CNOT(q0, q1),  # 双比特门：作用于 q0 和 q1
    #     cirq.X(q1),  # 单比特门：作用于 q1
    #     cirq.Z(q0),  # 单比特门：作用于 q0
    #     cirq.CZ(q0, q1),  # 双比特门：作用于 q0 和 q1
    #     cirq.TOFFOLI(q0, q1, q2)
    # )
    #
    # # # 构造 100 个 qubit
    # # num_qubits = 100
    # # qubits = cirq.LineQubit.range(num_qubits)
    # #
    # # # Moment 0: 对每个 qubit 应用 Hadamard 门（单比特操作）
    # # moment1 = [cirq.H(q) for q in qubits]
    # #
    # # # Moment 1: 对连续两个 qubit（0,1）、(2,3) ... (98,99) 施加 CNOT 门（双比特操作）
    # # moment2 = []
    # # for i in range(0, num_qubits, 2):
    # #     moment2.append(cirq.CNOT(qubits[i], qubits[i + 1]))
    # #
    # # # Moment 2: 对每个 qubit 应用 X 门（单比特操作）
    # # moment3 = [cirq.X(q) for q in qubits]
    # #
    # # # 构造 circuit
    # # circuit = cirq.Circuit(moment1, moment2, moment3)
    #
    # print("构造的电路如下：")
    # print(circuit)
    #
    # tgtest = build_from_cirq_circuit(circuit)
    # info = tgtest.summary()
    #
    #
    # # 返回 info 数据结构（你可以在调试或测试中查看 info 的内容）
    # print(info)
    # # tgtest.build_edge_connections()
    #
    # ordered_edges = tgtest.get_topological_order()
    # for edge in ordered_edges:
    #     print(f"{edge.id} -- rank {edge.rank} -- {len(edge.tensor)} elements")