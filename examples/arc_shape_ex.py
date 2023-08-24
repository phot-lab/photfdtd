import utils
from photfdtd import ArcShape, Grid

if __name__ == "__main__":

    arc = ArcShape(outer_radius=20, zlength=1, x=40, y=40, z=1, width=2, refractive_index=3.47, name="arc", direction=4)

    grid = Grid(grid_xlength=100, grid_ylength=100, grid_zlength=1, grid_spacing=1550e-10, total_time=10000)

    grid.add_object(arc)

    grid.set_source(
        x=60,
        xlength=0,
        y=60,
        ylength=0,
        z=0,
        zlength=0,
        source_type="pointsource",
        period=1550e-9 / 299792458,
        pulse=False,
    )

    grid.run()

    # 保存画好的图，设置保存位置，以及从哪一个轴俯视画图
    grid.savefig(filepath="ArcShapeZ.png", z=0)
