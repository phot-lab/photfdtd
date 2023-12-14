from photfdtd import Solve

if __name__ == "__main__":
    filepath = "D:\Github_Clone\photfdtd\examples\\test_multi_core_fiber"
    data_from_saved_modes = Solve.read_mode(filepath)
    print(data_from_saved_modes["effective_index"])
    Solve.draw_mode(filepath=filepath, data=data_from_saved_modes, content="amplitude")
    Solve.draw_mode(filepath=filepath, data=data_from_saved_modes, content="real_part")
    Solve.draw_mode(filepath=filepath, data=data_from_saved_modes, content="imaginary_part")
    Solve.draw_mode(filepath=filepath, data=data_from_saved_modes, content="phase")