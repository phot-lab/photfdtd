import numpy as np
import scipy.sparse as sps
import time
import math
from photfdtd import constants


def calculate_s(vect, k0=None, n=1, sigmaE_max=None):
    # 计算参数s
    # TODO: 究竟如何处理sigmaE_max能让solve的结果与lumerical一致？
    # k0 *= 10 ** 6 # 以um为标准单位
    omega = constants.c * k0
    # sigmaE_max = 1
    if sigmaE_max is None:
        # 0.000001是反射系数R
        sigmaE_max = (3 / 2) * constants.eps0 * constants.c * n * math.log(1 / 1e-10 ) / max(abs(vect))
        # sigmaE_max = 40
        print(sigmaE_max)
    sigmaE = sigmaE_max * (vect / max(abs(vect))) ** 2

    # 测试
    # sigmaE *= 1e12
    # omega *= 1e-6

    return 1 - 1j * sigmaE / (omega * constants.eps0 * n ** 2)


def eigen_build(k0, n, dx, dy, x_boundary_low=None, y_boundary_low=None, x_thickness_low=0, y_thickness_low=0,
                x_boundary_high=None, y_boundary_high=None, x_thickness_high=0, y_thickness_high=0,
                background_index=1):
    """

    @param k0: 波矢（单位um）
    @param n: 折射率
    @param dx: x方向单位长度（um）
    @param dy: y方向单位长度（um）
    @param x_boundary: x边界条件 str = "zero", "pml"
    @param y_boundary: y边界条件
    @param thickness: 边界厚度
    @return:
    """
    # TODO: 周期边界条件、对称边界条件
    # 关于pml边界的部分：Chin-Ping Yu and Hung-Chun Chang, "Yee-mesh-based finite difference eigenmode solver with
    # PML absorbing boundary conditions for optical waveguides and photonic crystal fibers,"
    # Opt. Express 12, 6165-6177 (2004) https://doi.org/10.1364/OPEX.12.006165
    # 添加于2023.12.03 by JiaTao
    # 似乎我们设置的xpml边界被放在了y方向，而ypml边界放在了x方向，不知道原因。因此我们只是简单交换xthickness与ythickness
    # FIXME: 根据文献，Ax和Bx应该是不一样的
    x_thickness_low, x_thickness_high, x_boundary_low, x_boundary_high, y_thickness_low, y_thickness_high, \
    y_boundary_low, y_boundary_high = y_thickness_low, y_thickness_high, y_boundary_low, y_boundary_high, \
                                      x_thickness_low, x_thickness_high, x_boundary_low, x_boundary_high

    # lets find out size of grid and construct some finite difference operators
    # These can take different forms depending on the user inputed boundarys
    # These operators also need boundaries
    nx, ny, dummy = np.shape(n)
    print('Assembling matrix for {} grid points...\n'.format(nx * ny))

    # construct finite difference operators single row of FD grid
    # Ax_temp = ( - np.eye(nx, k = 0) + np.eye(nx, k = 1) ) / dx
    # Ax = sps.block_diag([Ax_temp for i in range(ny)], format='csr')
    Ax = (- sps.eye(nx * ny, k=0, format="csr") + sps.eye(nx * ny, k=1, format="csr")) / dx
    Ay = (- sps.eye(nx * ny, k=0, format="csr") + sps.eye(nx * ny, k=nx, format="csr")) / dy
    # if x_boundary_low or x_boundary_high == 'periodic':
    #     pass
    #     # Ux_temp[nx - 1, 0] = 1. / dx
    #
    # if y_boundary_low or y_boundary_high == 'periodic':
    #     pass
    #     # This boundary needs a bit more thought although my intuition says its
    #     # just a wrap around
    #     Ay = Ay + sps.eye(nx * ny, k=-(nx - 1) * ny) / dy

    # This statement is kind of confusing but is the equivilent to doing a tensor
    # contraction. So each row operation is apended to the diagonals of a larger
    # matrix so we can operate on the whole grid at once.
    # sps.block_diag：从提供的矩阵构建对角稀疏矩阵。 即将矩阵一个接一个放在对角线上，与spdiags不一样
    # 这是为了将非方阵转为方阵

    if x_boundary_low or x_boundary_high or y_boundary_low or y_boundary_high == "pml":
        Ax = Ax.astype("complex")
        Ay = Ay.astype("complex")

        Cx = -Ax.transpose()
        Cy = -Ay.transpose()
        # 处理x_boundary
        if x_boundary_low == "pml":
            s = calculate_s(vect=np.arange(x_thickness_low - 0.5, -0.5, -1.0) * dx, k0=k0, n=background_index)
            s_for_C = calculate_s(vect=np.arange(x_thickness_low, 0, -1.0) * dx, k0=k0, n=background_index)
            for i in range(nx):
                Ax[nx * i: nx * i + x_thickness_low, :] = Ax[nx * i: nx * i + x_thickness_low, :] / s[:, np.newaxis]
                Cx[nx * i: nx * i + x_thickness_low, :] = Cx[nx * i: nx * i + x_thickness_low, :] / s_for_C[:,
                                                                                                    np.newaxis]

        if x_boundary_high == "pml":
            s = calculate_s(vect=np.arange(x_thickness_high - 0.5, -0.5, -1.0) * dx, k0=k0, n=background_index)
            s_for_C = calculate_s(vect=np.arange(x_thickness_high, 0, -1.0) * dx, k0=k0, n=background_index)
            s_flip = np.flip(s)
            s_for_C_flip = np.flip(s_for_C)
            for i in range(nx):
                Ax[nx * (i + 1) - x_thickness_high: nx * (i + 1), :] = Ax[nx * (i + 1) - x_thickness_high: nx * (i + 1),
                                                                       :] / s_flip[
                                                                            :,
                                                                            np.newaxis]
                Cx[nx * (i + 1) - x_thickness_high: nx * (i + 1), :] = Cx[nx * (i + 1) - x_thickness_high: nx * (i + 1),
                                                                       :] / s_for_C_flip[
                                                                            :,
                                                                            np.newaxis]

        # 处理y_boundary
        if y_boundary_low == "pml":
            s = calculate_s(vect=np.arange(y_thickness_low - 0.5, -0.5, -1.0) * dy, k0=k0, n=background_index)
            s_for_C = calculate_s(vect=np.arange(y_thickness_low, 0, -1.0) * dy, k0=k0, n=background_index)
            for i in range(nx):
                if i < y_thickness_low:
                    Ay[nx * i:nx * (i + 1), :] = Ay[nx * i:nx * (i + 1), :] / s[i]
                    Cy[nx * i:nx * (i + 1), :] = Cy[nx * i:nx * (i + 1), :] / s_for_C[i]

        if y_boundary_high == "pml":
            s = calculate_s(vect=np.arange(y_thickness_high - 0.5, -0.5, -1.0) * dy, k0=k0, n=background_index)
            s_for_C = calculate_s(vect=np.arange(y_thickness_high, 0, -1.0) * dy, k0=k0, n=background_index)
            for i in range(nx):
                if i > ny - y_thickness_high - 1:
                    Ay[nx * i:nx * (i + 1), :] = Ay[nx * i:nx * (i + 1), :] / s[ny - i - 1]
                    Cy[nx * i:nx * (i + 1), :] = Cy[nx * i:nx * (i + 1), :] / s_for_C[ny - i - 1]

        # Bx = Ax
        # By = Ay

        # 处理Cx
        # s = calculate_s(vect=np.arange(x_thickness, 0, -1.0), k0=k0)
        # s_flip = np.flip(s)
        # for i in range(nx):
        #     Cx[nx * i: nx * i + x_thickness, :] = Cx[nx * i: nx * i + x_thickness, :] / s[:, np.newaxis]
        #     Cx[nx * (i + 1) - x_thickness: nx * (i + 1), :] = Cx[nx * (i + 1) - x_thickness: nx * (i + 1), :] / s_flip[
        #                                                                                                         :,
        #                                                                                                         np.newaxis]

        # 处理Cy
        # s = calculate_s(vect=np.arange(y_thickness, 0, -1.0), k0=k0)
        # for i in range(nx):
        #     if i < y_thickness:
        #         Cy[nx * i:nx * (i + 1), :] = Cy[nx * i:nx * (i + 1), :] / s[i]
        #     elif i > ny - y_thickness - 1:
        #         Cy[nx * i:nx * (i + 1), :] = Cy[nx * i:nx * (i + 1), :] / s[ny - i - 1]

        # Dx = Cx
        # Dy = Cy

        I = sps.eye(nx * ny, dtype="complex")

        # We then build relative permitivity tensors
        epsx = np.empty(nx * ny, dtype="complex")
        epsy = np.empty(nx * ny, dtype="complex")
        epszi = np.empty(nx * ny, dtype="complex")

    # %% Now we can construct all the other operators
    else:
        # 零值边界条件
        Cx = - Ax.transpose()
        Cy = - Ay.transpose()

        I = sps.eye(nx * ny)

        # We then build relative permitivity tensors
        epsx = np.empty(nx * ny, dtype=n.dtype)
        epsy = np.empty(nx * ny, dtype=n.dtype)
        epszi = np.empty(nx * ny, dtype=n.dtype)

    count = 0
    for j in range(0, ny):
        for i in range(0, nx):
            epsx[count] = n[i, j, 0] ** 2
            epsy[count] = n[i, j, 1] ** 2
            epszi[count] = 1. / n[i, j, 2] ** 2
            count = count + 1
    # 把eps展成了一维数组，再用spdiags把它们放在对角线上

    epsx = sps.spdiags(epsx, 0, nx * ny, nx * ny, format='csr')
    epsy = sps.spdiags(epsy, 0, nx * ny, nx * ny, format='csr')
    epszi = sps.spdiags(epszi, 0, nx * ny, nx * ny, format='csr')

    # Now we need to construct the full operator matrices
    t = time.time()
    Pxx = (- Ax * epszi * Cy * Cx * Ay / k0 ** 2
           + (k0 ** 2 * I + Ax * epszi * Cx) * (epsx + Cy * Ay / k0 ** 2))

    Pyy = (- Ay * epszi * Cx * Cy * Ax / k0 ** 2
           + (k0 ** 2 * I + Ay * epszi * Cy) * (epsy + Cx * Ax / k0 ** 2))

    Pxy = (Ax * epszi * Cy * (epsy + Cx * Ax / k0 ** 2)
           - (k0 ** 2 * I + Ax * epszi * Cx) * Cy * Ax / k0 ** 2)

    Pyx = (Ay * epszi * Cx * (epsx + Cy * Ay / k0 ** 2)
           - (k0 ** 2 * I + Ay * epszi * Cy) * Cx * Ay / k0 ** 2)

    print('and we are done (after {} secs).'.format(time.time() - t))

    # Ok we should be able to do the final assembly now !!!
    P = sps.vstack([sps.hstack([Pxx, Pxy]), sps.hstack([Pyx, Pyy])])

    return P, {'epsx': epsx, 'epsy': epsy, 'epszi': epszi,
               'ux': Ax, 'uy': Ay, 'vx': Cx, 'vy': Cy}
    # solve(P, )


def solve(P, beta_trial, E_trial=None, neigs=1):
    """
	Solves eigenproblem and returns beta and the transverse E-feilds
	"""
    print('Solving eigenmodes on CPU')
    t = time.time()

    beta_squared, E = linalg.eigs(P, neigs, sigma=beta_trial ** 2, v0=E_trial)

    Ex, Ey = np.split(E, 2)

    Ex, Ey = np.transpose(Ex), np.transpose(Ey)
    print('{} secs later we have the final solution.'.format(time.time() - t))

    return beta_squared ** 0.5, Ex, Ey
