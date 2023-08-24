# PyPhot API 接口文档

**注意：参考 pyhot 仓库的 toml 文件写**

## 生成随机二进制

- 函数名：gen_bits
- 前端显示名字：Random bits generator

输入参数

| 参数名   | 前端显示名字   | 数据类型 | 默认值 | 默认单位 | 单位类型 |
| -------- | -------------- | -------- | ------ | -------- | -------- |
| num_bits | Number of bits | int      | 393216 | 无       | 无       |

输出变量

- bit序列：bits

## 加入DAC噪声

- 函数名：dac_noise
- 前端显示名字：DAC noise

输入参数

| 参数名              | 前端显示名字        | 数据类型 | 默认值      | 默认单位 | 单位类型  |
| ------------------- | ------------------- | -------- | ----------- | -------- | --------- |
| sampling_rate_awg   | Sampling rate AWG   | int      | 96000000000 | hz       | frequency |
| sampling_rate       | Sampling rate       | int      | 40000000000 | hz       | frequency |
| dac_resolution_bits | DAC resolution bits | int      | 8           | 无       | 无        |

输入变量

- 输入信号：signals

输出变量

- 输出信号：signals

## 自适应均衡

- 函数名：adaptive_equalize
- 前端显示名字：Adaptive equalize
- 描述信息：自适应均衡

输入参数

| 参数名             | 前端显示名字           | 数据类型 | 默认值      | 默认单位 | 单位类型 |
| ------------------ | ---------------------- | -------- | ----------- | -------- | -------- |
| num_tap            | Number of tap          | int      | 25          | 无       | 无       |
| cma_convergence    | CMA convergence        | int      | 30000       | 无       | 无       |
| ref_power_cma      | reference power of CMA | int      | 2           | 无       | 无       |
| step_size_cma      | step size of CMA       | float    | 0.000000001 | 无       | 无       |
| step_size_rde      | step size of RDE       | float    | 0.000000001 | 无       | 无       |
| up_sampling_factor | up sampling factor     | int      | 2           | 无       | 无       |
| bits_per_symbol    | bits per symbol        | int      | 6           | 无       | 无       |
| total_baud         | total baud rate        | int      | 20000000000 | 无       | 无       |

输入变量

- 输入信号：signals

输出变量

- 输出信号：signals

## 添加频率偏移量

- 函数名：add_freq_offset
- 前端显示名字：Add frequency offset to signal

输入参数

| 参数名           | 前端显示名字     | 数据类型 | 默认值        | 默认单位 | 单位类型  |
| ---------------- | ---------------- | -------- | ------------- | -------- | --------- |
| frequency_offset | Frequency offset | float    | 2000000000    | 无       | 无        |
| sampling_rate    | Sampling rate    | float    | 1024000000000 | hz       | frequency |

输入变量

- 输入信号：signals

输出变量

- 输出信号：signals

## 位错误计数器

- 函数名：bits_error_count
- 前端显示名字：Bits error counter

输入参数

| 参数名          | 前端显示名字    | 数据类型 | 默认值 | 默认单位 | 单位类型 |
| --------------- | --------------- | -------- | ------ | -------- | -------- |
| bits_per_symbol | bits per symbol | int      | 6      | 无       | 无       |

输入变量

- 输入信号：signals
- 上一个输入符号：prev_symbols

输出变量

- 位错误率：ber
- Q因子（db）：q_factor

## 星座图

- 函数名：constellation_diagram
- 前端显示名字：Constellation diagram
- 是否为分析器：是

输入参数

| 参数名  | 前端显示名字  | 数据类型 | 默认值 | 默认单位 | 单位类型 |
| ------- | ------------- | -------- | ------ | -------- | -------- |
| signals | Input signals | 无       | 无     | 无       | 无       |

输入变量

- 输入信号：signals

输出变量

无

## 眼图

- 函数名：eye_diagram
- 前端显示名字：Eye diagram
- 描述信息：A function of analyzer, plot eye diagram

输入参数

