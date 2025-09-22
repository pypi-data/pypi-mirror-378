import copy, itertools
import numpy as np
from typing import Union
from tgqSim.utils.tgq_expection import TgqSimError as CircuitError

class Bit:
    __slots__ = {"_register", "_index", "_hash", "_repr"}
    
    def __init__(self, register=None, index=None) -> None:
        """
        Create a new genertic bit.

        Args:
            register (_type_, optional): 寄存器. Defaults to None.
            index (_type_, optional): 索引. Defaults to None.
        """
        if (register, index) == (None, None):
            self._register = None
            self._index = None
            self._hash = object.__hash__(self)
        else:
            try:
                index = int(index)
            except Exception as ex:
                raise CircuitError(f"index needs to be castable to an int: type {type(index)} was provided") from ex
            if index < 0:
                index += register.size
            if index >= register.size:
                raise CircuitError(f"index {index} out of range for register of size {register.size}")
        
        self._register = register
        self._index = index
        # self._hash = hash((self._register, self._index))
        self._hash = hash(self._index)
        self._repr = f"{self.__class__.__name__}({self._register}, {self._index})"
    
    def register(self):
        """Get the register of this bit."""
        if (self._register, self._index) == (None, None):
            raise CircuitError("Attempt to query register of a new-style Bit.")
        return self._register
    
    def index(self):
        """Get the index of this bit."""
        if (self._register, self._index) == (None, None):
            raise CircuitError("Attempt to query index of a new-style Bit.")
        return self._index
    
    def __repr__(self) -> str:
        if (self._register, self._index) == (None, None):
            return object.__repr__(self)
        return self._repr
    
    def __hash__(self) -> int:
        return self._hash
    
    def __eq__(self, other: 'Bit') -> bool:
        if (self._register, self._index) == (None, None):
            return other is self
        try:
            return self._index == other._index
        except AttributeError:
            return False
    
    def __gt__(self, other) -> bool:
        if (self._register, self._index) == (None, None):
            return False
        try:
            return self._index > other._index
        except AttributeError:
            return False
    
    def __lt__(self, other) -> bool:
        if (self._register, self._index) == (None, None):
            return False
        try:
            return self._index < other._index
        except AttributeError:
            return False
    
    def __copy__(self):
        return self
    
    def __deepcopy__(self, memo=None):
        if (self._register, self._index) == (None, None):
            return self
        
        bit = type(self).__new__(type(self))
        bit._register = copy.deepcopy(self._register, memo)
        bit._index = self._index
        bit._hash = self._hash
        bit._repr = self._repr
        return bit

class Qubit(Bit):
    """A quantum bit."""
    __slots__ = ()
    
    def __init__(self, register=None, index=None) -> None:
        """
        Create a new quantum bit.

        Args:
            register (_type_, optional): 寄存器. Defaults to None.
            index (_type_, optional): 索引. Defaults to None.
        """
        if (register is None) or (isinstance(register, QuantumRegister)):
            super().__init__(register, index)
        else:
            raise CircuitError("Qubit must be in a QuantumRegister. Register provided: %s" % type(register).__name__)


