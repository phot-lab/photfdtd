import utils
from photfdtd import Arc

if __name__ == "__main__":

    arc = Arc(outer_radius=20, zlength=1, x=40, y=40, z=1, width=2, refractive_index=3.47, name="arc", direction=4)

    arc.set_grid(
        grid_xlength=100,
        grid_ylength=100,
        grid_zlength=1,
        grid_spacing=1550e-10,
        total_time=1,
    )

    # 保存画好的图，设置保存位置，以及从哪一个轴俯视画图
    arc.savefig(filepath="ArcZ.png", axis="z")