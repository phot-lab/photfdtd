import numpy as np
import matplotlib.pyplot as plt
neff = [1.4469999230486192-2.1737798046280357E-11j ,1.44699991945947-2.1688276234728036E-11j, 1.4435467687445382-9.303749287415494E-6j,
1.4435433520012488-9.658407165974244E-6j, 1.443403426550843-2.255430767442035E-5j, 1.4433987680238394-2.2937769235794295E-5j 
        ]
neff_pyphotpassive= [1.44700181+1.82689044e-09j, 1.44700163+1.82764295e-09j,
 1.44362898-1.43298623e-05j, 1.4436299 -1.40922924e-05j,
 1.44343175-3.64070451e-05j, 1.44343157-3.64509015e-05j]

imag = np.imag(neff)
real = np.real(neff)
imag_pyphotpassive = np.imag(neff_pyphotpassive)
real_pyphotpassive = np.real(neff_pyphotpassive)

filepath = "E:\\campus\\高速长距光纤传输系统软件设计平台\\中期\\曲线图"
l1, = plt.plot(np.linspace(1, len(real), len(real)), real, label='Line',
         marker="o")
l2, = plt.plot(np.linspace(1, len(real), len(real)), real_pyphotpassive, label='Line',
         marker="o")
plt.legend([l1, l2], ["Comsol", "Pyphotpassive"])

plt.title('neff plot')
plt.xticks(np.arange(1, len(real), 1))
plt.xlabel('mode')
plt.savefig(fname='%s\\%s.png' % (filepath, 'neff_plot'))
plt.close()

loss, loss_pyphotpassive = np.empty_like(imag), np.empty_like(imag)
for i in range(len(imag)):
    print(i)
    loss[i] = -20 * np.log10(np.e ** (-2 * np.pi * imag[i] / (1550e-9)))
    loss_pyphotpassive[i] = -20 * np.log10(np.e ** (-2 * np.pi * imag_pyphotpassive[i] / (1550e-9)))
l1, = plt.plot(np.linspace(1, len(imag), len(imag)), loss, label='Line',
         marker="o")
l2, = plt.plot(np.linspace(1, len(imag), len(imag)), loss_pyphotpassive, label='Line',
         marker="o")
plt.legend([l1, l2], ["Comsol", "Pyphotpassive"])
plt.title('loss plot')
plt.xticks(np.arange(1, len(imag), 1))
plt.xlabel('mode')
plt.ylabel('dB/m')
plt.savefig(fname='%s\\%s.png' % (filepath, 'loss_plot'))
plt.close()
