import sys, os
import types
import math
import matplotlib.pyplot as plt
import numpy as np
import scipy as sc
from scipy.optimize import root
import cmath
sys.path.append(os.path.abspath(os.path.join('..')))



def clamp(x,a,b):
    """
    Limit x value within [a,b] range
    """
    return min(max(x,a),b)

def step(x): # take only list or arrays
    """
    Unit step function.
    """
    return 1- np.double(x < 0)

def rect(x):
    """
    Return a rectangle function.
    """
    return step(-x+1/2)*step(x+1/2) #（-1/2，1/2）是1，其他为0
### length of float and integer are not defined ###

def sinc(x):
    return min(1,np.sin(x)/(x*np.pi))

def fpower(x,Ex,Hy = [],Ey = [],Hx = []):
    """
    Calculate the field optical power.
    计算光场的功率。

    参数：
    x  : ndarray  - 空间坐标数组
    Ex : ndarray  - x 方向的电场分量
    Hy : ndarray  - y 方向的磁场分量（可选）
    Ey : ndarray  - y 方向的电场分量（可选）
    Hx : ndarray  - x 方向的磁场分量（可选）

    返回：
    float - 计算得到的光学功率

    """
    if (len(Ey) != 0) and (len(Hx) != 0): # 如果提供了 Ey 和 Hx，使用完整的 Poynting 矢量计算功率
        Sz = 1/2 * np.real(Ex*np.conj(Hy)-Ey*np.conj(Hx))# Poynting 矢量的 z 分量
        return np.trapz(Sz,x) # 对空间进行积分，得到总功率
    elif len(Hy) != 0:
        Sz = np.real(Ex*np.conj(Hy))
        return np.trapz(Sz,x)
    else:
        return np.trapz(np.abs(Ex)**2,x)

def pnorm(x,Ex,Hy = [],Ey = [],Hx = []):
    """
    Normalizes field to unit power/intensity.对电场和磁场进行归一化处理，使得它们的总功率或强度等于单位值。
    """
    if (len(Ey) != 0) and (len(Hx) != 0):

        P = fpower(x,Ex,Hy,Ey,Hx)
        Exnorm = Ex/np.sqrt(P)
        Hynorm = Hy/np.sqrt(P)
        Eynorm = Ey/np.sqrt(P)
        Hxnorm = Hx/np.sqrt(P)
        return Exnorm,Hynorm,Eynorm,Hxnorm

    elif len(Hy) != 0:

        P = fpower(x,Ex,Hy)
        Exnorm = Ex/np.sqrt(P)
        Hynorm = Hy/np.sqrt(P)
        return Exnorm,Hynorm

    else:

        P = fpower(x,Ex)
        return Ex/np.sqrt(P)


def mat_prod(a, ma1,ma2):
    """
    Multiplication of multiple dimension array.

    a   - array of final dimension
    ma1 - first array  (mxn)
    ma2 - second array (nxn)
    """
    for i in range(len(a)):
        for j in range(len(a[i])):
            a[i][j] = ma1[i]*ma2[j]
    return a


def list_to_array(lst,dtype = complex):
    """
    Transform Python list to numpy array.
    """
    if len(lst) <= 2 or type(lst[0]) not in [int, float]:
        return np.array(list(lst))
    new_list = np.zeros(len(lst),dtype = dtype)
    for i,j in enumerate(lst):
        new_list[i] += j
    return new_list