class Register:
    """Implement a generic register.

    .. note::
        This class should not be instantiated directly. This is just a superclass
        for :class:`~.ClassicalRegister` and :class:`~.QuantumRegister`.

    """

    __slots__ = ["_name", "_size", "_bits", "_bit_indices", "_hash", "_repr"]

    # Counter for the number of instances in this class.
    instances_counter = itertools.count()
    # Prefix to use for auto naming.
    prefix = "reg"
    bit_type = None

    def __init__(self, size: Union[list, None] = None, name: Union[list, None] = None):
        """Create a new generic register.

        Either the ``size`` or the ``bits`` argument must be provided. If
        ``size`` is not None, the register will be pre-populated with bits of the
        correct type.

        Args:
            size (int): Optional. The number of bits to include in the register.
            name (str): Optional. The name of the register. If not provided, a
               unique name will be auto-generated from the register type.
            bits (list[Bit]): Optional. A list of Bit() instances to be used to
               populate the register.

        Raises:
            CircuitError: if both the ``size`` and ``bits`` arguments are
                provided, or if neither are.
            CircuitError: if ``size`` is not valid.
            CircuitError: if ``name`` is not a valid name according to the
                OpenQASM spec.
            CircuitError: if ``bits`` contained duplicated bits.
            CircuitError: if ``bits`` contained bits of an incorrect type.
        """

        try:
            valid_size = size == int(size)
        except (ValueError, TypeError):
            valid_size = False

        if not valid_size:
            raise CircuitError(
                "Register size must be an integer. (%s '%s' was provided)"
                % (type(size).__name__, size)
            )
        size = int(size)  # cast to int

        if size < 0:
            raise CircuitError(
                "Register size must be non-negative (%s '%s' was provided)"
                % (type(size).__name__, size)
            )

        # validate (or cast) name
        if name is None:
            name = "%s%i" % (self.prefix, next(self.instances_counter))
        else:
            try:
                name = str(name)
            except Exception as ex:
                raise CircuitError(
                    "The circuit name should be castable to a string "
                    "(or None for autogenerate a name)."
                ) from ex

        self._name = name
        self._size = size

        self._hash = hash((type(self), self._name, self._size))
        self._repr = "%s(%d, '%s')" % (self.__class__.__qualname__, self.size, self.name)
        
        self._bits = [self.bit_type(self, idx) for idx in range(size)]

        # Since the hash of Bits created by the line above will depend upon
        # the the hash of self, which is not guaranteed to have been initialized
        # first on deepcopying or on pickling, so defer populating _bit_indices
        # until first access.
        self._bit_indices = None

    @property
    def name(self):
        """Get the register name."""
        return self._name

    @property
    def size(self):
        """Get the register size."""
        return self._size

    def __repr__(self):
        """Return the official string representing the register."""
        return self._repr

    def __len__(self):
        """Return register size."""
        return self._size

    def __getitem__(self, key):
        """
        Arg:
            bit_type (Qubit or Clbit): a constructor type return element/s.
            key (int or slice or list): index of the bit to be retrieved.

        Returns:
            Qubit or Clbit or list(Qubit) or list(Clbit): a Qubit or Clbit instance if
            key is int. If key is a slice, returns a list of these instances.

        Raises:
            CircuitError: if the `key` is not an integer or not in the range `(0, self.size)`.
        """
        if not isinstance(key, (int, np.integer, slice, list)):
            raise CircuitError("expected integer or slice index into register")
        if isinstance(key, slice):
            return self._bits[key]
        elif isinstance(key, list):  # list of qubit indices
            if max(key) < len(self):
                return [self._bits[idx] for idx in key]
            else:
                raise CircuitError("register index out of range")
        else:
            return self._bits[key]

    def __iter__(self):
        for idx in range(self._size):
            yield self._bits[idx]

    def __contains__(self, bit):
        if self._bit_indices is None:
            self._bit_indices = {bit: idx for idx, bit in enumerate(self._bits)}

        return bit in self._bit_indices

    def index(self, bit):
        """Find the index of the provided bit within this register."""
        if self._bit_indices is None:
            self._bit_indices = {bit: idx for idx, bit in enumerate(self._bits)}

        try:
            return self._bit_indices[bit]
        except KeyError as err:
            raise ValueError(f"Bit {bit} not found in Register {self}.") from err

    def __eq__(self, other):
        """Two Registers are the same if they are of the same type
        (i.e. quantum/classical), and have the same name and size. Additionally,
        if either Register contains new-style bits, the bits in both registers
        will be checked for pairwise equality. If two registers are equal,
        they will have behave identically when specified as circuit args.

        Args:
            other (Register): other Register

        Returns:
            bool: `self` and `other` are equal.
        """
        if self is other:
            return True

        res = False
        if (
            type(self) is type(other)
            # and self._repr == other._repr
            and all(
                # For new-style bits, check bitwise equality.
                sbit == obit
                for sbit, obit in zip(self, other)
                if None in (sbit._register, sbit._index, obit._register, obit._index)
            )
        ):
            res = True
        return res

    def __hash__(self):
        """Make object hashable, based on the name and size to hash."""
        return self._hash

    def __getstate__(self):
        # Specifically exclude _bit_indices from pickled state as bit hashes
        # can in general depend on the hash of their containing register,
        # which may not have yet been initialized.
        return self._name, self._size, self._hash, self._repr, self._bits

    def __setstate__(self, state):
        self._name, self._size, self._hash, self._repr, self._bits = state
        self._bit_indices = None
    
    def resize(self, new_size: int) -> None:
        """Resize the register to a new size.

        Args:
            new_size (int): The new size of the register.

        Raises:
            CircuitError: if the new size is not valid.
        """
        if not isinstance(new_size, int) or new_size < 0:
            raise CircuitError("Register size must be non-negative.")
        
        old_size = self._size
        self._size = new_size
        if new_size == old_size:
            return
        if new_size > old_size:
            self._bits.extend([self.bit_type(self, idx) for idx in range(old_size, new_size)])
        else:
            self._bits = self._bits[:new_size]
        self._hash = hash((type(self), self._name, self._size))
        self._repr = "%s(%d, '%s')" % (self.__class__.__qualname__, self.size, self.name)
        self._bit_indices = None
    
    def __iadd__(self, num: int):
        """Add a number to the register size."""
        if not isinstance(num, int) or num < 0:
            raise CircuitError("Register size must be non-negative.")
        self.resize(self._size + num)
        return self
    
    def __isub__(self, num: int):
        """Subtract a number from the register size."""
        if not isinstance(num, int) or num < 0:
            raise CircuitError("Register size must be non-negative.")
        self.resize(self._size - num)
        return self

class QuantumRegister(Register):
    """Implement a quantum register."""

    # Counter for the number of instances in this class.
    instances_counter = itertools.count()
    # Prefix to use for auto naming.
    prefix = "q"
    bit_type = Qubit
    
class ClassicalRegister(Register):
    """Implement a classical register."""

    # Counter for the number of instances in this class.
    instances_counter = itertools.count()
    # Prefix to use for auto naming.
    prefix = "c"
    bit_type = Bit


if __name__ == "__main__":
    quantumReg = QuantumRegister(size=5, name="qreg")
    qubit = Qubit(register=quantumReg, index=4)
    print(qubit.index())
    print(type(quantumReg[4]))