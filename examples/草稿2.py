import numpy as np
from photfdtd.fdtd import constants
f = 20e-2 #m
c = constants.c
FWHM = 1e-3#m
lam = 1030e-9#m
w0 = FWHM/(np.sqrt(2*np.log(2)))
zR = np.pi * w0**2 / lam
z0 = 1000000000
Mr = abs(f/(z0-f))
r = zR/(z0-f)
M = Mr/np.sqrt(1+r ** 2)
w = f * w0/zR #m
print(f/zR)
# (b)
P0 = 1e-3 * 1e13*1e-6 # W
I = 2*P0/(np.pi*(w*1e-2)**2) #W*s-1*m-2
print(f"peak intensity, {I}")
h_bar = 1.0545e-34 / (1.60218e-19) #eV*s
h = h_bar * 2 * np.pi
v = c / lam
Eg = 1.12 #eV
mv=1.08
mc=0.57
mr = 1/(1/mv+1/mc)
print(h*v-Eg)
rho = (2*mr) ** 1.5/(np.pi * h_bar ** 2) * (h*v-Eg)**0.5
print(rho)
# (c)
T=100e-15#s
alpha=0.0063#/m
d=1000e-6#m
tao=1e-6#s
Iavg=I*1e-7/np.sqrt(2*np.pi) #W*s-1*m-2
print(f"I_avg: {Iavg}")
GL=Iavg/(alpha*h*v*(1.60218e-19))*(1-np.exp(-alpha*d))
delta_n=GL*tao
print(f"delta_n: {delta_n}")
'''6'''
Eg_half=-0.75#eV
T = np.array([300, 600])
m0=0.5110*1e6#eV
me=0.06*m0
e=1#e
kB=8.6173303e-5#eV/K
Nc=2*(2*np.pi*me*kB*T/h**2)
ne=Nc*np.exp(Eg_half/(kB*T))
pf = np.sqrt(ne*e**2/(constants.eps0*me))
print(f"plasma frequencies are{pf}")