def slabindex(lmbda0,t,na,nc,ns,**kwargs):
    """ Slabkwargsdex Guided mode effective index of planar waveguide.

    DESCRIPTION:
    Solves for the TE (or TM) effective index of a 3-layer slab waveguide
              na          y
      ^   ----------      |
      t       nc          x -- z
      v   ----------
              ns

      with propagation in the +z direction

    INPUT:
    lambda0 - freespace wavelength
    t  - core (guiding layer) thickness
    na - cladding index (number|function)
    nc - core index (number|function)
    ns - substrate index (number|function)

    OPTIONS:
    Modes - max number of modes to solve
    Polarisation - one of 'TE' or 'TM'

    OUTPUT:

    neff - vector of indexes of each supported mode

    NOTE: it is possible to provide a function of the form n = lambda lambda0: func(lambda0) for
    the refractive index which will be called using lambda0."""

    neff = []# 存储最终的有效折射率

    if "Modes" not in kwargs.keys():# 如果没有指定模式数目，则默认为无穷大（即求解所有模式）
        kwargs["Modes"] = np.inf

    if "Polarisation" not in kwargs.keys():# 如果没有指定偏振类型，则默认为"TE"
        kwargs["Polarisation"] = "TE"


    if (type(na) == types.FunctionType) or (str(type(na)) == "<class 'material.Material.Material'>"):# 如果折射率是一个函数或材料类实例，调用其计算折射率
        na = na(lmbda0)
    if (type(nc) == types.FunctionType) or (str(type(nc)) == "<class 'material.Material.Material'>"):
        nc = nc(lmbda0)
    if (type(ns) == types.FunctionType) or (str(type(ns)) == "<class 'material.Material.Material'>"):
        ns = ns(lmbda0)

    a0 = max(np.arcsin(ns/nc),np.arcsin(na/nc))# 计算a0值，即包层与芯层折射率的比值的反正弦值
    if np.imag(a0) != 0:# 如果a0的虚部不为0，说明计算结果不合法，直接返回空列表
        return neff

    if kwargs["Polarisation"].upper() == "TE": # 根据偏振类型计算TE或TM模式的有效折射率
        B1 = lambda a : np.sqrt(((ns/nc)**2 - np.sin(a)**2)+0j)# 对于TE模式，定义B1和B2等参数函数
        r1 = lambda a : (np.cos(a)-B1(a))/(np.cos(a)+B1(a))

        B2 = lambda a : np.sqrt(((na/nc)**2 - np.sin(a)**2)+0j)
    else:# 对于TM模式，定义B1和B2等参数函数
        B1 = lambda a : (nc/ns)**2*np.sqrt(((ns/nc)**2 - np.sin(a)**2)+0j)
        r1 = lambda a : (np.cos(a)-B1(a))/(np.cos(a)+B1(a))

        B2 = lambda a : (nc/na)**2*np.sqrt(((na/nc)**2 - np.sin(a)**2)+0j)
    # 定义r2和phi相关的函数
    r2 = lambda a : (np.cos(a)-B2(a))/(np.cos(a)+B2(a))

    phi1 = lambda a : np.angle(r1(a))
    phi2 = lambda a : np.angle(r2(a))
    # 计算有效折射率M，采用数学方法来求解
    M = math.floor((4*np.pi*t*nc/lmbda0*np.cos(a0)+phi1(a0) + phi2(a0))/(2*np.pi))

    for m in range(min(kwargs["Modes"],M+1)): # 遍历并计算每一个模式的有效折射率
        a = root(lambda a : 4*np.pi*t*nc/lmbda0*np.cos(a)+phi1(a)+phi2(a)-2*(m)*np.pi,1) # 使用牛顿求解法来求解每个模式的有效折射率
        neff.append((np.sin(a.x)*nc)[0])# 将计算的有效折射率添加到结果列表中
    return neff# 返回所有计算得到的有效折射率



