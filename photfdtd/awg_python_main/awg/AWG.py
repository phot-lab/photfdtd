from .core import *
from .material import *
from .material.material import Material
from .field import Field
from .waveguide import Waveguide
from .aperture import Aperture
import types
from numpy.random import randn
from tabulate import tabulate
import os
import numpy as np
import numbers

class AWG:
    """
         Arrayed Waveguide Grating Model
    
    PROPERTIES:
        lambda_c - design center wavelength设计中心波长
        clad - top cladding material上包层材料
        core - core (guiding) material芯层材料
        subs - bottom cladding material, note that materials can be assigned by a
            string literal refering to a awg.material.* function, a function handle
            for computing dipersion, a lookup table, a constant value or an
            awg.material.Material object instance. See awg.material.Material for
            details.下包层材料（衬底）
        w - waveguide core width波导宽度（芯层）
        h - waveguide code height波导高度（芯层）
        t - waveguide slab thickness (for rib waveguides) (def. 0)波导厚度（适用于脊状波导）（默认值为0）
        N - number of arrayed waveguides阵列波导数目
        m - diffraction order衍射级次
        R - grating radius of carvature (focal length)光栅圆半径（焦距）
        g - gap width between array apertures相邻阵列波导的间距
        d - array aperture spacing相邻阵列波导的中心间距（d-g=wa,wa是阵列波导孔径宽度）（中心-中心）
        L0 - minimum waveguide length offset (def. 0)阵列波导最小长度
        Ni - number of input waveguides输入波导数目
        wi - input waveguide aperture width输入波导孔径宽度
        di - input waveguide spacing (def. 0)输入波导间距
        li - input waveguide offset spacing (def. 0)输入波导偏移间距（默认值为0）？
        No - number of output waveguides输出波导个数
        wo - output waveguide aperture width输出波导孔径宽度
        do - output waveguide spacing (def. 0)输出波导间距（默认值为0）
        lo - output waveguide offset spacing (def. 0)输出波导偏移间距（默认值为0）？
        defocus - added defocus to R (def. 0)
        confocal - use confocal arrangement rather than Rowland (def. false)使用共焦配置而不是罗兰配置（默认值为假）
        channel_spacing -信道间隔

    
    CALCULATED PROPERTIES:计算的属性
        wg - array waveguide aperture width阵列波导孔径宽度
        dl - array length increment相邻阵列波导长度差
    """
    __slots__ = [
        '_lambda_c',  # center wavelength
        '_clad',      # clad material or index of the waveguide
        '_core',      # core material or index of the waveguide
        '_subs',      # substrate material or index of the waveguide
        '_w',         # waveguide core width
        '_h',         # waveguide core height
        '_t',         # waveguide slab thickness (for rib waveguides) (def. 0)
        '_N',         # number of arrayed waveguides
        '_m',         # diffraction order
        '_R',         # grating radius of carvature (focal length)
        '_d',         # array aperture spacing
        '_g',         # gap width between array apertures
        '_L0',        # minimum waveguide length offset (def. 0)
        '_Ni',        # number of input waveguides
        '_wi',        # input waveguide aperture width
        '_di',        # input waveguide spacing (def. 0)
        '_li',        # input waveguide offset spacing (def. 0)
        '_No',        # number of output waveguides
        '_wo',        # output waveguide aperture width
        '_do',        # output waveguide spacing (def. 0)
        '_lo',        # output waveguide offset spacing (def. 0)
        '_confocal',  # use confocal arrangement rather than Rowland (def. false)
        '_defocus',   # radial defocus (def. 0)径向失焦
        '_wa',        # waveguide aperture width
        '_Ri',        # input/output radius curvature # To add in future update
        '_Ra',         # array radius curvature # To add in future update
        '_channel_spacing',  # 信道间隔
        '_type',       #解复用/复用
    ]
    def __init__(self,**kwargs):
        _in = kwargs.keys()

        if "lambda_c" in _in:
            if type(kwargs["lambda_c"]) in [float, int] and kwargs["lambda_c"] > 0:
                self._lambda_c = kwargs["lambda_c"]
            else:
                raise ValueError("The central wavelength [um] must be a positive float or integer.")
        else:
            self._lambda_c = 1.550

        if "clad" in _in:
            if type(kwargs["clad"]) in [types.FunctionType, float, int]:
                self._clad = Material(kwargs["clad"])
            elif (str(type(kwargs["clad"])) == "<class 'awg.material.Material.Material'>"):
                self._clad = kwargs["clad"]
            elif type(kwargs["clad"]) == list:
                self._clad = Material(list_to_array(kwargs["clad"]))
            elif str(type(kwargs["clad"])) == "<class 'numpy.ndarray'>":
                self._clad = Material(kwargs["clad"])
            else:
                raise ValueError("The cladding must be a material or a float representing its refractive index.")
        else:
            self._clad = Material(SiO2)

        if "core" in _in:
            if type(kwargs["core"]) in [types.FunctionType, float, int]:
                self._core = Material(kwargs["core"])
            elif (str(type(kwargs["core"])) == "<class 'awg.material.Material.Material'>"):
                self._core = kwargs["core"]
            elif type(kwargs["core"]) == list:
                self._core = Material(list_to_array(kwargs["core"]))
            elif str(type(kwargs["core"])) == "<class 'numpy.ndarray'>":
                self._core = Material(kwargs["core"])
            else:
                raise ValueError("The core must be a material or a float representing its refractive index.")
        else:
            self._core = Material(Si)

        if "subs" in _in:
            if type(kwargs["subs"]) in [types.FunctionType, float, int]:
                self._subs = Material(kwargs["subs"])
            elif (str(type(kwargs["subs"])) == "<class 'awg.material.Material.Material'>"):
                self._subs = kwargs["subs"]
            elif type(kwargs["subs"]) == list:
                self._subs = Material(list_to_array(kwargs["subs"]))
            elif str(type(kwargs["subs"])) == "<class 'numpy.ndarray'>":
                self._subs = Material(kwargs["subs"])
            else:
                raise ValueError("The substrate must be a material or a float representing its refractive index.")
        else:
            self._subs = Material(SiO2)

        if "w" in _in:
            if type(kwargs["w"]) in [int, float] and kwargs["w"] > 0:
                self._w = kwargs["w"]
            else: 
                raise ValueError("The array waveguide core width 'w' [um] must be positive and be a float or an integer.")
        else:
            self._w = 0.450

        if "h" in _in:
            if type(kwargs["h"]) in [int, float] and kwargs["h"] > 0:
                self._h = kwargs["h"]
            else: 
                raise ValueError("The array waveguide core height 'h' [um] must be positive and be a float or an integer.")
        else:
            self._h = 0.220

        if "t" in _in:
            if type(kwargs["t"]) in [int, float] and kwargs["t"] >= 0:
                self._t = kwargs["t"]
            else: 
                raise ValueError("The array waveguide slab thickness 't' (for rib waveguides) [um] must be non-negative and be a float or an integer.")
        else:
            self._t = 0

        if "N" in _in:
            if (type(kwargs["N"]) == int) and (kwargs["N"] > 0):
                self._N = kwargs["N"]
            else: 
                raise ValueError("The The number of arrayed waveguide 'N' must be a positive integer.")
        else:
            self._N = 40

        if "m" in _in:
            if type(kwargs["m"]) in [int, float] and kwargs["m"] > 0:
                self._m = kwargs["m"]
            else: 
                raise ValueError("The order of diffraction 'm' must be a positive integer.")
        else:
            self._m = 30

        if "R" in _in:
            if type(kwargs["R"]) in [int, float] and kwargs["R"] > 0:
                self._R = kwargs["R"]
            else:
                raise ValueError("The grating radius of curvature (focal length) 'R' [um] must be a positive float or integer")
        else:
            self._R = 100

        if "d" in _in:
            if type(kwargs["d"]) in [int, float] and kwargs["d"] > 0:
                self._d = kwargs["d"]
            else:
                raise ValueError("The array aperture spacing 'd' [um] must be a positive float or integer")
        else:
            self._d = 1.3

        if "g" in _in:
            if type(kwargs["g"]) in [int, float] and kwargs["g"] > 0:
                self._g = kwargs["g"]
            else:
                raise ValueError("The gap width between array aperture 'g' [um] must be a positive float or integer")
        else:
            self._g = self.d-self.w

        if "L0" in _in:
            if type(kwargs["L0"]) in [int, float] and kwargs["L0"] >= 0:
                self._L0 = kwargs["L0"]
            else:
                raise ValueError("The minimum lenght offset 'L0' [um] must be a non-negative float or integer")
        else:
            self._L0 = 0

        if "Ni" in _in:
            if (type(kwargs["Ni"]) == int) and (kwargs["Ni"] >= 0):
                self._Ni = kwargs["Ni"]
            else:
                raise ValueError("The number of input waveguide 'Ni' must be a positive integer")
        else:
            self._Ni = 1

        if "wi" in _in:
            if type(kwargs["wi"]) in [int, float] and kwargs["wi"] > 0:
                self._wi = kwargs["wi"]
            else:
                raise ValueError("The input waveguide aperture width 'wi' [um] must be a positive float or integer")
        else:
            self._wi = 1

        if "di" in _in:
            # if type(kwargs["di"]) in [int, float] and kwargs["di"] > 0:
            #     self._di = kwargs["di"]
            if isinstance(kwargs["di"], numbers.Real) and kwargs["di"] > 0:
                self._di = float(kwargs["di"])  # 显式转换为标准 float
            else:
                raise ValueError("The input waveguide spacing 'di' [um] must be a positive float or integer")
        else:
            self._di = 0

        if "li" in _in:
            if type(kwargs["li"]) in [int, float] and kwargs["li"] >= 0:
                self._li = kwargs["li"]
            else:
                raise ValueError("The input waveguide offset spacing 'li' [um] must be a non-negative float or integer")
        else:
            self._li = 0

        if "No" in _in:
            if (type(kwargs["No"]) == int) and (kwargs["No"] >= 0):
                self._No = kwargs["No"]
            else:
                raise ValueError("The number of output waveguide 'No' must be a positive integer")
        else:
            self._No = 1

        if "wo" in _in:
            if type(kwargs["wo"]) in [int, float] and kwargs["wo"] > 0:
                self._wo = kwargs["wo"]
            else:
                raise ValueError("The output waveguide aperture width 'wo' [um] must be a positive float or integer")
        else:
            self._wo = 1

        if "do" in _in:
            # if type(kwargs["do"]) in [int, float] and kwargs["do"] > 0:
            #     self._do = kwargs["do"]
            if isinstance(kwargs["do"], numbers.Real) and kwargs["do"] > 0:
                self._do = float(kwargs["do"])  # 显式转为 float
            else:
                raise ValueError("The output waveguide spacing 'do' [um] must be a positive float or integer")
        else:
            self._do = 0

        if "lo" in _in:
            if type(kwargs["lo"]) in [int, float] and kwargs["lo"] >= 0:
                self._lo = kwargs["lo"]
            else:
                raise ValueError("The output waveguide offset spacing 'lo' [um] must be a non-negative float or integer")
        else:
            self._lo = 0

        if "confocal" in _in:
            if kwargs["confocal"] in [True, False]:
                self._confocal = kwargs["confocal"]
            else:
                raise ValueError("The confocal arrangement use instead of Rowland circle must be either True or False")
        else:
            self._confocal = False

        if "defocus" in _in:
            if type(kwargs["defocus"]) in [int, float] and kwargs["defocus"] > 0:
                self._defocus = kwargs["defocus"]
            else:
                raise ValueError("The radial defocus must be a positive float or integer")
        else:
            self._defocus = 0

        if "wa" in _in:
            if type(kwargs["wa"]) in [int, float] and kwargs["wa"] > 0:
                self._wa = kwargs["wa"]
            else:
                raise ValueError("The waveguide aperture width 'wa' [um] must be a positive float or integer")
        else:
            self._wa = self._d - self._g

        if "channel_spacing" in _in:
            if type(kwargs["channel_spacing"]) in [int, float] and kwargs["channel_spacing"] > 0:
                self._channel_spacing = kwargs["channel_spacing"]
            else:
                 raise ValueError("The channel spacing must be a positive float or integer.")
        else:
             self._channel_spacing = 0.4  # 设定默认信道间隔，例如 0.4 nm

        if "type" in _in:
            if kwargs["type"] in ["DEMUX", "MUX"]:
                self._type = kwargs["type"]
            else:
                raise ValueError("The parameter 'type' must be either 'DEMUX' or 'MUX'.")
        else:
            self._type = "DEMUX"  # 默认值





    def getSlabWaveguide(self):
        """
        Return the slab waveguide propreties.平板波导
        """
        return Waveguide(clad = self._clad,core = self._core,subs = self._subs,h = self._h, t = self._h)
    
    def getArrayWaveguide(self):
        """
        Return the arrayed waveguide propreties.脊型波导(t≠0）、条形波导（t=0)
        """

        return Waveguide(clad = self._clad,core = self._core,subs = self._subs,w = self._w,h = self._h, t = self._t)

    def getInputAperture(self):
        """
        Return the input waveguide aperture.输入波导孔径就是一个条形波导
        """
        return Aperture(clad = self._clad,core = self._core,subs = self._subs,w = self._wi,h = self._h)


    def getArrayAperture(self):
        """
        Return the slab waveguide propreties.
        """
        return Aperture(clad = self._clad,core = self._core,subs = self._subs,w = self._wa,h = self._h)

    def getOutputAperture(self):
        """
        Return the slab waveguide propreties.
        """
        return Aperture(clad = self._clad,core = self._core,subs = self._subs,w = self._wo,h = self._h)

    def __str__(self):
        
        if type(self._clad.model) == types.FunctionType:
            clad = self._clad.model.__name__
        elif self._clad.type == "constant":
            clad = self._clad.model
        elif self._clad.type == "polynomial":
            if len(self._clad.model) <= 3:
                clad = self._clad.model
            else:
                clad = f"[{self._clad.model[0]},...,{self._clad.model[-1]}]"
        elif self._clad.type == "lookup":
            clad = "lookup table"

        if type(self._core.model) == types.FunctionType:
            core = self._core.model.__name__
        elif self._core.type == "constant":
            core = self._core.model
        elif self._core.type == "polynomial":
            if len(self._core.model) <= 3:
                core = self._core.model
            else:
                core = f"[{self._core.model[0]},...,{self._core.model[-1]}]"
        elif self._core.type == "lookup":
            core = "lookup table"

        if type(self._subs.model) == types.FunctionType:
            subs = self._subs.model.__name__
        elif self._subs.type == "constant":
            subs = self._subs.model
        elif self._subs.type == "polynomial":
            if len(self._subs.model) <= 3:
                subs = self._subs.model
            else:
                subs = f"[{self._subs.model[0]},...,{self._subs.model[-1]}]"
        elif self._subs.type == "lookup":
            subs = "lookup table"
        
        return tabulate([['lambda_c', self._lambda_c, "Central wavelenght"], 
                        ['clad', clad , "clad material"], 
                        ['core', core, "core material"], 
                        ['subs', subs, "subs material"],
                        ['w', self.w,"core width [\u03BCm]"],#[\u03BCm] 是表示微米（μm）的Unicode编码
                        ['h', self._h,"core height [\u03BCm]"],
                        ["t",self.t,"slab thickess for rib waveguides [\u03BCm]"],
                        ["N",self.N,"Number of arrayed waveguide"],["m",self.m, "Diffraction order"],
                        ["R",self.R,"grating radius of carvature (focal length) [\u03BCm]"],
                        ["d",self.d,"array aperture spacing"],["g",self.g,"gap width between array apertures"],
                        ["L0",self.L0,"minimum waveguide length offset (def. 0) [\u03BCm]"],
                        ["Ni",self.Ni,"Number of input waveguide"],
                        ["wi",self.wi,"input waveguide aperture width [\u03BCm]"],
                        ["di",self.di,"input waveguide spacing (def. 0) [\u03BCm]"],
                        ["li",self.li,"input waveguide offset spacing (def. 0)"],
                        ["No",self.No,"Number of ouput waveguide"],
                        ["wo",self.wo,"ouput waveguide aperture width [\u03BCm]"],
                        ["do",self.do,"ouput waveguide spacing (def. 0) [\u03BCm]"],
                        ["lo",self.lo,"ouput waveguide offset spacing (def. 0)"],
                        ["confocal",self.confocal,"use confocal arrangement rather than Rowland (def. false)"],
                        ], headers=['parameters', 'Value', 'definition'])

    @property
    def lambda_c(self):
        return self._lambda_c

    @lambda_c.setter
    def lambda_c(self,lambda_c):
        if (type(lambda_c) == float) or (type(lambda_c) == int) and (lambda_c > 0):
            self._lambda_c = lambda_c 
        else:
            raise ValueError("The central wavelength [um] must be a positive float or integer.")

    @property
    def clad(self):
        return self._clad
    
    @clad.setter
    def clad(self,clad):
        if (type(clad) == types.FunctionType) or (str(type(clad)) == "<class 'material.Material.Material'>") or (type(clad) == float) or (type(clad) == int):
            self._clad = clad
        else:
            raise ValueError("The cladding must be a material or a float representing its refractive index.")

    @property
    def core(self):
        return self._core
    
    @core.setter
    def core(self,core):
        if (type(core) == types.FunctionType) or (str(type(core)) == "<class 'material.Material.Material'>") or (type(core) == float) or (type(core) == int):
            self._core = core
        else:
            raise ValueError("The core must be a material or a float representing its refractive index.")

    @property
    def nc(self):
        return self.getArrayWaveguide().index(self.lambda_c,1)[0]

    @property
    def ncore(self):
        return self.core.index(self.lambda_c)

    @property
    def nclad(self):
        return self.clad.index(self.lambda_c)
    
    @property
    def subs(self):
        return self.subs.index(self.lambda_c)

    

    @property
    def subs(self):
        return self._subs
    
    @clad.setter
    def subs(self,subs):
        if (type(subs) == types.FunctionType) or (str(type(subs)) == "<class 'material.Material.Material'>") or (type(subs) == float) or (type(subs) == int):
            self._subs = subs
        else:
            raise ValueError("The substrate must be a material or a float representing its refractive index.")

    @property
    def w(self):
        return self._w

    @w.setter
    def w(self,w):
        if type(w) in [int, float] and w > 0:
            self._w = w
        else:
            raise ValueError("The array waveguide core width 'w' [um] must be positive and be a float or an integer.")

    @property
    def h(self):
        return self._h

    @h.setter
    def h(self,h):
        if type(h) in [int, float] and h > 0:
            self._h = h
        else:
            raise ValueError("The array waveguide core height 'h' [um] must be positive and be a float or an integer.")

    @property
    def t(self):
        return self._t

    @t.setter
    def t(self,t):
        if type(t) in [int, float] and t >= 0:
            self._t = t
        else:
            raise ValueError("The array waveguide slab thickness 't' (for rib waveguides) [um] must be non-negative and be a float or an integer.")

    @property
    def N(self):
        return self._N

    @N.setter
    def N(self,N):
        if (type(N) == int) and (N > 0):
            self._N = N 
        else:
            raise ValueError("The The number of arrayed waveguide 'N' must be a positive integer.")

    @property
    def m(self):
        return self._m

    @m.setter
    def m(self,m):
        if type(m) in [int, float] and m > 0:
            self._m = m
        else:
            raise ValueError("The order of diffraction 'm' must be a positive integer.")
    
    @property
    def R(self):
        return self._R

    @R.setter
    def R(self,R):
        if type(R) in [int, float] and R > 0:
            self._R = R
        else:
            raise ValueError("The grating radius of curvature (focal length) 'R' [um] must be a positive float or integer")

    @property
    def d(self):
        return self._d

    @d.setter
    def d(self,d):
        if type(d) in [int, float] and d > 0:
            self._d = d
        else:
            raise ValueError("The array aperture spacing 'd' [um] must be a positive float or integer")

    @property
    def g(self):
        return self._g

    @g.setter
    def g(self,g):
        if type(g) in [int, float] and g > 0:
            self._g = g
        else:
            raise ValueError("The gap width between array aperture 'g' [um] must be a positive float or integer")
    
    @property
    def L0(self):
        return self._L0

    @L0.setter
    def L0(self,L0):
        if ((type(L0) == float) or (type(L0) == int) and (L0 >=0)):
            self._L0 = L0
        else:
            raise ValueError("The minimum lenght offset 'L0' [um] must be a non-negative float or integer")
    
    @property
    def Ni(self):
        return self._Ni

    @Ni.setter
    def Ni(self,Ni):
        if (type(Ni) == int) and (Ni > 0):
            self._Ni = Ni 
        else:
            raise ValueError("The The number of input waveguide 'Ni' must be a positive integer.")
    
    @property
    def wi(self):
        return self._wi

    @wi.setter
    def wi(self,wi):
        if type(wi) in [int, float] and wi > 0:
            self._wi = wi
        else:
            raise ValueError("The input waveguide aperture width 'wi' [um] must be a positive float or integer")

    @property
    def di(self):
        return self._di

    @di.setter
    def di(self,di):
        if type(di) in [int, float] and di > 0:
            self._di = di
        else:
            raise ValueError("The input waveguide spacing 'di' [um] must be a positive float or integer")

    @property
    def li(self):
        return self._li

    @li.setter
    def li(self,li):
        if type(li) in [int, float] and li >= 0:
            self._li = li
        else:
            raise ValueError("The input waveguide offset spacing 'li' [um] must be a non-negative float or integer")

    @property
    def No(self):
        return self._No

    @No.setter
    def No(self,No):
        if (type(No) == int) and (No > 0):
            self._No = No 
        else:
            raise ValueError("The The number of output waveguide 'No' must be a positive integer.")
    
    @property
    def wo(self):
        return self._wo

    @wo.setter
    def wo(self,wo):
        if type(wo) in [int, float] and wo > 0:
            self._wo = wo
        else:
            raise ValueError("The output waveguide aperture width 'wo' [um] must be a positive float or integer")

    @property
    def do(self):
        return self._do

    @do.setter
    def do(self,do):
        if type(do) in [int, float] and do > 0:
            self._do = do
        else:
            raise ValueError("The output waveguide spacing 'do' [um] must be a positive float or integer")

    @property
    def lo(self):
        return self._lo

    @lo.setter
    def lo(self,lo):
        if type(lo) in [int, float] and lo >= 0:
            self._lo = lo
        else:
            raise ValueError("The output waveguide offset spacing 'lo' [um] must be a non-negative float or integer")


    @property
    def confocal(self):
        return self._confocal

    @confocal.setter
    def confocal(self, confocal):
        if confocal in [True, False]:
            self._confocal = confocal
        else:
            raise ValueError("The confocal arrangement use instead of Rowland circle must be either True or False")


    @property
    def defocus(self):
        return self._defocus
    
    @defocus.setter
    def defocus(self,defocus):
        if type(defocus) in [int, float] and defocus > 0:
            self._defocus = defocus
        else:
            raise ValueError("The defocus or R must be a positive float or integer")



    @property
    def wa(self):
        return self._wa

    @wa.setter
    def wa(self,wa):
        if type(wa) in [int, float] and wa > 0:
            self._wa = wa
        else:
            raise ValueError("The waveguide aperture width 'wa' [um] must be a positive float or integer")

    @property
    def dl(self):
        return self._m*self._lambda_c/self.nc

    @dl.setter
    def dl(self,dl):
        if type(dl) in [int, float] and dl > 0:
            self._dl = dl
        else:
            raise ValueError("The arrayed waveguide lenght increment 'dl' must be a positive float or integer")

    @property
    def wg(self):
        return self._d-self._g
    @property
    def channel_spacing(self):
        return self._channel_spacing

    @channel_spacing.setter
    def channel_spacing(self, value):
        if isinstance(value, (int, float)) and value > 0:
            self._channel_spacing = value
        else:
            raise ValueError("channel_spacing 必须是正数")

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if value in ["DEMUX", "MUX"]:
            self._type = value
        else:
            raise ValueError("The parameter 'type' must be either 'DEMUX' or 'MUX'.")
    
    



