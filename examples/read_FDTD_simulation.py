from photfdtd import Grid

if __name__ == "__main__":
    filepath = "D:\Github_Clone\photfdtd\examples\\test_ysplitter"
    data = Grid.read_simulation(folder=filepath)
    Grid.plot_fieldtime(folder=filepath, data=data, field="E", field_axis="x",
                        index=5, name_det="detector1")


