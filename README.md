# Spectrum AWG python driver

## 使用说明

需要在已安装Spectrum AWG驱动的电脑上运行。

目前简单实现了光镊阵列简单移动需要的波形生成，时序触发相关的内容尚未完善。

主要程序位于awg2.py中。



### 附：AWG m4i66 双通道接口操作说明

[^m4i66]: high-speed 16 bit AWG

#### 波信息存储方式

一段任意波形可以用三个元素表示：1、一个整型序列a，用于存储波形信息；2、时间序列t；3、位移序列y；

即：在时间 t[i] 处，波的位移为 y[a[i]]

在具体的实现中，一般会规定采样频率 fs ，和单位位移dy，则时间 i/fs 处 位移为 y[i]*dy

总之，在规定采样频率和单位位移后，一个整型序列即可表示一段任意波形，一个整数（该设备要用int16）可以表示一个位移信息。

计算机通过缓存(buffer)向AWG中传送波形信息。buffer是一段01序列，每隔一定位数存储一个位移信息。要实现双通道输出，则可以将间隔位数设定为32位。由于每16位表示一个位移信息，32位可分别表示两个通道的位移信息。

#### 双通道设定方式

[^self.hCard]: 这里表示设备的句柄

```python
spcm_dwSetParam_i64 (self.hCard, SPC_CHENABLE,   CHANNEL0 | CHANNEL1 )
```

这里表示两个通道都被激活

```python
spcm_dwSetParam_i64 (self.hCard, SPC_ENABLEOUT0,  1)
spcm_dwSetParam_i64 (self.hCard, SPC_ENABLEOUT1,  1)

```

这里授权了两个通道的输出

```python
def normalize(arr):
    max = np.abs(np.max(arr)) if np.abs(np.max(arr))>np.abs(np.min(arr)) else np.abs(np.min(arr))
    return arr/max
def convert_to_int2(arr):
    return np.round(32767*arr).astype(np.int32)
```

定义归一化操作与整数化操作。注意，这里只将归一化后的arr*32767，即拓展到16位，但是整数化后类型为int32，是为了便于双通道信息的存储。

```python
a = convert_to_int2(normalize(waveform1))
b = convert_to_int2(normalize(waveform2))
ab=a+b*(2**16)
pnBuffer = ab.ctypes.data_as(ptr32)
```

关键操作：ab=a+b*(2^16)，即将a，b两个波的信息，错位安放。pnBuffer是对Buffer的指针，注意要定义为32位整型指针(ptr32)

之后将pnBuffer利用spcm_dwDefTransfer_i64传送到AWG硬件即可，两个波的信息会被自动传送到两个通道

#### 库函数使用指南

```python
awg=AWG2()
awg.open()#打开硬件
awg.set_buffer_size(8192)#设定buffer_size,采样规模，单位：k个
#self.llMemSamples=1024*buffer_size, 表示采样点总数
awg.config()#初始化
awg.arbitrary_synthesis(wv1,wv2,time_out)#输出双通道波形
```

这里wv1，wv2即要输出的两个波形数组。注意两个数组的长度一定要与先前设定的self.llMemSamples数值一致



[^注]: 具体代码参见/AWG2_pack/awg2.py