def iw(model, lmbda, _input = 0, u = np.array([]),**kwargs):
    """
    Generates input waveguide field distribution.生成输入波导的场分布

    INPUT :
        model - AWG systeme
        lmbda - center wavelength [μm]
        _input - 指定的输入波导编号（从 0 到 Ni-1）
        u     - custom input field (def.[])自定义输入场（默认为空数组）

    OPTIONAL :
        ModeType - Type of mode to use (rect, gaussian,solve)(def.gaussian)使用的模式类型（rect, gaussian, solve）（默认值为"gaussian"）
        points   - number of field sample场的采样点
    OUTPUT :
        output field返回的场分布
    """

    _in = kwargs.keys()

    ModeType = kwargs["ModeType"] if "ModeType" in _in else "gaussian"# 获取ModeType参数，默认为"gaussian"
    if ModeType not in ["rect","gaussian", "solve"]:# 判断ModeType是否有效
        raise ValueError(f"Wrong mode type {ModeType}.")
    # 获取采样点数，默认为100
    points = kwargs["points"] if "points" in _in else 100
    #计算输入波导的中心位置
    x_center = (_input - (model.Ni - 1) / 2) * model.di  # 计算波导中心位置，使其对称分布，左边为-，右边为+
    print(" x_center:", x_center)

    if str(type(u)) == "<class 'awg.Field.Field'>":# 判断u的类型，如果u是Field对象，直接赋值给F
        F = u
    elif len(u) == 0:# 如果u为空数组，则生成一个默认的输入场
        x = np.linspace(-1/2, 1/2, points) * max(model.di, model.wi) *(model.Ni +4)  # 生成x坐标范围
        F = model.getInputAperture().mode(lmbda,model.lambda_c, x= x+ x_center, ModeType = ModeType)# 使用模型的输入光阑生成模式场
    elif (min(u.shape) > 2) or (len(u.shape) > 2) :# 如果u的形状不合适，抛出异常
        raise ValueError("Data provided for the input field must be a two column matrix of coordinate, value pairs.")
    else:# 如果u是一个合适的数组，则将其转换为Field对象
        n,m = u.shape
        F = Field.Field(u[:,0],u[:,1])

    return F.normalize()# 返回归一化后的场分布