def slabmode(lmbda0,t,na,nc,ns,**kwargs):
    """Slab_mode  Guided mode electromagnetic fields of the planar waveguide.Slab_mode  解决平面波导的导模电磁场问题。

    DESCRIPTION:
      solves for the TE (or TM) mode fields of a 3-layer planar waveguide解决3层平面波导的TE（或TM）模场问题

              na          y
      ^   ----------      |
      t       nc          x -- z
      v   ----------
              ns

      with propagation in the +z direction 在+z方向传播

    INPUT:
    lambda0   - simulation wavelength (freespace)仿真波长（自由空间）
    t         - core (guiding layer) thickness核心（导光层）厚度
    na        - top cladding index (number|function)
    nc        - core layer index (number|function)
    ns        - substrate layer index (number|function)
    y (optional) - provide the coordinate vector to use提供用于计算的坐标向量

    OPTIONS:
    Modes - max number of modes to solve最大求解模式数量
    Polarisation - one of 'TE' or 'TM'
    Limits - coordinate range [min,max] (if y was not provided)坐标范围[min, max]（如果没有提供y坐标）
    Points - number of coordinate points (if y was not provided)坐标点数（如果没有提供y坐标）

    OUTPUT:
    y - coordinate vector坐标向量
    E,H - all x,y,z field components, ex. E(<y>,<m>,<i>), where m is the mode
      number, i is the field component index such that 1: x, 2: y, 3:z所有x、y、z场分量，例：E(<y>,<m>,<i>)，
      其中m是模式编号，i是场分量索引，1: x, 2: y, 3: z

    NOTE: it is possible to provide a function of the form n = lambda lambda0: func(lambda0) for
    the refractive index which will be called using lambda0."""

    n0 = 120*np.pi

    _in = kwargs
    if "y" not in _in.keys():
        _in["y"] = []

    if "Modes" not in kwargs.keys():
        kwargs["Modes"] = np.inf
    if "Polarisation" not in _in.keys():
        _in["Polarisation"] = "TE"

    if "Range" not in _in.keys():
        _in["Range"] = [-3*t,3*t]
    if "points" not in _in.keys():
        _in["points"] = 100
    # 如果折射率是函数类型，则计算折射率
    if (type(na) == types.FunctionType) or (str(type(na)) == "<class 'material.Material.Material'>"):
        na = na(lmbda0)
    if (type(nc) == types.FunctionType) or (str(type(nc)) == "<class 'material.Material.Material'>"):
        nc = nc(lmbda0)
    if (type(ns) == types.FunctionType) or (str(type(ns)) == "<class 'material.Material.Material'>"):
        ns = ns(lmbda0)
    # 如果没有提供y坐标，则自动生成坐标
    if "y" not in _in or _in["y"] is None:
       _in["y"] = np.linspace(_in["Range"][0], _in["Range"][1], _in["points"])
    else:
        y = _in["y"]


    i1 = []# y < -t/2 区域
    i2 = []# -t/2 <= y <= t/2 区域
    i3 = []# y > t/2 区域
    for i,e in enumerate(y):
        if e < -t/2:
            i1.append(i)
        elif e <= t/2 and y[i] >= -t/2:
            i2.append(i)
        else:
            i3.append(i)
    # 计算有效折射率
    neff = slabindex(lmbda0,t,ns,nc,na,Modes = _in["Modes"],Polarisation = _in["Polarisation"])
    E = np.zeros((len(y), len(neff), 3), dtype=complex)
    H = np.zeros((len(y), len(neff), 3), dtype=complex)
    k0 = 2*np.pi/lmbda0# 真空波数
    for m in range(len(neff)):# 计算各层波数
        p = k0*np.sqrt(neff[m]**2 - ns**2)
        k = k0*np.sqrt(nc**2 - neff[m]**2)
        q = k0*np.sqrt(neff[m]**2 - na**2)

        if _in["Polarisation"].upper() == "TE":

            f = 0.5*np.arctan2(k*(p - q),(k**2 + p*q)) # 极化角度

            C = np.sqrt(n0/neff[m]/(t + 1/p + 1/q))# 归一化常数
            # 各区域的电场分量
            Em1 = np.cos(k*t/2 + f)*np.exp(p*(t/2 + y[i1]))
            Em2 = np.cos(k*y[i2] - f)
            Em3 = np.cos(k*t/2 - f)*np.exp(q*(t/2 - y[i3]))
            Em = np.concatenate((Em1,Em2,Em3))*C


            H[:,m,1] = neff[m]/n0*Em
            H[:,m,2] = 1j/(k0*n0)*np.concatenate((np.zeros(1),np.diff(Em)))
            E[:,m,0] = Em
        else:# 对于TM模式
            n = np.ones(len(y))
            n[i1] = ns
            n[i2] = nc
            n[i3] = na

            f = 0.5*np.arctan2((k/nc**2)*(p/ns**2 - q/na**2),((k/nc**2)**2 + p/ns**2*q/na**2))
            p2 = neff[m]**2/nc**2 + neff[m]**2/ns**2 - 1
            q2 = neff[m]**2/nc**2 + neff[m]**2/na**2 - 1


            C = -np.sqrt(nc**2/n0/neff[m]/(t+1/(p*p2) + 1/(q*q2)))
            Hm1 = np.cos(k*t/2 + f)*np.exp(p*(t/2 + y[i1]))
            Hm2 = np.cos(k*y[i2] - f)
            Hm3 = np.cos(k*t/2 - f)*np.exp(q*(t/2 - y[i3]))
            Hm = np.concatenate((Hm1,Hm2,Hm3))*C

            E[:,m,1] = -neff[m]*n0/n**2*Hm
            E[:,m,2] = -1j*n0/(k0*nc**2)*np.concatenate((np.zeros(1),np.diff(Hm)))
            H[:,m,0] = Hm


    return E,H,y,neff

