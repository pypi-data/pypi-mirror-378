import numpy as np
from typing import Union

ATOL_DEFAULT = 1e-8
RTOL_DEFAULT = 1e-5

def is_unitary_matrix(mat:Union[list, np.ndarray], rtol:float=RTOL_DEFAULT, atol:float=ATOL_DEFAULT)->bool:
    """Test if an array is a unitary matrix."""
    mat = np.array(mat)
    # Compute A^dagger.A and see if it is identity matrix
    mat = np.conj(mat.T).dot(mat)
    return is_identity_matrix(mat, ignore_phase=False, rtol=rtol, atol=atol)

def is_identity_matrix(mat:Union[list, np.ndarray], ignore_phase:bool=False, rtol:float=RTOL_DEFAULT, atol:float=ATOL_DEFAULT)->bool:
    """Test if an array is an identity matrix."""
    if atol is None:
        atol = ATOL_DEFAULT
    if rtol is None:
        rtol = RTOL_DEFAULT
    mat = np.array(mat)
    if mat.ndim != 2:
        return False
    if ignore_phase:
        # If the matrix is equal to an identity up to a phase, we can
        # remove the phase by multiplying each entry by the complex
        # conjugate of the phase of the [0, 0] entry.
        theta = np.angle(mat[0, 0])
        mat = np.exp(-1j * theta) * mat
    # Check if square identity
    iden = np.eye(len(mat))
    return np.allclose(mat, iden, rtol=rtol, atol=atol)