def fpr1(model,lmbda,F0,**kwargs):
    """
    Propagates the field in the first free propagation region.在第一个自由传播区传播场。

    INPUT :
        model - AWG systeme
        lmbda - center wavelength [μm]
        F0    - Input Field输入场

    OPTIONAL :
        x      - spatial range of the field at the end of fpr自由传播区结束时场的空间范围（即sf的值）
        points - number of field sample采样点

    OUTPUT :
        Field at the end of the first fpr第一自由传播区末端的场
    """
    _in =kwargs.keys()

    x = kwargs["x"] if "x" in _in else []# 如果有"x"，则使用，否则默认为空列表
    _input = kwargs["Input"] if "Input" in _in else 0# 如果有"Input"，则使用，否则默认为0
    points = kwargs["points"] if "points" in _in else 250 # 如果有"points"，则使用，否则默认为250
    xi = F0.x# 输入场的横坐标（即iw里面的生成的x)
    ui = F0.Ex # 输入场的电场分量Ex


    ns = model.getSlabWaveguide().index(lmbda,1)[0]# 获取平板波导的有效折射率
    print("ns:",ns)
    # 如果没有提供x，则生成默认的空间范围
    if len(x) == 0:
        sf = np.linspace(-1/2,1/2,points)*(model.N+4)*model.d# 自由传播区的空间范围
    else:
        sf = x# 使用提供的x


    R = model.R# 自由传输区的长度，光栅圆半径
    r = model.R/2# 罗兰圆半径
    if model.confocal:# 如果是共焦配置，使用完整的半径
        r = model.R

    a = xi/r # （xi是罗兰圆上的点，相当于弧长，a是罗兰圆弧长所对的圆心角）
    xp = r*np.tan(a)# xp是xi对应的在同一直线上的点，直线上位于z=0处
    dp = r*(1/np.cos(a))-r# 计算xi与xp的传播距离
    up = ui*np.exp(1j*2*np.pi/lmbda*ns*dp) # xp点处的电场（该函数使用延迟相位约定：exp(-1j*k*z)，向前传取-，往后传取+）相当于化曲为直圆周上同相位的电场转为同一直线上的电场

    a = sf/R# （sf是光栅圆上的点，相当于弧长，a是光栅圆弧长所对的圆心角）
    xf = R*np.sin(a)# xf是sf对应的在直线上的点，化曲为直
    zf = model.defocus + R*np.cos(a)# 计算sf该点在z方向的位置
    uf = diffract(lmbda,ns,up,xp,xf,zf)[0]# 计算衍射后的场uf,lmbda/ns:波导里面传输的波长

    return Field(sf,uf).normalize(F0.power())# 返回归一化后的场

