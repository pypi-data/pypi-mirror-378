from tgqSim.backend.config import SuperConductingDevice, QCURL, Device, DeviceStatus
from tgqSim.utils.super_conducting_tools import *
from tgqSim.circuit.quantum_circuit import QuantumCircuit
# from circuit.decompose.compiler.transpiler import transpile
# from gate.bit import Qubit

from typing import List, Dict, Set
import numpy as np

class GJQ:
    __slots__ = ['_token', '_backendList']
    def __init__(self, token: str) -> None:
        self._token = token
    
    def _check_account(self):
        # todo: 未来需要增加账号验证逻辑
        return True
        
    def get_provider(self):
        if not self._check_account():
            raise ValueError("Account verification failed.")
        return Provider(token=self._token)
        

class Provider:
    __slots__ = ['_token', '_backendDict']
    def __init__(self, token: str) -> None:
        self._token = token
        self._backendDict:Dict[Device, Backend] = dict()
    
    def backends(self) -> List['Backend']:
        for id in SuperConductingDevice:
            url = f"http://{QCURL}/v1/quantumplatform/qdevicedetail?deviceid={id.value}"
            # print(f"url={url}")
            try:
                respone = request_get(url=url)
                state = respone["data"]["state"]
                # print(f"state={state}")
                if 1 == state:
                    base_singlegates = ['x', 'y', 'sx', 'rx', 'ry', 'rz']
                    base_doublegates = ['cz']
                    qubits, t1_mean, t2_mean, chip_topology, qubit_fidelity, qubit_t1, qubit_t2 = \
                        quantum_computer_info(url=url)
                    self._backendDict[id] = Backend(
                        qubits=qubits,
                        base_singlegates=base_singlegates,
                        base_doublegates=base_doublegates,
                        chip_topology=chip_topology,
                        qubit_fidelity=qubit_fidelity,
                        qubit_t1=qubit_t1,
                        qubit_t2=qubit_t2,
                        t1_mean=t1_mean,
                        t2_mean=t2_mean,
                        device_provider=id,
                        status=DeviceStatus.ONLINE, 
                        token=self._token
                    )
            except Exception as e:
                Warning(f"Error: quantum computer(id: {id.value}), Error info: {e}")
        return list(self._backendDict.keys())
    
    def get_backend(self, backend_name: Device) -> 'Backend':
        return self._backendDict.get(backend_name, None)

class Backend:
    __slots__ = ['_qubits', '_base_singlegates', '_base_doublegates', '_chip_topology', '_qubit_fidelity', '_provider',
                 '_t1_mean', "_t2_mean", "_qubit_t1", "_qubit_t2", "_status", "_token"]
    def __init__(self, 
                 qubits: int, base_singlegates: List[str],
                 base_doublegates: List[str],
                 chip_topology: np.ndarray,
                 qubit_fidelity: Dict[str, float],
                 qubit_t1: Dict[str, float],
                 qubit_t2: Dict[str, float],
                 t1_mean: Dict[str, float],
                 t2_mean: Dict[str, float],
                 device_provider: Device,
                 status: DeviceStatus, token: str) -> None:
        self._qubits:int = qubits
        self._base_singlegates: List[str] = base_singlegates
        self._base_doublegates: List[str] = base_doublegates
        self._chip_topology: np.ndarray = chip_topology
        self._qubit_fidelity: Dict[str, float] = qubit_fidelity
        # self._single_gate_error_rate: Dict[str, float] = None
        self._qubit_t1: Dict[str, float] = qubit_t1
        self._qubit_t2: Dict[str, float] = qubit_t2
        self._t1_mean: Dict[str, float] = t1_mean
        self._t2_mean: Dict[str, float] = t2_mean
        self._provider:Device = device_provider
        self._status: DeviceStatus = status
        self._token: str = token

    
    @property
    def qubits(self):
        return self._qubits
    
    @property
    def base_singlegates(self):
        return self._base_singlegates
    
    @property
    def base_doublegates(self):
        return self._base_doublegates
    
    @property
    def chip_topology(self):
        return self._chip_topology
    
    @property
    def qubit_fidelity(self):
        return self._qubit_fidelity
    
    @property
    def single_gate_error_rate(self):
        return self._single_gate_error_rate
    
    @property
    def qubit_t1(self):
        return self._qubit_t1
    
    @property
    def qubit_t2(self):
        return self._qubit_t2
    
    @property
    def t1_mean(self):
        return self._t1_mean
    
    @property
    def t2_mean(self):
        return self._t2_mean
    
    @property
    def status(self):
        self._status = self._get_device_status()
        return self._status
    
    def _get_device_status(self):
        url = f"http://{QCURL}/v1/quantumplatform/qdevicedetail?deviceid={self._provider.value}"
        try:
            respone = request_get(url=url)
            state = respone["data"]["state"]
            if 1 == state:
                return DeviceStatus.ONLINE
            else:
                return DeviceStatus.MAINTENANCE
        except:
            return DeviceStatus.OFFLINE
    
    # def configures(self):
    #     url = f"http://{QCURL}/v1/quantumplatform/qdevicedetail?deviceid={self._provider.value}"
    #     self._base_gates = ['x', 'y', 'sx', 'rx', 'ry', 'rz', 'cz']
    #     self._qubits, self._t1_mean, self._t2_mean, self._chip_topology, self._qubit_fidelity, self._qubit_t1, self._qubit_t2 = \
    #         quantum_computer_info(url=url)
    #     return self
    def run(self, original_circuit: QuantumCircuit):
        """
        Execute the quantum circuit on the backend.
        :param circuit: The quantum circuit to execute.
        :return: Result of the execution.
        """
        if not isinstance(original_circuit, QuantumCircuit):
            raise TypeError("circuit must be an instance of QuantumCircuit")
        
        # Here you would implement the logic to run the circuit on the backend
        # For now, we will just return a placeholder result        
        real_chip_topology, _, nQubit = get_real_chip_topology(
            chip_topology=self._chip_topology, 
            qubit_fidelity=self._qubit_fidelity, 
            circuit=original_circuit
        )
        
        result = split_quantum_circuit_by_chip_topology(circuit=original_circuit)
        circuit = decompose_quantum_circuit_split_unit(
            quantum_circuit_split_unit_list=result,
            nQubits=original_circuit.num_qubits,
            base_single_gates=self._base_singlegates,
            base_double_gates=self._base_doublegates
        )
        # if not original_circuit.is_decomposed:
        #     circuit, _, _ = transpile(
        #         circuit=original_circuit, 
        #         basis_single_qubit_gate=self._base_singlegates,
        #         basis_double_qubit_gate=self._base_doublegates,
        #         chip_topology=real_chip_topology,
        #         starting_physical_qubit_num=self._qubits
        #     )
        circuit.measure(original_circuit.measure_qubits, original_circuit.classical_register)
        # print(circuit)
        
        result = run_task(circuit=circuit, authorization=self._token, nQubit=circuit.num_qubits, computerType=self._provider.value)
        return result