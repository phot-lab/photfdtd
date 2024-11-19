import numpy as np
import matplotlib.pyplot as plt
neff = [2.8249367292552665+3.55572992979015E-12j, 2.725079730355833+5.0539625854543014E-11j, 2.043847532170219+3.6240008997592956E-8j,
1.7508952067195827-2.6071582039007206E-7j, 1.5630548490739649+2.7244086473295554E-6j]
neff_pyphotpassive= [2.75575402-7.05413071e-16j, 2.65038983+8.79871794e-15j]

imag = np.imag(neff)
real = np.real(neff)
imag_pyphotpassive = np.imag(neff_pyphotpassive)
real_pyphotpassive = np.real(neff_pyphotpassive)

filepath = "E:\\campus\\高速长距光纤传输系统软件设计平台\\中期\\曲线图"
l1, = plt.plot(np.linspace(1, len(real), len(real)), real, label='Line',
         marker="o")
l2, = plt.plot(np.linspace(1, len(real_pyphotpassive), len(real_pyphotpassive)), real_pyphotpassive, label='Line',
         marker="o")
plt.legend([l1, l2], ["Comsol", "Pyphotpassive"])

plt.title('neff plot')
plt.xticks(np.arange(1, len(real), 1))
plt.xlabel('mode')
plt.savefig(fname='%s\\%s.png' % (filepath, 'neff_plot'))
plt.close()

loss, loss_pyphotpassive = np.empty_like(imag), np.empty_like(imag_pyphotpassive)
for i in range(len(imag)):
    print(i)
    loss[i] = -20 * np.log10(np.e ** (-2 * np.pi * imag[i] / (1550e-9)))
    try:
        loss_pyphotpassive[i] = -20 * np.log10(np.e ** (-2 * np.pi * imag_pyphotpassive[i] / (1550e-9)))
    except:
        continue
l1, = plt.plot(np.linspace(1, len(imag), len(imag)), loss, label='Line',
         marker="o")
l2, = plt.plot(np.linspace(1, len(imag_pyphotpassive), len(imag_pyphotpassive)), loss_pyphotpassive, label='Line',
         marker="o")
plt.legend([l1, l2], ["Comsol", "Pyphotpassive"])
plt.title('loss plot')
plt.xticks(np.arange(1, len(imag), 1))
plt.xlabel('mode')
plt.ylabel('dB/m')
plt.savefig(fname='%s\\%s.png' % (filepath, 'loss_plot'))
plt.close()