| 参数名             | 前端显示名字       | 数据类型 | 默认值 | 默认单位 | 单位类型 |
| ------------------ | ------------------ | -------- | ------ | -------- | -------- |
| up_sampling_factor | Up sampling factor | int      | 2      | 无       | 无       |


输入变量

- 输入信号：signals

## IQ频偏和补偿

- 函数名：freq_offset_compensation
- 前端显示名字：IQ frequency offset and compensation

输入参数

| 参数名        | 前端显示名字  | 数据类型 | 默认值        | 默认单位 | 单位类型  |
| ------------- | ------------- | -------- | ------------- | -------- | --------- |
| sampling_rate | Sampling rate | float    | 1024000000000 | hz       | frequency |

输入变量

- 信号：signals

输出变量

- 信号：signals

## IQ正交化补偿

- 函数名：iq_compensation
- 前端显示名字：IQ compensation
- 描述信息：IQ正交化补偿

输入参数

| 参数名        | 前端显示名字    | 数据类型 | 默认值                         | 默认单位 | 单位类型  |
| ------------- | --------------- | -------- | ------------------------------ | -------- | --------- |
| sampling_rate | Sampling rate   | float    | 1024000000000                  | Hz       | frequency |
| beta2         | beta2           | float    | 0.0000000000000000000000216676 | 无       | 无        |
| span          | Simulation span | int      | 5                              | 无       | 无        |
| L             | Length          | int      | 75                             | km       | length    |

输入变量

- 输入信号：signals
- 输入信号功率：signals_power

输出变量

- 输出信号：signals

 ## 脉冲整形器

- 类名：PulseShaper
- 前端显示名字：Pulse shaper
- 描述信息：Quadrature Amplitude Modulation (QAM) Modulate

输入参数

| 参数名             | 前端显示名字         | 数据类型 | 默认值 | 默认单位 | 单位类型 |
| ------------------ | -------------------- | -------- | ------ | -------- | -------- |
| up_sampling_factor | Up sampling factor   | int      | 2      | 无       | 无       |
| alpha              | Roll-off coefficient | float    | 0.02   | 无       | 无       |

成员方法

##### tx_shape

输入变量

| 变量名  | 前端显示名字 | 数据类型 | 默认值 | 默认单位 | 单位类型 |
| ------- | ------------ | -------- | ------ | -------- | -------- |
| symbols | Symbols      | 无       | 无     | 无       | 无       |

输出变量

| 变量名  | 前端显示名字 | 数据类型 | 默认值 | 默认单位 | 单位类型 |
| ------- | ------------ | -------- | ------ | -------- | -------- |
| signals | Signals      | 无       | 无     | 无       | 无       |

##### rx_shape

输入变量

| 变量名  | 前端显示名字 | 数据类型 | 默认值 | 默认单位 | 单位类型 |
| ------- | ------------ | -------- | ------ | -------- | -------- |
| signals | Signals      | 无       | 无     | 无       | 无       |

输出变量

| 变量名  | 前端显示名字 | 数据类型 | 默认值 | 默认单位 | 单位类型 |
| ------- | ------------ | -------- | ------ | -------- | -------- |
| signals | Signals      | 无       | 无     | 无       | 无       |

## 添加ADC噪声

- 函数名：add_adc_noise
- 前端显示名字：Add ADC noise
- 描述信息：Add ADC noise to signal

输入参数

| 参数名              | 前端显示名字     | 数据类型 | 默认值        | 默认单位 | 单位类型  |
| ------------------- | ---------------- | -------- | ------------- | -------- | --------- |
| sampling_rate       | Sampling rate    | int      | 1024000000000 | hz       | frequency |
| adc_sample_rate     | Frequency offset | int      | 160000000000  | hz       | frequency |
| adc_resolution_bits | Frequency offset | int      | 8             | 无       | 无        |

输入变量

- 输入信号序列：signals

输出变量

- 输出信号序列：signals

## 添加频率IQ失衡

- 函数名：add_iq_imbalance
- 前端显示名字：Add frequency IQ imbalance

输入变量

- 输入信号序列：signals

输出变量

