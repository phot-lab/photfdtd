import utils
from photfdtd import Waveguide, Grid

if __name__ == "__main__":
    # 新建一个 grid 对象
    grid = Grid(grid_xlength=50, grid_ylength=50, grid_zlength=50, grid_spacing=155e-9)

    # 设置器件参数
    waveguide = Waveguide(
        xlength=30, ylength=30, zlength=30, x=10, y=10, z=10, width=10, refractive_index=1.7, name="Waveguide"
    )

    # 往 grid 里添加一个器件
    grid.add_object(waveguide)

    # grid.set_source(
    #     x=8,
    #     xlength=0,
    #     y=25,
    #     ylength=0,
    #     z=25,
    #     zlength=0,
    #     source_type="pointsource",
    #     period=1550e-9 / 299792458,
    #     waveform=False,
    # )
    grid.set_source(source_type="planesource", period=1550e-9 / 299792458, waveform=False, x=8, y=20, z=20, xlength=0,
                    ylength=10, zlength=10)
    # print(1550e-9 / 299792458)

    grid.add_detector("BlockDetector", "Detector", x=5, y=5, z=5, xlength=40, ylength=40, zlength=40)

    grid.run()

    # 保存画好的图，设置保存位置，以及从哪一个轴俯视画图（这里画了三张图）
    grid.savefig(filepath="BlockDetectorX.png", x=0)
    grid.savefig(filepath="BlockDetectorY.png", y=0)
    grid.savefig(filepath="BlockDetectorZ.png", z=0)
    # grid.savefig_linedetector("DetectorFig.png", "Ez")
    grid.savefig_blockdetector("BlockDetectorFig.png", "Detector", 2, True)
