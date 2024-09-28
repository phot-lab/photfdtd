import grid
import photfdtd


def visualize(grid: photfdtd.Grid = None):
    if grid is None:
        raise ValueError("grid should not be None.")