def wgindex(lmbda0,w,h,t,na,nc,ns,**kwargs):
    """Effective index method for guided modes in arbitrary waveguide有效折射率方法用于任意波导中的导模

    DESCRIPTION:
      solves for the TE (or TM) effective index of an etched waveguide
      structure using the effectice index method.使用有效折射率方法计算刻蚀波导结构中TE（或TM）模式的有效折射率。

    USAGE:
      - get effective index for supported TE-like modes:获取支持的TE模式有效折射率:
      neff = eim_index(1.55, 0.5, 0.22, 0.09, 1, 3.47, 1.44)

                 |<   w   >|
                  _________           _____
                 |         |            ^
     ___    _____|         |_____
      ^                                 h
      t
     _v_    _____________________     __v__

             II  |    I    |  II

    INPUT:
    lambda0   - free-space wavelength
    w         - core width
    h         - slab thickness
    t         - slab thickness
                  t < h  : rib waveguide
                  t == 0 : rectangular waveguide w x h
                  t == h : uniform slab of thickness t
    na        - (top) oxide cladding layer material index (上)氧化物包层材料折射率
    nc        - (middle) core layer material index(中)芯层材料折射率
    ns        - (bottom) substrate layer material index(下)衬底材料折射率

    OPTIONS:
    Modes - number of modes to solve模式数目
    Polarisation - one of 'TE' or 'TM'模式的偏振，可以是'TE'或'TM'

    OUTPUT:
    neff - TE (or TM) mode index (array of index if multimode)TE（或TM）模式的有效折射率（若为多模，则为折射率的数组）

    NOTE: it is possible to provide a function of the form n = lambda lambda0: func(lambda0) for
    the refractive index which will be called using lambda0."""


    _in = kwargs
    if "Modes" not in _in.keys():# 如果没有指定模式数目，则默认为无穷大
        _in["Modes"] = np.inf

    if "Polarisation" not in _in.keys():# 如果没有指定偏振类型，则默认为"TE"
        _in["Polarisation"] = "TE"


    if (type(na) == types.FunctionType) or (str(type(na)) == "<class 'material.Material.Material'>"):# 如果折射率是一个函数或材料类实例，则调用该函数获取实际的折射率
        na = na(lmbda0)
    if (type(nc) == types.FunctionType) or (str(type(nc)) == "<class 'material.Material.Material'>"):
        nc = nc(lmbda0)
    if (type(ns) == types.FunctionType) or (str(type(ns)) == "<class 'material.Material.Material'>"):
        ns = ns(lmbda0)



    t = clamp(t,0,h)# 确保t的值不超过h

    neff_I = slabindex(lmbda0,h,na,nc,ns,Modes = _in["Modes"], Polarisation = _in["Polarisation"])# 计算第一部分（如果波导为脊波导，计算厚度h时的折射率）

    if t == h:# 如果t等于h，返回第一部分的结果
        return neff_I
    if t > 0:
        neff_II = slabindex(lmbda0,t,na,nc,ns,Modes = _in["Modes"],Polarisation = _in["Polarisation"]) # 如果t大于0，计算第二部分（厚度为t的波导折射率）
    else:
        neff_II = na #如果t小于0，则第二部分的折射率为na（上包层折射率）
    # 如果 neff_II 是一个 float，转换成列表
    if isinstance(neff_II, float):
        neff_II = [neff_II]

    neff = [] #存储最终结果的列表

    if _in["Polarisation"].upper() in "TE":# 如果偏振类型是TE
        # 遍历第一部分和第二部分的有效折射率，计算最终的TE模式有效折射率
        for m in range(min(len(neff_I),len(neff_II))):
            n = slabindex(lmbda0,w,neff_II[m],neff_I[m],neff_II[m],Modes = _in["Modes"],Polarisation = "TM")
            neff.extend(i for i in n if i > max(ns,na))# 仅保留大于衬底和包层折射率的模式
    else: # 如果偏振类型是TM，执行相同的计算，只是偏振类型改为"TE"
        for m in range(min(len(neff_I),len(neff_II))):
            n = slabindex(lmbda0,w,neff_II[m],neff_I[m],neff_II[m],Modes = _in["Modes"],Polarisation = "TE")
            neff.extend(i for i in n if i > max(ns,na))
    return neff# 返回有效折射率（单模或多模）


