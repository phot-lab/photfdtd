import numpy as np
import math
from photfdtd import Grid, Fiber, Solve

class IntercoreCoupling:
    def __init__(self, grid_spacing, Em_data, En_data, lam, neigs, refractive_index_data_m, background_index, m, n):
        self.grid_spacing = grid_spacing
        self.Em_data = Em_data
        self.En_data = En_data
        self.lam = lam
        self.neigs = neigs
        self.refractive_index_data_m = refractive_index_data_m
        self.background_index = background_index
        self.m = m
        self.n = n

    def calculate_intercore_coupling(self, Em_x, Hm_x, Em_y, Hm_y, Em_z, Hm_z, En_x, Hn_x, En_y, Hn_y, En_z, Hn_z):
        I_1 = np.conjugate(Em_x) * En_x + np.conjugate(Em_y) * En_y + np.conjugate(Em_z) * En_z
        I_2 = Em_x * np.conjugate(Hm_y) - Em_y * np.conjugate(Hm_x) + np.conjugate(Em_x) * Hm_y - np.conjugate(Em_y) * Hm_x

        Nm = self.refractive_index_data_m
        background_n = np.ones_like(Nm) * self.background_index
        I_5 = Nm**2 - background_n**2



        I_5_sliced = I_5[:, :, 0, 0]#确保Shape of I_1: (250, 250)与Shape of I_5: (250, 250, 1, 3)形状匹配
        I3 = np.sum(I_1 * I_5_sliced) * self.grid_spacing**2
        I4 = np.sum(I_2) * self.grid_spacing**2

        omega = 2 * math.pi * 3e8 / self.lam
        vp = 8.854187817e-12

        I1 = I3 * omega * vp
        I2 = 2 * I4

        coupling = I1 / I2
        return coupling

    def extract_and_calculate_overlap(self):
        Em_x_modes = [self.Em_data["Ex"][i] for i in range(self.neigs)]
        Em_y_modes = [self.Em_data["Ey"][i] for i in range(self.neigs)]
        Em_z_modes = [self.Em_data["Ez"][i] for i in range(self.neigs)]
        Hm_x_modes = [self.Em_data["Hx"][i] for i in range(self.neigs)]
        Hm_y_modes = [self.Em_data["Hy"][i] for i in range(self.neigs)]
        Hm_z_modes = [self.Em_data["Hz"][i] for i in range(self.neigs)]

        En_x_modes = [self.En_data["Ex"][i] for i in range(self.neigs)]
        En_y_modes = [self.En_data["Ey"][i] for i in range(self.neigs)]
        En_z_modes = [self.En_data["Ez"][i] for i in range(self.neigs)]
        Hn_x_modes = [self.En_data["Hx"][i] for i in range(self.neigs)]
        Hn_y_modes = [self.En_data["Hy"][i] for i in range(self.neigs)]
        Hn_z_modes = [self.En_data["Hz"][i] for i in range(self.neigs)]

        for i in range(self.neigs):
            for j in range(self.neigs):
                coupling = self.calculate_intercore_coupling(
                    Em_x_modes[i], Hm_x_modes[i],
                    Em_y_modes[i], Hm_y_modes[i],
                    Em_z_modes[i], Hm_z_modes[i],
                    En_x_modes[j], Hn_x_modes[j],
                    En_y_modes[j], Hn_y_modes[j],
                    En_z_modes[j], Hn_z_modes[j]
                )
                print(f"纤芯{self.m}的模式 {i+1} 和 纤芯{self.n}的模式 {j+1} 之间的耦合系数 (k{self.m}{self.n}): {coupling}")

    @staticmethod
    def calculate_modes(foldername, fiber, background_index, neigs):
        grid = Grid(
            grid_xlength=125e-6, grid_ylength=125e-6, grid_zlength=1, grid_spacing=500e-9,
            permittivity=background_index ** 2, foldername=foldername
        )

        grid.add_object(fiber)

        refractive_index_distribution = grid.get_refractive_index_distribution()
        solve = Solve(grid=grid, axis="z", filepath=grid.folder, index=0)
        solve.plot()
        grid.save_fig(axis="z", axis_number=0)

        data = solve.calculate_mode(
            lam=1550e-9, neff=1.4504, neigs=neigs, x_boundary_low="pml", y_boundary_low="pml",
            x_boundary_high="pml", y_boundary_high="pml", background_index=background_index
        )
        Solve.draw_mode(filepath=solve.filepath, data=data, content="real_part",number=50)

        return data, refractive_index_distribution