def aw(model,lmbda,F0,output_dir=None,**kwargs):
    """
    Couples input field to the array apertures and propagates the fields
    along the waveguide array to the other end.将输入场耦合到阵列孔径并沿着阵列波导传播到另一端。

    INPUT :
        model - AWG systeme
        lmbda - center wavelength [μm]
        F0    - Input Field
    OPTIONAL:
        ModeType       - Type of mode to use (rect, gaussian,solve)(def.gaussian)
        PhaseError     - Amplitude of random phase error through arrayed waveguide阵列波导中的随机相位误差幅度
        InsertionLoss  - Insertion loss in the model [dB]模型中的插入损耗 [dB]
        PopagationLoss - Propagation loss [dB/cm]传播损耗 [dB/cm]
    OUTPUT :
        Field at the end of the arrayed waveguide section阵列波导段末端的电场
    """
    _in = kwargs.keys()
    if output_dir is not None:
        os.makedirs(output_dir, exist_ok=True)
    # 如果没有传入 ModeType，则默认为“gaussian”
    ModeType = kwargs["ModeType"] if "ModeType" in _in else "gaussian"
    if ModeType.lower() not in ["rect","gaussian", "solve"]:
        raise ValueError(f"Wrong mode type {ModeType}.")
    # 设置随机相位误差的方差、插入损耗和传播损耗，默认值为0
    PhaseErrorVar = kwargs["PhaseErrorVar"] if "PhaseErrorVar" in _in else 0
    InsertionLoss = kwargs["InsertionLoss"] if "InsertionLoss" in _in else 0
    PropagationLoss = kwargs["PropagationLoss"] if "PropagationLoss" in _in else 0
    # 获取输入电场的基本信息
    x0 = F0.x# 输入电场的位置(即是fpr1光栅圆上的点)
    u0 = F0.Ex# 输入电场的 Ex 分量
    P0 = F0.power()# 输入电场的功率
    # 计算波数 k0 和波导折射率 nc
    k0 = 2*np.pi/lmbda
    print("lmbda:",lmbda)
    nc = model.getArrayWaveguide().index(lmbda,1)[0]
    print("nc:",nc)
    dl=model.m*model.lambda_c/nc
    print("dl:",dl)
    # # 生成随机的相位误差
    pnoise = randn(1,model.N)[0]*np.sqrt(PhaseErrorVar)
    # 计算插入损耗
    iloss = 10**(-abs(InsertionLoss)/10)
    # 初始化输出电场 Ex
    Ex = np.zeros(len(F0.E))
    # 遍历每个波导
    for i in range(model.N):
        j = i - (model.N - 1) // 2#最中间阵列波导编号为0，左边为-，右边为+
        xc = j *model.d# 计算第j个阵列波导相对中心的偏移量
        # 获取波导模式，并进行归一化处理
        Fk =  model.getArrayAperture().mode(lmbda,model.lambda_c,x = x0+xc, ModeType = ModeType).normalize()#调用 .normalize() 方法对计算出的模式进行归一化,x0-xc每条阵列波导的中心位置
        # 将模式与矩形函数结合，得到每个波导的电场,x0+xc的绝对值小于d/2为1，其他为0
        center = (np.min(x0 + xc) + np.max(x0 + xc)) / 2  # 计算各阵列波导高斯分布场中心点
        Ek = Fk.Ex * rect(((x0 + xc) - center) / model.d)
        # 归一化电场
        Ek = pnorm(Fk.x,Ek)
        Ek_interp = np.interp(x0, Fk.x, Ek)  # 线性插值,把Ek的x范围统一到x0范围
        # 计算重叠积分
        t1 = overlap(x0, Ek_interp,u0)
        # 计算波导的传播距离 L 和相位
        L = j *dl+model.L0
        phase = k0*nc*L+pnoise[j]
        print("phase:",phase)
        ploss = 10**(-abs(PropagationLoss*L*1e-4)/10)
        t = t1*ploss*iloss**2
        # 计算传播后的电场
        Efield = P0 * t * Ek_interp * np.exp(-1j * (phase + np.angle(u0)))#加上输入电场的相位
        # 累加电场
        Ex = Ex + Efield


    return Field(x0,Ex)# 返回最终的电场


