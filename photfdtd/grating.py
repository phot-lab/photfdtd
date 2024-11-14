from .tff import TFF
from .directional_coupler import DirectionalCoupler


class Grating(TFF):
    """ Grating"""

    # TODO: 方向耦合器之间加两个直波导，可以添加热光系数，或者Y分支
    def __init__(self,
                 xlength: int or float = 71,
                 ylength: int or float = 1,
                 zlength: int or float = 20,
                 x: int or float = None,
                 y: int or float = None,
                 z: int or float = None,
                 duty_cyle: float = 0.5,
                 n_periods: int = 5,
                 period: int or float = 400e-9,
                 refractive_index: float = None,
                 grid=None,
                 axis: str = "z",
                 name: str = "Grating",
                 priority: int = 1
                 ) -> None:
        super().__init__(xlength, ylength, zlength, x, y, z,
                         low_index=grid.background_index,
                         high_index=refractive_index,
                         dl=(1 - duty_cyle) * period,
                         dh=duty_cyle * period,
                         layers=n_periods * 2,
                         axis=axis,
                         name=name,
                         grid=grid,
                         priority=priority)