def wgmode(lmbda0,w,h,t,na,nc,ns,**kwargs):
    """	eim_mode   Solve 2D waveguide cross section by effective index method.使用有效折射率方法求解2D波导横截面模式。

    This function solves for the fundamental TE (or TM) mode fields using
    effective index method.此函数使用有效折射率方法计算基本的TE（或TM）模式场。

                 |<   w   >|
                  _________           _____
                 |         |            ^
     ___    _____|         |_____
      ^                                 h
      t
     _v_    _____________________     __v__

             II  |    I    |  II

    INPUT:
    lambda    - free space wavelength
    w         - core width
    h         - core thickness
    t         - slab thickness
                  t < h  : rib waveguide脊型波导
                  t == 0 : rectangular waveguide w x h矩形波导w x h
                  t == h : uniform slab of thickness t均匀薄膜，厚度为 t
    na        - (top) oxide cladding layer index of refraction（上）氧化物包层折射率
    nc        - (middle) core layer index of refraction（中）核心层折射率
    ns        - (bottom) substrate layer index of refraction（下）衬底层折射率
    x (optional) - provide the x coordinate vectors提供 x 坐标向量

    OPTIONS:
    Polarisation - one of 'TE' or 'TM'
    Limits - limits for autogenerated coordinates自动生成坐标的范围
    Points - number of points for autogenerated coordinates自动生成坐标的点数

    OUTPUT:
    E, H  - cell array of x, y and z field components such that E = {Ex, Ey, Ez}.包含 x、y 和 z 电场分量的数组，E = {Ex, Ey, Ez}
    x     - coordinate vector坐标向量
    neff  - effective index of the modes solved求解出的有效折射率

    NOTE: it is possible to provide a function of the form n = lambda lambda0: func(lambda0) for
    the refractive index which will be called using lambda0.
    注意：可以提供折射率的函数形式 n = lambda lambda0: func(lambda0)，
    其中 func(lambda0) 会在计算时使用 lmbda0 值来调用。
    """

    t = clamp(t,0,h) # 限制 t 的取值范围

    _in = kwargs.keys()

    if "Polarisation" in _in:# 设置极化类型，如果没有指定则默认为 "TE"
        if kwargs["Polarisation"] in ["TE","te","TM","tm"]:
            Polarisation = kwargs["Polarisation"]
    else:
        Polarisation = "TE"
    # 获取坐标范围和采样点数（默认x为[-3w，3w],point默认100）
    Xrange = kwargs["XRange"] if "XRange" in _in else [-3*w,3*w]
    Points = kwargs["Points"] if "Points" in _in else 100
    x = kwargs["x"] if "x" in _in else np.linspace(Xrange[0],Xrange[1],Points)
    # 如果折射率是函数类型，则调用它以获取具体的折射率值
    if (type(na) == types.FunctionType) or (str(type(na)) == "<class 'material.Material.Material'>"):
        na = na(lmbda0)
    if (type(nc) == types.FunctionType) or (str(type(nc)) == "<class 'material.Material.Material'>"):
        nc = nc(lmbda0)
    if (type(ns) == types.FunctionType) or (str(type(ns)) == "<class 'material.Material.Material'>"):
        ns = ns(lmbda0)


    ni1 = np.zeros(len(x),dtype =complex)# 初始化折射率数组
    # 根据极化类型计算电场和磁场
    if Polarisation.upper() in "TE":
        neff = wgindex(lmbda0,w,h,t,na,nc,ns,Polarisation = "TE",Modes = 1)[0]# TE模式：计算有效折射率

        n_I = slabindex(lmbda0,h,na,nc,ns,Polarisation = "TE",Modes = 1)[0]# 计算上层和核心层的折射率

        if t > 0 :# 如果 t > 0，计算薄膜层的折射率
            n_II = slabindex(lmbda0,t,na,nc,ns,Polarisation = "TE",Modes = 1)[0]
        else:
            n_II = na
        # 求解模式
        # print(_in)
        # print("x:", x)
        [Ek,Hk,_,_] = slabmode(lmbda0,w,n_II,n_I,n_II, Polarisation = "TM", y = x, Modes = 1)
        #print(Hk)
        # 归一化电场
        f = max(Ek[:,0,1])
        Ex = Ek[:,0,1]/f
        Hy = -Hk[:,0,0]/f
        Hz = -Hk[:,0,2]/f
        # 返回电场和磁场
        E = (Ex,ni1,ni1)
        H = (ni1,Hy,Hz)

    else:# TM模式
        neff = wgindex(lmbda0,w,h,t,na,nc,ns,Polarisation = "TM",Modes = 1)[0]

        n_I = slabindex(lmbda0,h,na,nc,ns,Polarisation = "TM",Modes = 1)[0]

        if t > 0 :
            n_II = slabindex(lmbda0,t,na,nc,ns,Polarisation = "TM",Modes = 1)[0]
        else:
            n_II = na

        [Ek,Hk,_,_] = slabmode(lmbda0,w,n_II,n_I,n_II, Polarisation = "TE")

        Ey = Ek[:,0,0]
        Ez = Ek[:,0,2]
        Hx = -Hk[:,0,1]

        E = (ni1,Ey,Ez)
        H = (Hx,ni1,ni1)



    return E,H,x,neff



