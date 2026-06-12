import pytest as _pytest
import numpy as _np

def roll_matrix_bdsim(tilt):
    """
    BDSIM convention:
    positive tilt = clockwise looking along the beam.
    """
    
    c = _np.cos(tilt)
    s = _np.sin(tilt)

    T = _np.array([
        [ c, 0,  s, 0, 0, 0],
        [ 0, c,  0, s, 0, 0],
        [-s, 0,  c, 0, 0, 0],
        [ 0,-s,  0, c, 0, 0],
        [ 0, 0,  0, 0, 1, 0],
        [ 0, 0,  0, 0, 0, 1],
    ])
    
    return T

def sec(x):
    return 1.0 / _np.cos(x)

def sym_set(T, i, j, k, value):
    if j == k:
        T[i, j, k] = value
    else:
        T[i, j, k] = 0.5 * value
        T[i, k, j] = 0.5 * value


def edge_R_matrix(rho, psi=0.0, fint=0.0, hgap=0.0, hgap_is_half_gap=True):
    """
    First-order dipole edge/fringe matrix.
    """
    R = _np.eye(6)
    h = 1.0 / rho

    psi_eff = effective_pole_face_angle(
        rho,
        psi,
        fint=fint,
        hgap=hgap,
        hgap_is_half_gap=hgap_is_half_gap,
    )

    R[1, 0] = h * _np.tan(psi)
    R[3, 2] = -h * _np.tan(psi_eff)
    
    return R
    
def fringe_T_entrance(rho, psi1, R1=_np.inf, fintK2=0.0):
    """
    Second-order TRANSPORT coefficients for entrance dipole fringe field.
    h  = 1/rho, reference curvature inside dipole
    psi1 = entrance pole-face angle
    R1 = entrance pole-face curvature radius
    """
    T = _np.zeros((6, 6, 6))
    h=1/rho
    tan = _np.tan
    secv = sec(psi1)
    K1 = fintK2
    invR1 = 0.0 if _np.isinf(R1) else 1.0 / R1

    sym_set(T, 0, 0, 0, -0.5 * h * tan(psi1)**2)     # T111
    sym_set(T, 1, 0, 1, +0.5 * h * tan(psi1)**2)     # T212
    sym_set(T, 1, 1, 0, +0.5 * h * tan(psi1)**2)     # same physical term

    sym_set(T, 1, 0, 0, +0.5 * h * invR1 * secv**3 + K1 * tan(psi1))  # T211
    sym_set(T, 1, 2, 2, -0.5 * h * invR1 * secv**3
                         - K1 * tan(psi1)
                         + 0.5 * h**2 * tan(psi1) * (1 + secv**2))    # T233

    sym_set(T, 2, 0, 2, +0.5 * h * tan(psi1)**2)     # T313

    sym_set(T, 3, 0, 2, -0.5 * h * invR1 * secv**3 - K1 * tan(psi1))  # T413
    sym_set(T, 3, 0, 3, -0.5 * h * tan(psi1)**2)     # T414
    sym_set(T, 3, 1, 2, -0.5 * h * secv**2)          # T423

    return T
    
def fringe_T_exit(rho, psi2, R2=_np.inf, fintK2=0.0): 
    """
    Second-order TRANSPORT coefficients for exit dipole fringe field.
    """
    h= 1/rho
    
    T = _np.zeros((6, 6, 6))
    K1 = fintK2
    tan = _np.tan
    secv = sec(psi2)

    invR2 = 0.0 if _np.isinf(R2) else 1.0 / R2

    sym_set(T, 0, 0, 0, +0.5 * h * tan(psi2)**2)     # T111
    sym_set(T, 1, 0, 1, -0.5 * h * tan(psi2)**2)     # T212

    sym_set(T, 1, 0, 0, +0.5 * h * invR2 * secv**3
                         + K1 * tan(psi2)
                         - 0.5 * h**2 * tan(psi2)**3)                 # T211

    sym_set(T, 1, 2, 2, -0.5 * h * invR2 * secv**3
                         - K1 * tan(psi2)
                         - 0.5 * h**2 * tan(psi2)**3)                 # T233

    sym_set(T, 2, 0, 2, -0.5 * h * tan(psi2)**2)     # T313

    sym_set(T, 3, 0, 2, -0.5 * h * invR2 * secv**3
                         - K1 * tan(psi2)
                         + 0.5 * h**2 * tan(psi2) * secv**2)          # T413

    sym_set(T, 3, 0, 3, +0.5 * h * tan(psi2)**2)     # T414
    sym_set(T, 3, 1, 2, +0.5 * h * secv**2)          # T423

    return T
    
def c_func(k2, L):
    if abs(k2) < 1e-15:
        return 1.0

    if k2 > 0.0:
        k = _np.sqrt(k2)
        return _np.cos(k * L)

    k = _np.sqrt(-k2)
    return _np.cosh(k * L)


def s_func(k2, L):
    if abs(k2) < 1e-15:
        return L

    if k2 > 0.0:
        k = _np.sqrt(k2)
        return _np.sin(k * L) / k

    k = _np.sqrt(-k2)
    return _np.sinh(k * L) / k


def d_func(k2, L):
    if abs(k2) < 1e-15:
        return 0.5 * L**2

    return (1.0 - c_func(k2, L)) / k2


def f_func(k2, L):
    if abs(k2) < 1e-15:
        return L**3 / 6.0

    return (L - s_func(k2, L)) / k2
    
def effective_pole_face_angle(rho, psi, fint=0.0, hgap=0.0, hgap_is_half_gap=True):
    h = 1.0 / rho
    g = 2.0 * hgap if hgap_is_half_gap else hgap

    return psi - h * g * fint * (1.0 + _np.sin(psi)**2)
    
