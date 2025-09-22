from tgqSim.circuit.quantum_circuit import QuantumCircuit
from tgqSim.gate.bit import Qubit, QuantumRegister
from tgqSim.gate.instruction import Gate
from tgqSim.circuit.decompose.compiler.transpiler import transpile

import requests, json
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from typing import Tuple, Dict, Set, List
import numpy as np
from copy import deepcopy
import random, string, yaml, time, datetime

class QuantumCircuitSplitUnit:
    __slots__ = ['_circuit', '_logic_to_real', '_real_to_logic', '_fidelity', '_real_chip_topology']
    def __init__(self, 
                 circuit: QuantumCircuit = None, 
                 logic_to_real: Dict[int, int] = {}, 
                 real_to_logic: Dict[int, int] = {},
                 fidelity: Dict[str, float] = {}, 
                 real_chip_topology: np.ndarray = None
        ) -> None:
        self._circuit = circuit
        self._logic_to_real = logic_to_real
        self._real_to_logic = real_to_logic
        self._fidelity = fidelity
        self._real_chip_topology = real_chip_topology
        
        
    @property
    def circuit(self) -> QuantumCircuit:
        """
        获取量子电路
        :return: 量子电路
        """
        return self._circuit
    
    @circuit.setter
    def circuit(self, circuit: QuantumCircuit) -> None:
        if not isinstance(circuit, QuantumCircuit):
            raise TypeError("circuit must be an instance of QuantumCircuit")
        self._circuit = circuit
    
    @property
    def logic_to_real(self) -> Dict[int, int]:
        """
        获取逻辑比特到实际比特的映射

        Returns:
            Dict[int, int]: _description_
        """
        return self._logic_to_real
    
    @logic_to_real.setter
    def logic_to_real(self, logic_to_real: Dict[int, int]) -> None:
        self._logic_to_real = deepcopy(logic_to_real)

    @property
    def real_to_logic(self) -> Dict[int, int]:
        """
        获取实际比特到逻辑比特的映射

        Returns:
            Dict[int, int]: _description_
        """
        return self._real_to_logic
    
    @real_to_logic.setter
    def real_to_logic(self, real_to_logic: Dict[int, int]) -> None:
        self._real_to_logic = deepcopy(real_to_logic)

    @property
    def fidelity(self) -> Dict[str, float]:
        """
        获取量子比特的保真度
        :return: 量子比特保真度字典
        """
        return self._fidelity
    
    @fidelity.setter
    def fidelity(self, fidelity: Dict[str, float]):
        self._fidelity = fidelity
    
    @property
    def real_chip_topology(self) -> np.ndarray:
        """
        获取实际的芯片拓扑结构
        :return: 芯片拓扑结构
        """
        return self._real_chip_topology
    
    @real_chip_topology.setter
    def real_chip_topology(self, real_chip_topology: np.ndarray) -> None:
        if not isinstance(real_chip_topology, np.ndarray):
            raise TypeError("real_chip_topology must be a numpy ndarray")
        if real_chip_topology.ndim != 2 or real_chip_topology.shape[0] != real_chip_topology.shape[1]:
            raise ValueError("real_chip_topology must be a square matrix")
        self._real_chip_topology = deepcopy(real_chip_topology)
    

def request_get(url: str):
    # todo: 未来需要更换成https协议，这里面需要增加需要解析和验证证书的逻辑
    error_info = ""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except HTTPError as err:
        error_info = f"HTTP错误: {err}"
        if response.text:
            error_info += f"响应内容: {response.text[:500]}"  # 截断长文本
        raise ValueError(error_info)
    except ConnectionError as err:
        error_info = f"无法连接到服务器: {err}"
        raise ValueError(error_info)
    except Timeout as err:
        error_info = f"请求超时: {err}"
        raise ValueError(error_info)
    except RequestException as err:
        error_info = f"未知请求错误: {err}"
        raise ValueError(error_info)
    except ValueError as err:
        error_info = f"JSON解析失败: {err} | 原始响应: {response.text[:200]}"
        raise ValueError(error_info)
    
def request_post(url: str, authorization: str, data: dict):
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization
    }
    
    error_info = ""
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except HTTPError as err:
        error_info = f"HTTP错误: {err}"
        if response.text:
            error_info += f"响应内容: {response.text[:500]}"  # 截断长文本
        raise ValueError(error_info)
    except ConnectionError as err:
        error_info = f"无法连接到服务器: {err}"
        raise ValueError(error_info)
    except Timeout as err:
        error_info = f"请求超时: {err}"
        raise ValueError(error_info)
    except RequestException as err:
        error_info = f"未知请求错误: {err}"
        raise ValueError(error_info)
    except ValueError as err:
        error_info = f"JSON解析失败: {err} | 原始响应: {response.text[:200]}"
        raise ValueError(error_info)