def diffract(lmbda,ns,ui,xi,xf,zf, method = "rs"):
    """
    One dimensional Rayleigh-Sommerfeld diffraction integral calculation.一维瑞利-索末菲尔德衍射积分计算。
    This function numerically solves the Rayleigh-Sommerfeld integral from an
    input field vector at z=0 to an output coordinate (xf,zf) in the x-z plane.该函数通过数值计算瑞利-索末菲尔德积分，从z=0(xi,0)的输入场ui到x-z平面(xf, zf)的输出场uf

    INPUT:

      lambda - propagation wavelength
      ui - input plane complex amplitude输入平面复振幅
      xi - input plane coordinate vector输入平面坐标向量
      xf - output plane coordinate (single or vector of coordinates)输出平面坐标（可以是单点或向量）
      zf - propagation distance between input/output planes输入与输出平面之间的传播距离

    OUTPUT:

      uf - output plane field amplitude输出平面的场振幅
      xf - output plane coordinate (single or vector of coordinates)输出平面的坐标（可以是单点或向量）

    NOTE: uses retarded phase convention: exp(-1j*k*z)该函数使用延迟相位约定：exp(-1j*k*z)
    """
    if (len(zf) == 1) or (type(zf) == int) or (type(zf) == float):# 如果 zf 是单值，将其扩展为与 xf 长度一致的数组
        zf = zf*np.ones(len(xf))
    elif len(zf) != len(xf):# 检查 zf 和 xf 的长度
        raise ValueError('Coordinate vectors x and z must be the same length.')
    k = 2*np.pi*ns/lmbda # 计算波数 k

    uf = np.zeros(len(xf), dtype = complex) # 初始化输出场 uf

    for i in range(len(xf)): # 遍历输出平面的每个坐标 xf[i]
        r = np.sqrt((xf[i]-xi)**2+zf[i]**2)# 计算从 xi 到 xf[i] 的距离 r

        if method == "rs":# 根据方法计算输出场，# 瑞利-索末菲尔德积分
            uf[i] = np.sqrt(zf[i]/(2*np.pi))*np.trapz(ui*(1j*k+1/r)*np.exp(-1j*k*r)/r**2,xi)
        elif method == "fr": # 菲涅耳近似
            uf[i] = np.sqrt(1j/lmbda/zf[i])*np.exp(-1j*k*zf[i])*np.trapz(ui*np.exp(-1j*k/2/zf[i]*(xi-xf[i])**2),xi)



    return uf,xf# 返回计算的输出场 uf 和对应坐标 xf