def edge_T_matrix(
    rho,
    psi=0.0,
    fint=0.0,
    hgap=0.0,
    pole_face_curvature=0.0,
    fintK2=0.0,
    entrance=True,
    hgap_is_half_gap=True,
):
    psi_eff = effective_pole_face_angle(
        rho,
        psi,
        fint=fint,
        hgap=hgap,
        hgap_is_half_gap=hgap_is_half_gap,
    )

    Rcurv = _np.inf if abs(pole_face_curvature) < 1e-15 else 1.0 / pole_face_curvature

    if entrance:
        return fringe_T_entrance(rho, psi_eff, R1=Rcurv, fintK2=fintK2)
    else:
        return fringe_T_exit(rho, psi_eff, R2=Rcurv, fintK2=fintK2)

def sector_body_T_minimal(length, angle, body_k1=0.0):
    rho = length / angle
    h = 1.0 / rho

    K1 = body_k1
    K2 = 0.0

    kx2 = h**2 + K1
    ky2 = -K1

    cx = c_func(kx2, length)
    sx = s_func(kx2, length)
    dx = d_func(kx2, length)

    cy = c_func(ky2, length)
    sy = s_func(ky2, length)

    T = _np.zeros((6, 6, 6))

    A = K2 + 2.0 * h * K1

    sym_set(T, 0, 0, 0, -(1.0 / 6.0) * A * (sx**2 + dx) - 0.5 * h * kx2 * sx**2)
    sym_set(T, 0, 0, 1, -(1.0 / 6.0) * A * sx * dx + 0.5 * h * sx * cx)
    sym_set(T, 0, 1, 1, -(1.0 / 6.0) * A * dx**2 + 0.5 * h * cx * dx)

    sym_set(T, 1, 0, 0, -(1.0 / 6.0) * A * sx * (1.0 + 2.0 * cx))
    sym_set(T, 1, 0, 1, -(1.0 / 6.0) * A * dx * (1.0 + 2.0 * cx))
    sym_set(T, 1, 1, 1, -(1.0 / 3.0) * A * sx * dx - 0.5 * h * sx)

    sym_set(T, 0, 2, 2, 0.5 * K1 * K2 * 0.0 + 0.5 * (K2 + h * K1) * dx)
    sym_set(T, 0, 2, 3, 0.5 * K2 * 0.0)
    sym_set(T, 0, 3, 3, 0.5 * K2 * 0.0 - 0.5 * h * dx)

    sym_set(T, 1, 2, 2, 0.5 * K1 * K2 * 0.0 + 0.5 * (K2 + h * K1) * sx)
    sym_set(T, 1, 2, 3, 0.5 * K2 * 0.0)
    sym_set(T, 1, 3, 3, 0.5 * K2 * 0.0 - 0.5 * h * sx)


    sym_set(T, 2, 0, 2, 0.5 * h * K1 * sx * sy)
    sym_set(T, 2, 0, 3, 0.5 * h * sx * cy)
    sym_set(T, 2, 1, 2, 0.5 * h * K1 * dx * sy)
    sym_set(T, 2, 1, 3, 0.5 * h * dx * cy)

    sym_set(T, 3, 0, 2, 0.5 * (K2 + h * K1) * sx * cy)
    sym_set(T, 3, 0, 3, 0.5 * (K2 + h * K1) * sx * sy)
    sym_set(T, 3, 1, 2, 0.5 * (K2 + h * K1) * dx * cy)
    sym_set(T, 3, 1, 3, 0.5 * (K2 + h * K1) * dx * sy)

    return T
    
def compose_order2(RB, TB, RA, TA):
    """
    Return C = B ∘ A.
    X1 = RA X0 + TA(X0,X0)
    X2 = RB X1 + TB(X1,X1)
    """
    RC = RB @ RA

    TC = _np.einsum("ia,ajk->ijk", RB, TA)
    TC += _np.einsum("iab,aj,bk->ijk", TB, RA, RA)

    return RC, TC
    
def rotate_order2_map_lab_to_magnet(Rm, Tm, T_l2m):
    """
    T_l2m maps lab -> magnet coordinates.
    Rm, Tm are the local magnet-frame map.

    Returns Rl, Tl in lab coordinates.
    """
    T_m2l = _np.linalg.inv(T_l2m)

    Rl = T_m2l @ Rm @ T_l2m

    Tl = _np.einsum(
        "ia,abc,bj,ck->ijk",
        T_m2l,
        Tm,
        T_l2m,
        T_l2m
    )

    return Rl, Tl

def rotated_matrix(rho, ref_rmatrix, tilt=0.0, e1=0.0, e2=0.0):

    R_in   = edge_R_matrix(rho, e1)
    R_body = ref_rmatrix
    R_out  = edge_R_matrix(rho, e2)

    R_magnet = R_out @ R_body @ R_in

    T = roll_matrix_bdsim(tilt)

    return _np.linalg.inv(T)  @ R_magnet @ T
    

def tensor_to_pybdsim_tmap(T):
    """
    Convert T[i,j,k] to pybdsim-style 4 x 9 quadratic map.
    """
    return _np.array([
        [
            T[i,0,0],  # x²
            T[i,0,1],  # x*xp
            T[i,0,2],  # x*y
            T[i,0,3],  # x*yp
            T[i,2,1],  # y*xp
            T[i,2,2],  # y²
            T[i,2,3],  # y*yp
            T[i,1,1],  # xp²
            T[i,3,3],  # yp²
        ]
        for i in range(4)
    ])
