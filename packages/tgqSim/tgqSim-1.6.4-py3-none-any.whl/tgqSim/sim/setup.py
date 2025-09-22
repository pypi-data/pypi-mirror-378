from setuptools import setup, find_packages
from Cython.Build import cythonize

setup(
    name="simulator_runner",
    packages=find_packages(),  # 自动发现所有子模块
    ext_modules=cythonize(
        ["gpu_simulator_runner.py", "dcu_simulator_runner.py"],  # 递归编译所有 .py 文件
        # exclude=["decompose/decompositon_methods.py"],  # 排除测试文件（可选）
        compiler_directives={
            'language_level': "3",
            'embedsignature': True,  # 保留函数签名
        },
        nthreads=4,  # 多线程加速编译（可选）
    ),
    # script_args=["build_ext", "--inplace"],
)