def run_task(circuit: QuantumCircuit, authorization: str, nQubit: int, computerType: int) -> dict:
    """
    运行量子任务
    :param circuit: 量子电路
    :param url: 请求的URL
    :param authorization: 授权令牌
    :param nQubit: 量子比特数量
    :return: 任务执行结果
    """
    data = to_json(optimized_circ=circuit, nQubits=nQubit, computerType=computerType)
    # f = open("test.yaml", "w", encoding="utf-8")
    # f.write(yaml.dump(data, allow_unicode=True, default_flow_style=False))
    # f.close()
    # return data
    try:
        exectask_url = "https://www.tiangongqs.com/v1/quantumplatform/executetask"
        response = request_post(url=exectask_url, authorization=authorization, data=data)
    except ValueError as e:
        raise RuntimeError(f"运行任务失败: {e}")
    
    while True:
        try:
            time.sleep(2)  # 每2秒检查一次任务状态
            check_url = f"http://www.tiangongqs.com/v1/quantumplatform/taskdetail?instanceId={data['instanceId']}"
            response = request_get(url=check_url)
            if response["status"] == 200:
                data = response["data"]
                if data["state"] == 2:
                    result = {}
                    probility = data["probabilityHis"]
                    for info in probility:
                        result[info["qState"]] = info["prob"]
                    return result
                elif data["state"] == 1:
                    raise RuntimeError(f"任务执行失败: {data['error']}")
                elif data["state"] == 0:
                    print(f"{datetime.datetime.now().replace(microsecond=0)} 任务正在执行中...")
                    continue
                elif data["state"] == 3:
                    print(f"{datetime.datetime.now().replace(microsecond=0)} 任务正在排队中...")
                    continue
            else:
                raise RuntimeError(response["msg"])
        except ValueError as e:
            raise RuntimeError(f"获取任务状态失败: {e}")

def quantum_computer_base_info(url: str) -> Tuple[int, float, float, int]:
    try:
        respones = request_get(url=url)
        result = json.loads(respones.text)
        if data["code"] == 0:
            data = result["data"]
            qubits = data["max_qubits"]
            t1_mean = data["t1_mean"]
            t2_mean = data["t2_mean"]
            state = data["state"]                
        else:
            raise RuntimeError(result["msg"])
    except Exception as e:
        raise ValueError(f"QuantumComputer base info: {e}")
    return qubits, t1_mean, t2_mean, state

def quantum_computer_qubit_info(
        single_url: str, 
        double_url: str, 
        num_qubit: int
    )-> Tuple[np.ndarray, Dict[str, float], Dict[str, float], Dict[str, float], Dict[str, float]]:
    chip_topology = np.zeros(shape=(num_qubit, num_qubit))
    qubit_fidelity, single_gate_error_rate, qubit_t1, qubit_t2 = dict(), dict(), dict(), dict()
    try:
        respones = request_get(url=single_url)
        result = json.loads(respones.text)
        if result["code"] == 0:
            data = result["data"]
            for qubit in data:
                qubit_name = qubit["qubit"]
                qubit_index = int(qubit_name.split("Q")[-1])
                if qubit_index >= num_qubit:
                    raise IndexError("Out of range")
                elif qubit_index < 0:
                    qubit_index += num_qubit
                chip_topology[qubit_index, qubit_index] = 1
                qubit_fidelity[qubit_name] = qubit["fidelity_0"]
                single_gate_error_rate[qubit_name] = qubit["singlegate_error_rate"]
                qubit_t1[qubit_name] = qubit["t1"]
                qubit_t2[qubit_name] = qubit["t2"]
        else:
            raise RuntimeError(result["msg"])
    except Exception as e:
        raise ValueError(f"QuantumComputer single qubits info: {e}")

    try:
        respones = request_get(url=double_url)
        result = json.loads(respones.text)
        if result["code"] == 0:
            data = result["data"]
            for qubit in data:
                qubit_name = qubit["qubit"]
                qubit_index_list = [int(ele.split("Q")[-1]) for ele in qubit_name.split("-")]
                for i, qubit_index in enumerate(qubit_index_list):
                    if qubit_index >= num_qubit:
                        raise IndexError("Out of range")
                    elif qubit_index < 0:
                        qubit_index_list[i] += num_qubit
                chip_topology[qubit_index_list[0], qubit_index[1]] = 1
                chip_topology[qubit_index_list[1], qubit_index[0]] = 1
                qubit_fidelity[qubit_name] = qubit["cz_fidelity"]
        else:
            raise RuntimeError(result["msg"])
    except Exception as e:
        raise ValueError(f"QuantumComputer single qubits info: {e}")
    return chip_topology, qubit_fidelity, single_gate_error_rate, qubit_t1, qubit_t2

