from photfdtd import Grid

if __name__ == "__main__":
    # 读取保存的监视器数据
    filepath = ".\\test_ring_0401_linesource"
    grid = Grid.read_simulation(folder=filepath)
    grid.folder=filepath
    # grid.animate(fps=200)
    # grid.visualize()
    freqs, spectrum1 = grid.visualize_single_detector(name_det='detector_input')
    freqs, spectrum2 = grid.visualize_single_detector(name_det="detector2")
    freqs, spectrum3 = grid.visualize_single_detector(name_det="detector3")


    import matplotlib.pyplot as plt

    # For S parameters: abs(spectrum2 / spectrum1)
    # For Power transmission: abs(spectrum2 / spectrum1) ** 2
    plt.plot(freqs, abs(spectrum2 / spectrum1) ** 2)
    plt.ylabel("S parameter")
    plt.xlabel("frequency (THz)")
    plt.title("S21(f)")
    plt.legend()
    file_name = "S21"
    plt.savefig(f"{grid.folder}/{file_name}.png")
    plt.close()

    plt.plot(freqs, abs(spectrum3 / spectrum1) ** 2)
    plt.ylabel("S parameter")
    plt.xlabel("frequency (THz)")
    plt.title("S31(f)")
    plt.legend()
    file_name = "S31"
    plt.savefig(f"{grid.folder}/{file_name}.png")
    plt.close()


