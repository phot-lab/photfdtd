import numpy as np

class OverlapCalculator:
    def __init__(self, grid_spacing, E1_data, E2_data, neigs):
        self.grid_spacing = grid_spacing
        self.E1_data = E1_data
        self.E2_data = E2_data
        self.neigs = neigs
        self.extract_and_calculate_overlap()

    def calculate_overlap_integral(self, E1_x, H1_x, E2_x, H2_x, E1_y, H1_y, E2_y, H2_y):
        # 计算点乘
        I_1 = E1_x * np.conjugate(H2_y) - E1_y * np.conjugate(H2_x)
        I_2 = E2_x * np.conjugate(H1_y) - E2_y * np.conjugate(H1_x)
        I_3 = E1_x * np.conjugate(H1_y) - E1_y * np.conjugate(H1_x)
        I_4 = E2_x * np.conjugate(H2_y) - E2_y * np.conjugate(H2_x)

        # 计算积分
        I1 = np.sum(I_1) * self.grid_spacing**2
        I2 = np.sum(I_2) * self.grid_spacing**2
        I3 = np.sum(I_3) * self.grid_spacing**2
        I4 = np.sum(I_4) * self.grid_spacing**2

        # 计算重叠积分
        overlap = np.abs(np.real((I1 * I2) / I3) / np.real(I4))

        return overlap

    def extract_and_calculate_overlap(self):
        # 提取电场和磁场分量
        E1_x_modes = [self.E1_data["Ex"][i] for i in range(self.neigs)]
        E1_y_modes = [self.E1_data["Ey"][i] for i in range(self.neigs)]
        H1_x_modes = [self.E1_data["Hx"][i] for i in range(self.neigs)]
        H1_y_modes = [self.E1_data["Hy"][i] for i in range(self.neigs)]
        E2_x_modes = [self.E2_data["Ex"][i] for i in range(self.neigs)]
        E2_y_modes = [self.E2_data["Ey"][i] for i in range(self.neigs)]
        H2_x_modes = [self.E2_data["Hx"][i] for i in range(self.neigs)]
        H2_y_modes = [self.E2_data["Hy"][i] for i in range(self.neigs)]

        # 计算所有组合的重叠积分
        for i in range(self.neigs):
            for j in range(self.neigs):
                overlap = self.calculate_overlap_integral(
                    E1_x_modes[i], H1_x_modes[i],
                    E2_x_modes[j], H2_x_modes[j],
                    E1_y_modes[i], H1_y_modes[i],
                    E2_y_modes[j], H2_y_modes[j]
                )
                print(f"Overlap integral between mode {i+1} and mode {j+1}: {overlap}")