def quantum_computer_info(url: str):
    try:
        respone = request_get(url=url)
        data = respone["data"]
        qubits = int(data["maxQubits"])
        
        # basic information
        basicInfo = data["basicInfo"]
        for ele in basicInfo:
            if ele["key"] == "T1":
                t1_mean = ele["avg"]
            elif ele["key"] == "T2":
                t2_mean = ele["avg"]
        
        # single qubite information
        chip_topology = np.zeros(shape=(qubits, qubits), dtype=np.int8)
        singleBitInfo = data["singleBitInfo"]
        qubit_fidelity:Dict[str, float] = dict()
        for i in range(qubits):
            qubit_fidelity[f"Q{i}"] = 0.0
        qubit_t1: Dict[str, float] = dict()
        qubit_t2: Dict[str, float] = dict()
        for ele in singleBitInfo:
            qubit_name = ele["quantumBit"]
            qubit_index = int(qubit_name.split("Q")[-1])
            chip_topology[qubit_index, qubit_index] = 1
            qubit_fidelity[qubit_name] = ele["singlefidelity"]
            qubit_t1[qubit_name] = ele["T1"]
            qubit_t2[qubit_name] = ele["T2"]
        
        # double qubit information
        doubleBitInfo = data["doubleBitInfo"]
        for ele in doubleBitInfo:
            qubit_name = ele["couplingQubits"]
            qubit_index_list = [int(ele.split("Q")[-1]) for ele in qubit_name.split("-")]
            chip_topology[qubit_index_list[0], qubit_index_list[1]] = 1
            chip_topology[qubit_index_list[1], qubit_index_list[0]] = 1
            # qubit_fidelity[qubit_name] = ele["czFidelity"]
    except Exception as e:
        raise ValueError(f"Get Quantum computer error, info: {e}")
    # 临时修改
    # chip_topology = np.ones(shape=(qubits, qubits), dtype=np.int8)
    # print(qubit_fidelity)
    return qubits, t1_mean, t2_mean, chip_topology, qubit_fidelity, qubit_t1, qubit_t2

def generate_custom_uuid():
    """生成类似 '9e45a03e-ea85-4ae1-823c-17b26f4d' 的自定义随机字符串"""
    chars = string.hexdigits.lower()  # 0-9, a-f
    segments = [
        ''.join(random.choices(chars, k=8)),  # 8 字符（如 '9e45a03e'）
        ''.join(random.choices(chars, k=4)),  # 4 字符（如 'ea85'）
        ''.join(random.choices(chars, k=4)),  # 4 字符（如 '4ae1'）
        ''.join(random.choices(chars, k=4)),  # 4 字符（如 '823c'）
        ''.join(random.choices(chars, k=6)),  # 6 字符（如 '17b26f4d'）
    ]
    return '-'.join(segments)  # 用 '-' 连接

