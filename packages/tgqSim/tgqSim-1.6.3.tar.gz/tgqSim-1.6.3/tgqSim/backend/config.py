from enum import Enum, auto

QCURL = "www.tiangongqs.com"

class QComputerType(Enum):
    SUPER_CONDUCTING = auto()   # 超导量子计算机
    TRAPPED_ION = auto()        # 离子阱量子计算机
    NEUTRAL_ATOM = auto()       # 中性原子量子计算机
    PHOTONIC = auto()           # 光量子计算机

# class Device(Enum):
#     def __init__(self) -> None:
#         super().__init__()

Device = Enum
OFFSET = 40

class SuperConductingDevice(Device):
    GUOJIQ_1 = OFFSET           # 国基一号
    GUOJIQ_2 = auto()           # 国基二号
    GUOJIQ_3 = auto()           # 国基三号

class DeviceStatus(Enum):
    OFFLINE = auto()
    ONLINE = auto()
    MAINTENANCE = auto()