from .simulation_options import SimulationOptions
from .simulate import Simulate
from .AWG import *
import pandas as pd

class Spectrum:
    """
    Simulate entire AWG device over wavelength range and extract transmission在整个波长范围内仿真AWG设备并提取传输特性。

    INPUT:

        model     - AWG system to Simulate
        lmbda     - center wavelength [μm]
        bandwidth - badwidth use around the center wavelenght [μm]以中心波长为中心的带宽范围 [μm]
    OPTIONAL :
        Points  - Number of point to sample over the calculated field (def.250)计算场时的采样点数（默认值：250）
        Samples - Number of point to sample over the bandwidth (def.100)在带宽范围内采样的点数（默认值：100）
        Options - Using some custom simulation options using the SimulationOptions function使用自定义仿真选项，参见SimulationOptions函数
    OUTPUT:
        None

    ATTRIBUTE:
        wavelength   - Array of the wavelegth use for the simulation仿真过程中使用的波长数组
        transmission - Array of transmission for each ouput channel of the AWG at every wavelenght每个输出通道在每个波长下的传输数组

    """
    def __init__(self,model,bandwidth,Ng,d,delta_x,m,foldername="./",**kwargs):
        self.foldername = foldername
        self.Ng=Ng
        self.d=d
        self.delta_x=delta_x
        self.m=m
        _in = kwargs.keys()

        points = kwargs["Points"] if "Points" in _in else 250# 获取采样点数，默认为250
        Samples = kwargs["Samples"] if "Samples" in _in else 100# 获取带宽范围内的采样点数，默认为100
        Options = kwargs["Options"] if "Options" in _in else SimulationOptions()# 获取仿真选项，默认为SimulationOptions()
        wvl = model.lambda_c + np.linspace(-0.5,0.5,Samples)*bandwidth# 生成波长数组，以中心波长为中心，带宽范围为上下限
        # 初始化传输数组，用于存储每个波长的传输值
        T = np.zeros((Samples,model.No), dtype = complex)


        # Replacement for the wait bar # 仿真过程，替代等待条
        for i in range(Samples):
            # 调用Simulate类进行仿真，获得每个波长下的传输结果
            R = Simulate(model,wvl[i],Options = Options,points = points)
            T[i,:] = R.transmission
            print(f"{i+1}/{Samples}")
        # 将波长和传输结果赋值给对象的属性
        self.wavelength = wvl
        self.transmission = T
    def export_to_excel(self, filename="spectrum_results.xlsx"):
        """
        Export the simulation results to an Excel file.把仿真结果导出为excel表格
        """
        os.makedirs(self.foldername, exist_ok=True)
        filepath = os.path.join(self.foldername, filename)
        data = {
            "Number of arrayed waveguides": [],
            "Arrayed waveguide spacing(μm)": [],
            "Output waveguide spacing(μm)": [],
            "Diffraction order": [],
            "Wavelength (um)": [],
            "Waveguide Index": [],
            "output_power(dB)": []

        }

        for i, wl in enumerate(self.wavelength):
            for j in range(self.transmission.shape[1]):
                T = abs(self.transmission[i, j])
                T_dB = 10 * np.log10(T + 1e-12)   # 避免 log(0)

                data["Number of arrayed waveguides"].append(self.Ng)
                data["Arrayed waveguide spacing(μm)"].append(self.d)
                data["Output waveguide spacing(μm)"].append(self.delta_x)
                data["Diffraction order"].append(self.m)
                data["Wavelength (um)"].append(wl)
                data["Waveguide Index"].append(j)
                data["output_power(dB)"].append(T_dB)

        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False)
        print(f"导出成功：{filepath}")