def fpr2(model,lmbda,F0,**kwargs):
    """
    Propagates the field in the second free propagation region.在第二自由传播区传播电场。

    INPUT :
        model - AWG systeme
        lmbda - center wavelength [μm]
        F0    - Input Field

    OPTIONAL :
        x      - spatial range of the field at the end of fpr在第二自由传播区末端的电场空间范围
        points - number of field sample电场采样点的数量（默认为250）

    OUTPUT :
        Field at the end of the second fpr第二自由传播区末端的电场
    """
    _in  = kwargs.keys()
    # 如果没有传入x，则默认为空；如果没有传入points，则默认250
    x = kwargs["x"] if "x" in _in else []
    points = kwargs["points"] if "points" in _in else 250
    # 获取输入电场的基本信息
    x0 = F0.x# 输入电场的位置
    u0 = F0.Ex# 输入电场的电场分量Ex
    # 获取平板波导的折射率
    ns = model.getSlabWaveguide().index(lmbda,1)[0]
    R = model.R# 光栅圆的半径
    r = R/2# 罗兰圆半径
    if model.confocal: # 如果为共焦配置，则半径为R
        r = R
    A=model.lambda_c*R/(ns*model.d)#计算相邻衍射级间距
    g=(np.pi*r)/(A)#将罗兰圆点范围内控制只有主干涉峰
    sf = np.linspace(-np.pi/g,np.pi/g,points)*r if len(x) == 0 else x#sf:罗兰圆上的点

    # 计算衍射
    a = x0/R# x0光栅圆上的点，阵列波导位于光栅圆圆周上
    xp = R*np.tan(a)# x0对应的直线上坐标xp，z=0
    dp = R*(1/np.cos(a))-R# 计算x0与xp的传播距离
    up = u0*np.exp(1j*2*np.pi/lmbda*ns*dp)#x0在直线上对应的电场up
    a = sf/r#sf：罗兰圆上的点，输出波导位于罗兰圆圆周上
    xf = r*np.sin(a)#sf对应直线上的坐标xf
    zf = (model.defocus+R-r)+r*np.cos(a)#在z方向传播的距离
    uf = diffract(lmbda,ns,up,xp,xf,zf)[0]# 计算衍射后的电场,用 [0] 是为了取出 uf
    return Field(sf,uf).normalize(F0.power())# 返回传播后的电场，并归一化功率