def overlap(x,u,v,hu = None,hv = None):
    """
    DESCRIPTION:
       Computes the overlap integral in 1D with or without the H field.
       计算一维重叠积分（overlap integral），用于计算两个场之间的功率耦合效率，
       可选地考虑磁场分量。

     INPUTS:
       x - coordinate vector坐标向量
       u - incident field (electric)入射电场（electric field）
       v - outgoing field (electric)输出电场（electric field）
       Hu - (optional) corresponding incident magnetic field（可选）对应的入射磁场（magnetic field）
       Hv - (optional) corresponding outgoing magnetic field（可选）对应的输出磁场（magnetic field）

     OUTPUT:
       t - Power coupling efficiency功率耦合效率
    """
    if hu is None and hv is None:# 如果没有提供磁场分量，则仅计算电场的重叠积分
        uu = np.trapz(np.conj(u)*u,x)# 计算 u 的功率归一化项
        vv = np.trapz(np.conj(v)*v,x)# 计算 v 的功率归一化项
        uv = np.trapz(np.conj(u)*v,x) # 计算 u 与 v 的重叠积分


        return abs(uv)/abs(vv)# 归一化得到功率耦合效率
    else: # 如果缺少某个磁场分量，则用全零复数数组填充
        if hu is None:
            hu = np.zeros(len(hv),dtype = complex)
        if hv is None:
            hv = np.zeros(len(hu),dtype = complex)
        # 计算带有磁场分量的重叠积分
        uu = np.trapz(u[:]*np.conj(hu[:]),x);# 入射场的能量
        vv = np.trapz(v*np.conj(hv),x);# 输出场的能量
        uv = np.trapz(u[:]*np.conj(hv),x);# u 和 hv 之间的重叠积分
        vu = np.trapz(v*np.conj(hu[:]),x);# v 和 hu 之间的重叠积分


        return abs(np.real(uv*vu/vv)/np.real(uu))# 计算带磁场的功率耦合效率，并取其实部


def gmode(lmbda,W,H,nclad,ncore,**kwargs): # Always produce fake TE mode默认TE模式
    _in = kwargs.keys()
    # 如果传入了 x，则使用传入的 x，否则使用默认生成的空数组
    x = kwargs["x"] if "x" in _in else []
    # 获取 Limits 参数（x 坐标的计算范围，默认为 [-3*W, 3*W]）
    Limits = kwargs["Limits"] if "Limits" in _in else [-3*W,3*W]
    points = kwargs["points"] if "points"in _in else 100#x 坐标的离散点数，默认为 100
    VCoef = kwargs["VCoef"] if "VCoef" in _in else [0.337,0.650]#模式系数，默认为 [0.337, 0.650]
    if len(x) == 0:# 如果 x 为空，生成默认的 x 坐标
        x = np.linspace(Limits[0],Limits[1], points)

    # define central location of x      x is numpy array    ray
    x0 = 1/2 * (x[-1]+x[0])#高斯分布的中心位置
    #新代码，计算高斯场
    V = 2*np.pi*W/lmbda * np.sqrt(ncore**2 - nclad**2)
    #计算束腰半径w0
    w=W*(0.321+2.1*V**(-3/2)+4*V**(-6))
    h=H*(0.321+2.1*V**(-3/2)+4*V**(-6))

    # 计算折射率
    n = (nclad + ncore)/2



    #修改后的代码：理论上EX,HY为非零值，其他分量为0
    Ex = (2 / (np.pi * w**2))**(1 / 4) * np.exp(-(x-x0)**2 / w**2) + 0j  # TE mode: Ex is non-zero      ray
    Ey = np.zeros_like(x, dtype=complex)  # TE mode: Ey = 0
    Ez = np.zeros_like(x, dtype=complex)  # TE mode: Ez = 0



    Hx = np.zeros_like(x, dtype=complex)  # TE mode: Hx = 0
    Hy =n/(120*np.pi)* (2 / (np.pi * h**2))**(1 / 4) * np.exp(-(x-x0)**2 / h**2) + 0j  # TE mode: Hy is non-zero       ray
    Hz = np.zeros_like(x, dtype=complex)  # TE mode: Hz = 0

    # # Combine electric and magnetic field components into tuples
    E = (Ex, Ey, Ez)
    H = (Hx, Hy, Hz)



    return E,H,x



