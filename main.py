
import os

import matplotlib.pyplot as plt

import numpy as np
from Internal_Functions import IWR6843_Parser_Config
from Internal_Functions._Inner_Raw2Npy_Preprocessing import RawData2NumpyData

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    ConfigFile = "Demo_3Tx4RxMIMO.cfg"
    config_file = os.path.join(os.path.abspath("./"), ConfigFile)

    raw_data = "Dataset/"
    NumpyData_Path = raw_data

    parameters = IWR6843_Parser_Config.parse_config_file(ConfigFile)  # 打印输出 配置参数
    # 解析数据 RAW -> npy
    ADC_Cube_complex = RawData2NumpyData(raw_data, NumpyData_Path, config_file)

    for i in range(ADC_Cube_complex.shape[0]):

        cur_frame = ADC_Cube_complex[i, ...]

        # (1) Range FFT
        Out_1DFFT = np.fft.fft(cur_frame, axis=-1)
        plt.figure(1)
        plt.plot(abs(Out_1DFFT[1, 1, :]))
        plt.pause(0.01)

        # (2) Doppler FFT
        # get 1TX, 1Rx data
        fft2d_in = Out_1DFFT[::3, :, :]
        fft2d_in = np.transpose(fft2d_in, axes=(2, 1, 0))
        Out_2DFFT = np.fft.fftshift(np.fft.fft(fft2d_in, axis=-1))
        Out_2DFFT_log = 10*np.log10(abs(Out_2DFFT))
        plt.figure(2)
        plt.imshow(Out_2DFFT_log[:, 1, :], aspect='auto', cmap='jet')
        plt.pause(0.01)




    print("Done.")

