from networkx import Graph, DiGraph
from gate.bit import Qubit, QuantumRegister
from typing import Union, Dict, Tuple, List
from gate.instruction import Gate
from circuit.quantum_circuit import QuantumCircuit

def create_dag(dag_mapping: Dict[Tuple[Qubit, int, Gate], Tuple[int, Gate]]) -> DiGraph:
    circuit_dag = DiGraph()
    for mapping in dag_mapping.keys():
        v_index = mapping[1]
        v = mapping[2]
        u_index = dag_mapping.get(mapping)[0]
        u = dag_mapping.get(mapping)[1]
        # 生成新的边，其中U和V是两个节点
        # U表示前面那个节点信息，U_index是它在DAG中的索引
        # V表示后面那个节点信息，V_index是它在DAG中的索引
        circuit_dag.add_edge((u, u_index), (v, v_index))

    return circuit_dag

def get_dag_mapping(instructions: List[Gate]) -> Dict[Tuple[Qubit, int, Gate], Tuple[int, Gate]]:
    circuit_dag_mapping:Dict[Tuple[Qubit, int, Gate], Tuple[int, Gate]] = dict()
    # circuit_instructions = enumerate(instructions)
    for curr_gate_index, curr_gate in enumerate(instructions):
        # 问题：下面这个定义的curr_gate_qubits是一个list，什么情况下长度不是2？
        curr_gate_qubits = [curr_gate.control_qubit, curr_gate.target_qubit]
        if len(curr_gate_qubits) == 2:
            for curr_gate_qubit in curr_gate_qubits:
                # current_instructions = enumerate(list(instructions)[:curr_gate_index])
                for prev_gate_index, prev_gate in enumerate(list(instructions)[:curr_gate_index]):
                    prev_gate_qubits = set([prev_gate.control_qubit, prev_gate.target_qubit])
                    if curr_gate_qubit in prev_gate_qubits:
                        circuit_dag_mapping.update({(curr_gate_qubit, curr_gate_index, curr_gate): (prev_gate_index,
                                                                                                    prev_gate)})

    return circuit_dag_mapping

def initialize_front_layer(circuit_dag: DiGraph):
    front_layer_gates = list()
    for node in circuit_dag.nodes():
        if circuit_dag.in_degree(node) == 0:
            front_layer_gates.append(node)
    return front_layer_gates


if __name__ == '__main__':
    num_qubits = 3
    qreg = QuantumRegister(num_qubits)
    circuit = QuantumCircuit(num_qubits=num_qubits, qreg=qreg)
    # circuit.h(qreg[0])
    circuit.cnot(qreg[0], qreg[1])
    circuit.cnot(qreg[1], qreg[2])
    circuit.rxx(qreg[0], qreg[1], theta=1.57)
    print(circuit)

    mapping = get_dag_mapping(instructions=circuit)
    circuit_dag = create_dag(dag_mapping=mapping)
    front_layer_gates = initialize_front_layer(circuit_dag=circuit_dag)
    for ele in circuit_dag.successors(front_layer_gates[0]):
        print(ele)
    print("DAG Mapping:", front_layer_gates)