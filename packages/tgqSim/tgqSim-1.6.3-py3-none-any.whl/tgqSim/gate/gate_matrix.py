from enum import Enum
import numpy as np

class GateType(Enum):
    X = 1
    Y = 2
    Z = 3
    SQRT_X = 4
    SQRT_X_DAG = 5
    ZERO = 6
    ONE = 7
    RX = 8
    RY = 9
    RZ = 10
    H = 11
    S = 12
    S_DAG = 13
    T = 14
    T_DAG = 15
    CNOT_CS = 16
    CNOT_CB = 17
    CZ = 18
    SWAP = 19
    CP = 20
    ISWAP = 21
    RXX = 22
    RYY = 23
    RZZ = 24
    SYC = 25
    CCX = 26
    CSWAP = 27
    RP = 28


def Rx(theta: float) -> np.ndarray:
    cos = np.cos(theta / 2)
    isin = -1j * np.sin(theta / 2)
    return np.array([[cos, isin], [isin, cos]], dtype=np.complex128)

def Ry(theta: float) -> np.ndarray:
    cos = np.cos(theta / 2)
    sin = np.sin(theta / 2)
    return np.array([[cos, -sin], [sin, cos]], dtype=np.complex128)

def Rz(theta: float) -> np.ndarray:
    return np.array([[np.exp(-1j * theta / 2), 0], [0, np.exp(1j * theta / 2)]], dtype=np.complex128)

def Cp(theta: float) -> np.ndarray:
    return np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, np.exp(1j * theta)]], dtype=np.complex128)

def Rxx(theta: float) -> np.ndarray:
    cos = np.cos(theta / 2)
    isin = -1j * np.sin(theta / 2)
    return np.array([[cos, 0, 0, isin], [0, cos, isin, 0], [0, isin, cos, 0], [isin, 0, 0, cos]], dtype=np.complex128)

def Ryy(theta: float) -> np.ndarray:
    cos = np.cos(theta / 2)
    isin = 1j * np.sin(theta / 2)
    return np.array([[cos, 0, 0, isin], [0, cos, -isin, 0], [0, -isin, cos, 0], [isin, 0, 0, cos]], dtype=np.complex128)

def Rzz(theta: float) -> np.ndarray:
    return np.array([[np.exp(-1j * theta / 2), 0, 0, 0], [0, np.exp(1j * theta / 2), 0, 0], [0, 0, np.exp(1j * theta / 2), 0], [0, 0, 0, np.exp(-1j * theta / 2)]], dtype=np.complex128)

def Rp(theta: float) -> np.ndarray:
    return np.array([[1, 0], [0, np.exp(1j * theta)]], dtype=np.complex128)

# single qubit gates
I_GATE = np.array([[1, 0], [0, 1]], dtype=np.complex128)
ZERO_GATE = np.array([[1, 0], [0, 0]], dtype=np.complex128)  # |0><0|
ONE_GATE = np.array([[0, 0], [0, 1]], dtype=np.complex128)  # |1><1|
x_mat = np.array([[0, 1], [1, 0]], dtype=np.complex128)
y_mat = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
z_mat = np.array([[1, 0], [0, -1]], dtype=np.complex128)
sqrt_x_mat = 1 / 2 * np.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]], dtype=np.complex128)
sqrt_x_sdg_mat = 1 / 2 * np.array([[1 - 1j, 1 + 1j], [1 + 1j, 1 - 1j]], dtype=np.complex128)
rx_mat = Rx
ry_mat = Ry
rz_mat = Rz
h_mat = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
s_mat = np.array([[1, 0], [0, 1j]], dtype=np.complex128)
s_dag_mat = np.array([[1, 0], [0, -1j]], dtype=np.complex128)
t_mat = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=np.complex128)
t_dag_mat = np.array([[1, 0], [0, np.exp(-1j * np.pi / 4)]], dtype=np.complex128)
zero_mat = np.array([[1, 0], [0, 0]], dtype=np.complex128)
one_mat = np.array([[0, 0], [0, 1]], dtype=np.complex128)
rp_mat = Rp

# two qubit gates
cnot_mat_csmall = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=np.complex128)
cnot_mat_cbig = np.array([[1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0]], dtype=np.complex128)
cz_mat = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]], dtype=np.complex128)
swap_mat = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=np.complex128)
cp_mat = Cp
iswap_mat = np.array([[1, 0, 0, 0], [0, 0, 1j, 0], [0, 1j, 0, 0], [0, 0, 0, 1]], dtype=np.complex128)
rxx_mat = Rxx
ryy_mat = Ryy
rzz_mat = Rzz
syc_mat = np.array([[1, 0, 0, 0], [0, 0, -1j, 0], [0, -1j, 0, 0], [0, 0, 0, np.exp(-1j * np.pi / 6)]], dtype=np.complex128)

# three qubit gates
ccx_mat = np.array([
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 1, 0]
        ], dtype=np.complex128)
cswap_mat = np.array([
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1]
        ], dtype=np.complex128)

name_matrix_mapping = {
    GateType.X: x_mat,
    GateType.Y: y_mat,
    GateType.Z: z_mat,
    GateType.SQRT_X: sqrt_x_mat,
    GateType.SQRT_X_DAG: sqrt_x_sdg_mat,
    GateType.RX: rx_mat,
    GateType.RY: ry_mat,
    GateType.RZ: rz_mat,
    GateType.H: h_mat,
    GateType.S: s_mat,
    GateType.S_DAG: s_dag_mat,
    GateType.T: t_mat,
    GateType.T_DAG: t_dag_mat,
    GateType.ZERO: zero_mat,
    GateType.ONE: one_mat,
    GateType.CNOT_CS: cnot_mat_csmall,
    GateType.CNOT_CB: cnot_mat_cbig,
    GateType.CZ: cz_mat,
    GateType.SWAP: swap_mat,
    GateType.CP: cp_mat,
    GateType.ISWAP: iswap_mat,
    GateType.RXX: rxx_mat,
    GateType.RYY: ryy_mat,
    GateType.RZZ: rzz_mat,
    GateType.SYC: syc_mat,
    GateType.CCX: ccx_mat,
    GateType.CSWAP: cswap_mat,
    GateType.RP: rp_mat
}

SQGlibrary = {'h': h_mat, 'x': x_mat, 'y': y_mat, 'z': z_mat, 'sx': sqrt_x_mat, 'sxdg': sqrt_x_sdg_mat,
              's': s_mat, 'sdg': s_dag_mat, 't': t_mat, 'tdg': t_dag_mat}

SPaulibrary = {'rx': rx_mat, 'ry': ry_mat, 'rz': rz_mat, 'rp': rp_mat}
