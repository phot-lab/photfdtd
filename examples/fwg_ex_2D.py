from photfdtd import FWG, Grid, fdtd
from numpy import pi
fdtd.set_backend("torch.cuda")

if __name__ == "__main__":
    background_index = 1.4447
    n_Si = 3.476

    # 新建一个 grid 对象
    grid = Grid(grid_xlength=200, grid_ylength=1, grid_zlength=200, grid_spacing=20e-9,
                permittivity=background_index ** 2, foldername="test_fwg_2D")

    # 设置器件参数
    fwg = FWG(outer_radius=2.3e-6, ylength=1, refractive_index=n_Si, name="fwg",
              z=1e-6,
              grid=grid, angle_psi=120, angle_phi=30, period=10 * 20e-9, duty_cycle=0.4, number=11)

    # 往 grid 里添加器件
    grid.add_object(fwg)
    grid.save_fig()
    grid.plot_n()

    grid.set_source(source_type="linesource", period=1550e-9 / 299792458,
                    x_start=1.7e-6, y_start=0e-6, z_start=0.8e-6,
                    x_end=2.2e-6, y_end=0e-6, z_end=0.8e-6,
                    polarization="x")
    grid.set_detector(detector_type='linedetector',
                      x=2e-6, y=0, z=3e-6, xlength=10,
                      name='detector1')

    grid.run(time=2000, save=True, animate=True)
    grid.visualize()