- 输出信号序列：signals

## BPS 恢复

- 函数名：bps_restore
- 前端显示名字：BPS restore

输入参数

| 参数名          | 前端显示名字          | 数据类型 | 默认值 | 默认单位 | 单位类型 |
| --------------- | --------------------- | -------- | ------ | -------- | -------- |
| num_test_angle  | number of test angles | int      | 64     | 无       | 无       |
| block_size      | block size            | int      | 100    | 无       | 无       |
| bits_per_symbol | bits per symbol       | int      | 6      | 无       | 无       |

输出变量

- 信号序列：signals

## 光纤

- 函数名：fiber
- 前端显示名字：Optical fiber
- 描述：单芯单模双偏振光纤

输入参数

| 参数名        | 前端显示名字    | 数据类型 | 默认值                         | 默认单位 | 单位类型  |
| ------------- | --------------- | -------- | ------------------------------ | -------- | --------- |
| sampling_rate | Sampling rate   | float    | 1024000000000                  | hz       | frequency |
| num_spans     | Number of spans | int      | 5                              | 无       | 无        |
| beta2         | beta2           | float    | 0.0000000000000000000000216676 | 无       | 无        |
| delta_z       | Step length     | float    | 1                              | 无       | 无        |
| gamma         | gamma           | float    | 1.3                            | 无       | 无        |
| alpha         | alpha           | float    | 0.2                            | 无       | 无        |
| span_length   | Span length     | int      | 75                             | km       | length    |

输出变量

- 信号序列：signals

输出变量

- 信号：signals
- 输出信号功率：signals_power

## 加入高斯白噪声

- 函数名：gaussian_noise
- 前端显示名字：Gaussian noise
- 描述信息：根据设置的OSNR来加入高斯白噪声

输入参数

| 参数名        | 前端显示名字  | 数据类型 | 默认值      | 默认单位 | 单位类型  |
| ------------- | ------------- | -------- | ----------- | -------- | --------- |
| osnr_db       | OSNR          | float    | 50          | db       | sound     |
| sampling_rate | Sampling rate | int      | 40000000000 | hz       | frequency |

输入变量

- 输入信号序列：signals

输出变量

- 输出信号序列：signals

## 加入发射端激光器产生的相位噪声

- 函数名：phase_noise
- 前端显示名字：Phase noise
- 描述信息：加入发射端激光器产生的相位噪声

输入参数

| 参数名             | 前端显示名字       | 数据类型 | 默认值      | 默认单位 | 单位类型  |
| ------------------ | ------------------ | -------- | ----------- | -------- | --------- |
| over_sampling_rate | Over sampling rate | int      | 2           | 无       | 无        |
| sampling_rate      | Sampling rate      | int      | 40000000000 | hz       | frequency |
| linewidth          | Linewidth          | int      | 150000      | 无       | 无        |
| total_baud         | Total baud         | int      | 20000000000 | 无       | 无        |

输入变量

- 输入信号：signals

输出变量

- 输出信号：signals

## QAM调制器

- 函数名：qam_modulate
- 前端显示名字：QAM modulate
- 描述信息：Quadrature Amplitude Modulation (QAM) Modulate

输入参数

| 参数名          | 前端显示名字    | 数据类型 | 默认值 | 默认单位 | 单位类型 |
| --------------- | --------------- | -------- | ------ | -------- | -------- |
| bits_per_symbol | Bits per symbol | int      | 6      | 无       | 无       |

输入变量

- 输入比特序列：bits

输出变量

- 输出符号：symbols

## 同步帧

- 函数名：sync_frame
- 前端显示名字：Synchronize frame

输入参数

| 参数名             | 前端显示名字       | 数据类型 | 默认值 | 默认单位 | 单位类型 |
| ------------------ | ------------------ | -------- | ------ | -------- | -------- |
| up_sampling_factor | up sampling factor | int      | 2      | 无       | 无       |

输入变量

- 输入信号：signals
- 上次输入信号：prev_symbols

输出变量

- 输入信号：signals
- 上次输入信号：prev_symbols
