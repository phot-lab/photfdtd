import numpy as np


class Arc:

    # TODO: 由于在设置的波导中，非波导部分折射率都为1，因此目前设置空间折射率来改变包层折射率并无意义
    """四分之一圆环
    outer_radius: 外环半径
    zlength: 波导厚度
    x,y,z: 位置坐标（通常是矩形区域最靠近原点的点）
    width: 波导宽度
    refractive_index:折射率
    name: 名称
    flag: 等于1，2，3，4，分别表征四个方向：左下，左上，右下，右上
    """

    def __init__(
        self,
        outer_radius: int,
        zlength: int,
        x: int,
        y: int,
        z: int,
        width: int,
        refractive_index: float,
        name: str,
        flag: int,
    ) -> None:

        self.outer_radius = outer_radius
        self.zlength = zlength
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.refractive_index = refractive_index
        self.name = name
        self.flag = flag

    def set_grid(self) -> dict:
        """
        输入波导规格，返回字典，包含名字、介电常数矩阵（规格为[ylength,xlength,zlength]）、区域规格、位置坐标、flag(=1表示形状左上至右下，=-1表示形状从左下到右上)
        :return:
        """
        x = y = np.linspace(1, self.outer_radius, self.outer_radius)
        X, Y = np.meshgrid(x, y, indexing="ij")  # indexing = 'ij'很重要

        if self.flag == 1:
            # flag=1, 圆心在左下
            m = (X - self.outer_radius) ** 2 + Y**2 >= (self.outer_radius - self.width) ** 2
            m1 = (X - self.outer_radius) ** 2 + Y**2 <= self.outer_radius**2

        elif self.flag == 2:
            # flag=2, 圆心在左上
            m = X**2 + Y**2 >= (self.outer_radius - self.width) ** 2
            m1 = X**2 + Y**2 <= self.outer_radius**2

        elif self.flag == 3:
            # flag=3, 圆心在右上
            m = X**2 + (Y - self.outer_radius) ** 2 >= (self.outer_radius - self.width) ** 2
            m1 = X**2 + (Y - self.outer_radius) ** 2 <= self.outer_radius**2

        elif self.flag == 4:
            # flag=4, 圆心在右下
            m = (X - self.outer_radius) ** 2 + (Y - self.outer_radius) ** 2 >= (self.outer_radius - self.width) ** 2
            m1 = (X - self.outer_radius) ** 2 + (Y - self.outer_radius) ** 2 <= self.outer_radius**2

        for i in range(self.outer_radius):
            for j in range(self.outer_radius):
                if m1[i, j] != m[i, j]:
                    m[i, j] = 0

        permittivity = np.ones((self.outer_radius, self.outer_radius, self.zlength))
        permittivity += m[:, :, None] * (self.refractive_index**2 - 1)

        result = {
            "name": self.name,
            "permittivity": permittivity,
            "size": (self.outer_radius, self.outer_radius, self.zlength),
            "position": (self.x, self.y, self.z),
            "flag": self.flag,
        }

        return result


if __name__ == "__main__":

    arc = Arc(outer_radius=20, zlength=1, x=1, y=1, z=1, width=2, refractive_index=3.47, name="arc1", flag=4)
    result = arc.set_grid()
    print(result["size"][0])