def to_json(optimized_circ:QuantumCircuit, nQubits:int, computerType: int=40) -> dict:
    '''
    构建转json格式的不同字典格式
    '''
    data = {
        'version': '1.1',
        'circuit-type': 'simple',
        'computerType': None,
        'instanceId': None,
        'measure-position': [],
        'projectName': None,
        'quantum-num': None,
        'repetitions': 1024,
        'steps': []
    }
    
    print("optimize circuit:")
    print(optimized_circ.num_qubits)
    index = [0] * nQubits
    circuit_json = {}
    for i, gate in enumerate(optimized_circ):
        if i > 31:
            print(f"{i}: gate.name: {gate.name}")
            print(f"gate.on_qubits: {gate.on_qubits[0].index()}")
        tmp = {}
        if hasattr(gate, "theta"):
            nCol = index[gate.on_qubits[0].index()]
            tmp['name'] = gate.name.lower()
            tmp['targets'] = [bit.index() for bit in gate.on_qubits]
            tmp['theta'] = float(round(gate.theta, 4))
            index[gate.on_qubits[0].index()] += 1
            print(tmp) if i > 31 else print(".....")
        elif len(gate.on_qubits) == 2:
            nCol = max([index[bit.index()] for bit in gate.on_qubits])
            minQIndex, maxQIndex = min([bit.index() for bit in gate.on_qubits]), max([bit.index() for bit in gate.on_qubits])
            tmp['name'] = gate.name.lower()
            tmp['targets'] = [bit.index() for bit in gate.on_qubits]
            for i in range(minQIndex, maxQIndex + 1):
                # print(f"i = {i}, index = {index}")
                index[i] = nCol + 1
        elif gate.name == 'SQRT_X':
            nCol = index[gate.on_qubits[0].index()]
            tmp['name'] = 'sx'
            tmp['targets'] = [bit.index() for bit in gate.on_qubits]
            tmp['root'] = '1/2'
            index[gate.on_qubits[0].index()] += 1
        else:
            nCol = index[gate.on_qubits[0].index()]
            tmp['name'] =gate.name.lower()
            tmp['targets'] = [bit.index() for bit in gate.on_qubits]
            index[gate.on_qubits[0].index()] += 1
        if nCol not in circuit_json:
            circuit_json[nCol] = [tmp]
        else:
            circuit_json[nCol].append(tmp)
    for key in sorted(circuit_json.keys()):
        data['steps'].append({
            'index': key,
            'gates': circuit_json[key]
        })
    maxIndex = max(index)
    measue_gate = {"index": maxIndex, "gates": []}
    for i in optimized_circ.classical_register:
        measue_gate["gates"].append({
            "name": "measure",
            "targets": [i],
            "bits": 0
        })
    data['steps'].append(measue_gate)
    data["instanceId"] = generate_custom_uuid()
    data['quantum-num'] = nQubits
    data['computerType'] = computerType
    data['measure-position'] = optimized_circ.classical_register
    data["projectName"] = f"tgqSim-{data['instanceId'].split('-')[0]}"
    data["repetitions"] = 2 ** (len(optimized_circ.classical_register) + 1)
    print(data)
    return data

def get_real_chip_topology(
        chip_topology: np.ndarray, 
        qubit_fidelity: Dict[str, float], 
        circuit: QuantumCircuit
    ) -> Tuple[np.ndarray, Dict[str, float]]:
    """
    获取实际的芯片拓扑结构
    :param chip_topology: 芯片拓扑结构
    :param qubit_num: 量子比特数量
    :return: 实际的芯片拓扑结构
    """
    circuit_bits:Set[int] = set()
    for gate in circuit:
        for qubit in gate.on_qubits:
            if isinstance(qubit, Qubit):
                circuit_bits.add(qubit.index())
            else:
                raise TypeError("Circuit contains non-Qubit elements")
    real_fidelity = {}
    for i in circuit_bits:
        real_fidelity[f"Q{i}"] = qubit_fidelity[f"Q{i}"]
    mesh_grid_rows, mesh_grid_cols = np.meshgrid(list(circuit_bits), list(circuit_bits))
    real_chip_topology = chip_topology[mesh_grid_rows, mesh_grid_cols]
    return real_chip_topology.astype(np.int8), real_fidelity, max(circuit_bits) + 1

def find_connected_component(adj_matrix: np.ndarray) -> List[Set[int]]:
    """
    Find connected components in an undirected graph represented by an adjacency matrix.
    
    :param adj_matrix: Adjacency matrix of the graph.
    :return: List of connected components, where each component is a list of node indices.
    """
    n = adj_matrix.shape[0]
    visited = np.zeros(n, dtype=bool)
    components = []

    def dfs(node: int, component: set):
        visited[node] = True
        component.add(node)
        for neighbor in range(n):
            if adj_matrix[node, neighbor] == 1 and not visited[neighbor]:
                dfs(neighbor, component)

    for i in range(n):
        if not visited[i]:
            component = set()
            dfs(i, component)
            components.append(component)

    return components

