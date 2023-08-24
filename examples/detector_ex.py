import utils
from photfdtd import Waveguide, Grid

if __name__ == "__main__":
    # 新建一个 grid 对象
    grid = Grid(grid_xlength=100, grid_ylength=100, grid_zlength=1, grid_spacing=155e-9, total_time=1000, pml_width=2)

    # 设置器件参数
    waveguide = Waveguide(
        xlength=50, ylength=50, zlength=1, x=25, y=25, z=1, width=10, refractive_index=1.7, name="Waveguide"
    )

    # 往 grid 里添加一个器件
    grid.add_object(waveguide)

    grid.set_source(
        x=20,
        xlength=0,
        y=50,
        ylength=0,
        z=0,
        zlength=0,
        source_type="pointsource",
        period=1550e-9 / 299792458,
        pulse=False,
    )

    grid.add_detector("LineDetector", "Detector", x=80, y=45, z=0, xlength=0, ylength=10, zlength=0)

    grid.run()

    # 保存画好的图，设置保存位置，以及从哪一个轴俯视画图（这里画了三张图）
    # grid.savefig(filepath="DetectorX.png", x=0)
    # grid.savefig(filepath="DetectorY.png", y=0)
    grid.savefig(filepath="DetectorExZ.png", z=0)
    grid.savefig_linedetector("DetectorFig.png", "Detector", "Ez", True)
