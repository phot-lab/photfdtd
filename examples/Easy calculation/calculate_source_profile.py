from photfdtd import Grid

if __name__ == "__main__":
    # 读取保存的监视器数据
    filepath = ".\\test_tff"
    grid = Grid.read_simulation(folder=filepath)
    source_profile = grid.calculate_source_profile()
    print(source_profile)