def split_quantum_circuit_by_chip_topology(
        circuit: QuantumCircuit, 
        chip_topology: np.ndarray = None,
        fidelity: Dict[str, float] = None
    ) -> QuantumCircuitSplitUnit:
    """
    根据芯片拓扑结构将量子电路拆分为多个子电路。

    Args:
        circuit (QuantumCircuit): 量子线路图
        chip_topology (np.ndarray): 芯片拓扑结构

    Returns:
        QuantumCircuitSplitUnit: 拆分后的量子电路图
    """
    if not isinstance(circuit, QuantumCircuit):
        raise TypeError("circuit must be an instance of QuantumCircuit")
    
    num_qubits = circuit.num_qubits
    
    if not chip_topology:
        chip_topology = np.ones(shape=(num_qubits, num_qubits), dtype=np.int8)
    
    if not fidelity:
        fidelity = {}
        for i in range(num_qubits):
            fidelity[f'Q{i}'] = 1.0
    
    connected_component = find_connected_component(chip_topology)
    # print(f"Connected components: {connected_component}")
    result = []
    for component in connected_component:
        tmpQubitSet:set = set()
        tmpGateList:List[Gate] = []
        for gate in circuit:
            if any(qubit.index() in component for qubit in gate.on_qubits):
                if not all(qubit.index() in component for qubit in gate.on_qubits):
                    raise ValueError("Circuit contains gates that span multiple components")
            else:
                continue
            tmpQubitSet = tmpQubitSet.union(set(gate.on_qubits))
            tmpGateList.append(gate)
        if tmpGateList == []:
            continue
        tmpQuantumCircuit = QuantumCircuitSplitUnit()
        # print(f"Component size: {len(tmpQubitSet)}")
        # print(f"QubitSet: {tmpQubitSet}")
        real_to_logic = {}
        logic_to_real = {}
        unit_fidelity = {}
        for i, qubit in enumerate(tmpQubitSet):
            # print(f"Qubit: {qubit}, index: {i}")
            real_to_logic[qubit] = i
            logic_to_real[i] = qubit
            unit_fidelity[f"Q{i}"] = fidelity[f"Q{qubit.index()}"]
        tmpQuantumCircuit.logic_to_real = logic_to_real
        tmpQuantumCircuit.real_to_logic = real_to_logic
        tmpQuantumCircuit.fidelity = unit_fidelity
        # print(f"Real to logic mapping: {tmpQuantumCircuit.real_to_logic}")
        # print(f"Logic to real mapping: {tmpQuantumCircuit.logic_to_real}")
        # qreg = QuantumRegister(size=len(tmpQubitSet))
        cir = QuantumCircuit(num_qubits=len(tmpQubitSet))
        for gate in tmpGateList:
            new_on_qubits = [tmpQuantumCircuit.real_to_logic[qubit] for qubit in gate.on_qubits]
            gate.on_qubits = new_on_qubits
            cir.append(gate)
        tmpQuantumCircuit.circuit = cir
        
        tmpQuantumCircuit.real_chip_topology = chip_topology[np.ix_(list(tmpQuantumCircuit.real_to_logic.keys()), list(tmpQuantumCircuit.real_to_logic.keys()))]
        result.append(tmpQuantumCircuit)
    return result

def decompose_quantum_circuit_split_unit(
        quantum_circuit_split_unit_list: List[QuantumCircuitSplitUnit], 
        nQubits: int,
        base_single_gates: List[str],
        base_double_gates: List[str]
    ) -> QuantumCircuit:
    # 最终形成的量子电路
    qreg = QuantumRegister(size=nQubits)
    circuit = QuantumCircuit(num_qubits=nQubits, qreg=qreg)
    for unit in quantum_circuit_split_unit_list:
        if not isinstance(unit, QuantumCircuitSplitUnit):
            raise TypeError("quantum_circuit_split_unit_list must be a list of QuantumCircuitSplitUnit")
        
        # 对线路进行拆解
        # print("unit.circuit")
        # print(unit.circuit)
        # print(f"unit.circuit.num_sgate: {unit.circuit.num_sgate}")
        # print(f"unit.circuit.num_dgate: {unit.circuit.num_dgate}")
        # print(f"unit.circuit.num_mgate: {unit.circuit.num_mgate}")
        # print(f"unit.circuit.num_qubits: {unit.circuit.num_qubits}")
        # print(f"base_single_gates: {base_single_gates}")
        # print(f"base_double_gates: {base_double_gates}")
        # print(f"unit.real_chip_topology: {unit.real_chip_topology}")
        # print(f"unit.circuit.num_qubits: {unit.circuit.num_qubits}")
        
        # 注：目前不能传递保真度信息，算法部门需要做进一步更新
        cir, _, _ = transpile(
            circuit=unit.circuit,
            basis_single_qubit_gate=base_single_gates,
            basis_double_qubit_gate=base_double_gates,
            chip_topology=unit.real_chip_topology,
            starting_physical_qubit_num=unit.circuit.num_qubits
        )
        
        for gate in cir:
            new_on_qubits = [qreg[unit.logic_to_real[qubit]] for qubit in gate.on_qubits]
            gate.on_qubits = new_on_qubits
            circuit.append(gate)
    return circuit