def ow(model,lmbda,F0,**kwargs):
    """
    Compute output waveguide coupling 计算输出波导耦合

    INPUT :
        model - AWG systeme
        lmbda - center wavelength [μm]
        F0    - Field distribution at the beginning of the output waveguide

    OPTIONAL :
        ModeType - Type of mode to use (rect, gaussian,solve)(def.gaussian)
    OUTPUT :
        # Power transmission for each output waveguide.每个输出波导的功率传输值
        Power transmission for each output waveguide and the field distribution at each output waveguide.
        每个输出波导的功率传输值和每个输出波导的光场分布。
    """
    # 获取模式类型，默认为 'gaussian'
    ModeType = kwargs.get("ModeType", "gaussian")
    if ModeType.lower() not in ["rect","gaussian", "solve"]:# 检查模式类型是否有效
        raise ValueError(f"Wrong mode type {ModeType}.")
    # 获取输入场的坐标和电场分量
    x0 = F0.x
    u0 = F0.Ex
    P0 = F0.power() # 获取输入场的功率
    # 初始化功率传输数组，存储每个输出波导的耦合传输值
    T = np.zeros(model.No, dtype = complex)
    # 遍历每个输出波导计算耦合效率
    for i in range(model.No):
        # 计算每个输出波导的中心位置
        xc = model.lo +(i-(model.No-1)/2)*max(model.do,model.wo)
        # 获取当前输出波导的模式场分布
        Fk = model.getOutputAperture().mode(lmbda,model.lambda_c,x = x0+xc, ModeType = ModeType)#x0-xc把采样点的参考系从某个全局坐标系转换到以波导为中心的局部坐标系。
        Ek = Fk.Ex#由于采样点的问题，采样点位置与中心点距离较大，所以就没有rect，要不然rect容易出错

        # 将输出电场 Ek 插值到输入场的 x0 上，确保坐标一致
        Ek_interp = np.interp(x0, Fk.x, np.real(Ek)) + 1j * np.interp(x0, Fk.x, np.imag(Ek))
         # 归一化电场
        Ek_interp = pnorm(x0, Ek_interp)
        # 计算当前输出波导的传输功率
        T[i] =  P0 *overlap(x0, Ek_interp, u0)**2
        # 输出每个输出波导的索引和其对应的功率传输值
        print(f"Output Waveguide {i}, Power Transmission: {abs(T[i]):.4f}")

    return abs(T)# 返回每个输出波导的功率传输值的绝对值和输出波导编号

