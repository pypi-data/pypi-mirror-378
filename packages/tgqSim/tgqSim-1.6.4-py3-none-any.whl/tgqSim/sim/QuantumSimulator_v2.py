from tgqSim.circuit.quantum_circuit import QuantumCircuit
from tgqSim.sim.cpu_simulator_runner import run_with_cpu_device
from tgqSim.sim.gpu_simulator_runner import run_with_gpu_device

import numpy as np
import GPUtil
from typing import List
from numba import prange

class QuantumSimulator:
    def __init__(self, device='cpu', noise_model=None):
        self.state = None
        self.noise_model = noise_model
        self._device = device
        self._deviceId = None
        self._get_default_config()
    
    def _get_default_config(self):
        """
           获取默认的配置
           后面可以再增加NPU相关的内容
        """
        if self._device.lower() == "gpu":
            self._deviceId = self._get_default_GPUId()
            
    
    def _get_default_GPUId(self) -> List[int]:
        ""
        gpus = GPUtil.getGPUs()
        if 0 == len(gpus):
            raise ValueError("There is no GPU resource in current environment")
        return [gpus[0].id]

    # todo 最好是把加了噪声之后的线路也保留一下成一个新的QuantumCircuit对象
    # todo 注意一下像ccx，他的构建方法可以是c-c-x、c-cx或者是ccx原生，但是他们分别的matrix属性是不一样的
    def run_statevector(self, circuit: QuantumCircuit):
        # 现在不在这里构造含噪声线路了,直接摘出去,QuantumCircuit类已经构造好了
        if self._device == 'cpu':
            state = run_with_cpu_device(circuit=circuit)
        elif self._device == 'gpu':
            state = run_with_gpu_device(circuit=circuit, gpuId=self._deviceId)
        for i in prange(2**(circuit.num_qubits-1)):
            reverse_val = int(format(i, f"0{circuit.num_qubits}b")[::-1], 2)
            if reverse_val > i: # 避免出现重复交换
                state[i], state[reverse_val] = state[reverse_val], state[i]
        self.state = state
        return self.state
    # def run_statevector(self, circuit: QuantumCircuit):
    #     self.state = np.zeros(2 ** circuit.num_qubits, dtype=complex)
    #     self.state[0] = 1.0
    #
    #     for gate in circuit.circuit:
    #         # 注意这个gate是真门，下边的g是可能是噪声门，别用错了
    #         gates_to_apply = [gate]
    #         if self.noise_model:
    #             print("当前这一组有噪声")
    #             gates_to_apply = self.noise_model.noisy_operation(gate)
    #             print("当前这一组门， ", gates_to_apply)
    #
    #         for g in gates_to_apply:
    #             gate_type = g.name
    #             qargs = [qb.index() for qb in g.on_qubits]
    #             angles = g.params if isinstance(g.params, tuple) else (g.params,)
    #             print("  Applying gate:", gate_type, "on qubits:", qargs, "with args:", angles)
    #
    #             if len(qargs) == 1:
    #                 print("  当前门认为是单比特门，类型是：{}， 矩阵是：{}".format(gate_type, g.matrix))
    #                 self.state = SingleAct(self.state, circuit.num_qubits, g.matrix, qargs[0])
    #             elif len(qargs) == 2:
    #                 print("  当前门认为是双比特门，类型是：{}， 矩阵是：{}".format(gate_type, g.matrix))
    #                 # print("  当前双比特门是否为控制门，", gate.control_qubit)
    #                 self.state = DoubleAct(self.state, circuit.num_qubits, g.matrix, qargs)
    #             # elif len(qargs) == 3:
    #             #     self.state = TripleAct(self.state, circuit.num_qubits, gate_type, qargs, *angles)
    #             else:
    #                 raise ValueError("Unsupported number of qubits for gate.")
    #     return self.state

    # todo  这个地方可能要在外边再加一个循环
    def execute(self, circuit: QuantumCircuit, shots: int = 1000):
        statevector = self.run_statevector(circuit)
        prob = np.real(np.conjugate(statevector) * statevector)
        print(prob)
        distribution = {format(i, f'0{circuit.num_qubits}b'): prob[i] for i in range(len(prob))}
        result = {}
        cumulate = 0
        sample = np.random.uniform(0, 1, size=shots)
        for key, p in distribution.items():
            new_cumulate = cumulate + p
            result[key] = sum((cumulate <= sample) & (sample < new_cumulate))
            cumulate = new_cumulate
        return result
