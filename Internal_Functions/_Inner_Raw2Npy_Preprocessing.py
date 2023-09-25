# _*_coding:utf-8_*_
"""
@File       : _Inner_Raw2Npy_Preprocessing.py
@Project:   : 
@Time       ：2022/9/16-20:07
@Author     : Long  Fan
@Software   : PyCharm
@License    : (C) Copyright 2021-2031, NanJing University

@Last Modify Time      @Version         @Description
-----------------      ---------        ------------
2022/9/16-20:07          1.0             None
"""

import matplotlib.pyplot as plt
import numpy as np
import os
import sys

sys.path.append(os.path.join(os.getcwd(), "../"))
from Internal_Functions.IWR6843_Parser_Config import parse_config_file
from Internal_Functions.parser_lvds_demo_captured_file import get_HW_ADC_Buffer


def RawData2NumpyData(RawData_Path, NumpyData_Path, config_file, isPrefix=False):
    if RawData_Path is None or config_file is None:
        print("ERROR: g_range_profile_data=None or output_data_path=None")
        raise InterruptedError
    if NumpyData_Path is None:
        NumpyData_Path = RawData_Path
        print("Message: Set NumpyData_Path to RawData_Path.")

    # 1. 读取config文件
    # datacard_prefix: filename prefix provided to DCA1000 CLI;

    datacard_prefix = None
    if isPrefix:
        datacard_prefix = RawData_Path
    else:
        datacard_prefix = RawData_Path + r"/raw_recoder"

    # numFramesToBePrint: if debug data needs to be printed by the parser script
    numFramesToBePrint = 10  # print log
    # 输出参数配置信息
    parameters = parse_config_file(config_file)

    # 2. 读取recoder数据
    # call the parser API
    HW_ADC_buffer = get_HW_ADC_Buffer(config_file, numFramesToBePrint, datacard_prefix)
    ADC_Cube = np.array(HW_ADC_buffer).astype(np.float16)
    real_buffer = ADC_Cube[:, :, :, 1::2]
    imag_buffer = ADC_Cube[:, :, :, 0::2]
    ADC_Cube_complex = real_buffer + 1j * imag_buffer
    print("ADC_Cube buffer shape[frames, chirps, numRx, Samples]: {}".format(ADC_Cube_complex.shape))

    np.save(NumpyData_Path + r"/{}.npy".format(os.path.basename(datacard_prefix)), ADC_Cube_complex)
    print("{}/raw_recoder.npy Success!".format(NumpyData_Path))

    return ADC_Cube_complex


if __name__ == "__main__":
    plt.close('all')
    RawData_Path = os.path.join(os.getcwd(), "../Dataset/")
    NumpyData_Path = os.path.join(os.getcwd(), "../Dataset")
    ConfigFile = "LPD_Hybrid_Beam_Steering_VitalSigns_.cfg"
    config_file = os.path.join(os.getcwd(), "../Data_Collecting/Config_files/" + ConfigFile)

    cube = RawData2NumpyData(RawData_Path, NumpyData_Path, config_file)


    # Reshape data, [frames, beams, doppler, nRx, Samples]
    beam_num = 4
    ADC_Cube_complex = np.reshape(cube[:beam_num*(cube.shape[0]//beam_num),...], (cube.shape[0]//beam_num, beam_num,
                                  cube.shape[1], cube.shape[2], cube.shape[3]))




    print("done")
