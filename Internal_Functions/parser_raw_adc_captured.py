import math
from enum import Enum
import numpy as np

class CMD(Enum):
    RESET_FPGA_CMD_CODE = '0100'
    RESET_AR_DEV_CMD_CODE = '0200'
    CONFIG_FPGA_GEN_CMD_CODE = '0300'
    CONFIG_EEPROM_CMD_CODE = '0400'
    RECORD_START_CMD_CODE = '0500'
    RECORD_STOP_CMD_CODE = '0600'
    PLAYBACK_START_CMD_CODE = '0700'
    PLAYBACK_STOP_CMD_CODE = '0800'
    SYSTEM_CONNECT_CMD_CODE = '0900'
    SYSTEM_ERROR_CMD_CODE = '0a00'
    CONFIG_PACKET_DATA_CMD_CODE = '0b00'
    CONFIG_DATA_MODE_AR_DEV_CMD_CODE = '0c00'
    INIT_FPGA_PLAYBACK_CMD_CODE = '0d00'
    READ_FPGA_VERSION_CMD_CODE = '0e00'

    def __str__(self):
        return str(self.value)


# Global variables hold test configurations
# Set one time per test by read_config() function when read configuration parameters from test profile file
# Used by parser processing
CFG_PARAMS = {}

numOfChirps_buf = []
numLoops_buf = []
freqSlope_buf = []
numAdcSamples_buf = []
adcSampleRate_buf = []
profileIdx_buf = []
SigImgNumSlices_buf = []
RxSatNumSlices_buf = []
chanIdx_buf = []

lvdsCfg_headerEn_buf = []
lvdsCfg_dataFmt_buf = []
lvdsCfg_userBufEn_buf = []

Raw_file_numSubframes = 0
Raw_file_subframeIdx_buf = []
Raw_file_sessionFlag = ""

ADC_file_numSubframes = 0
ADC_file_subframeIdx_buf = []
ADC_file_sessionFlag = ""

CC9_file_numSubframes = 0
CC9_file_subframeIdx_buf = []
CC9_file_sessionFlag = ""

# Definations for test pass/fail or not_apply/don't care
NOT_APPLY = -1
TC_PASS = 0
TC_FAIL = 1

# MESSAGE = codecs.decode(b'5aa509000000aaee', 'hex')
CONFIG_HEADER = '5aa5'
HEADER_Num = 0xa55a
CONFIG_STATUS = '0000'
STATUS_STR = {0: 'success', 1: 'failed'}
CONFIG_FOOTER = 'aaee'
FOOTER_Num = 0xeeaa

ADC_PARAMS = {'chirps': 128,  # 32
              'rx': 4,
              'tx': 1,
              'samples': 64,
              'IQ': 2,
              'bytes': 2}
# STATIC
MAX_PACKET_SIZE = 4096
BYTES_IN_PACKET = 1456  # Data in payload per packet from FPGA
BYTES_OF_PACKET = 1466  # payload size per packet from FPGA
MAX_BYTES_PER_PACKET = 1470  # Maximum bytes in the data packet
FPGA_CLK_CONVERSION_FACTOR = 1000  # Record packet delay clock conversion factor
FPGA_CLK_PERIOD_IN_NANO_SEC = 8  # Record packet delay clock period in ns
VERSION_BITS_DECODE = 0x7F  # Version bits decode
VERSION_NUM_OF_BITS = 7  # Number of bits required for version
PLAYBACK_BIT_DECODE = 0x4000  # Playback FPGA bitfile identifier bit
# DYNAMIC
BYTES_IN_FRAME = (ADC_PARAMS['chirps'] * ADC_PARAMS['rx'] * ADC_PARAMS['tx'] *
                  ADC_PARAMS['IQ'] * ADC_PARAMS['samples'] * ADC_PARAMS['bytes'])

BYTES_IN_FRAME_CLIPPED = (BYTES_IN_FRAME // BYTES_IN_PACKET) * BYTES_IN_PACKET

PACKETS_IN_FRAME = BYTES_IN_FRAME / BYTES_IN_PACKET

PACKETS_IN_FRAME_CLIPPED = BYTES_IN_FRAME // BYTES_IN_PACKET
UINT16_IN_PACKET = BYTES_IN_PACKET // 2
UINT16_IN_FRAME = BYTES_IN_FRAME // 2


def read_config(config_file_name):
    """!
    This function read config from test profile file and fills up global variables to contain the configuration

        @param config_file_name : test config profile file name
        @return None
    """
    global CFG_PARAMS
    global ADC_PARAMS

    global numOfChirps_buf
    global numLoops_buf
    global numAdcSamples_buf
    global adcSampleRate_buf
    global freqSlope_buf
    global profileIdx_buf
    global SigImgNumSlices_buf
    global RxSatNumSlices_buf
    global chanIdx_buf

    global lvdsCfg_headerEn_buf
    global lvdsCfg_dataFmt_buf
    global lvdsCfg_userBufEn_buf

    global Raw_file_numSubframes
    global Raw_file_subframeIdx_buf
    global Raw_file_sessionFlag

    global ADC_file_numSubframes
    global ADC_file_subframeIdx_buf
    global ADC_file_sessionFlag

    global CC9_file_numSubframes
    global CC9_file_subframeIdx_buf
    global CC9_file_sessionFlag

    CFG_PARAMS = {}
    ADC_PARAMS = {}
    numOfChirps_buf = []
    numLoops_buf = []
    numAdcSamples_buf = []
    adcSampleRate_buf = []
    freqSlope_buf = []
    profileIdx_buf = []
    SigImgNumSlices_buf = []
    RxSatNumSlices_buf = []
    chanIdx_buf = []
    lvdsCfg_headerEn_buf = []
    lvdsCfg_dataFmt_buf = []
    lvdsCfg_userBufEn_buf = []
    Raw_file_subframeIdx_buf = []
    ADC_file_subframeIdx_buf = []
    CC9_file_subframeIdx_buf = []

    config = open(config_file_name, 'r')

    for line in config:
        # print("**** line from config file: \n" + line)
        List = line.split()

        if 'channelCfg' in line:
            CFG_PARAMS['rxAntMask'] = int(List[1])
            CFG_PARAMS['txAntMask'] = int(List[2])
        if 'adcCfg' in line:
            CFG_PARAMS['dataSize'] = int(List[1])
            CFG_PARAMS['dataType'] = int(List[2])
        if 'adcbufCfg' in line:
            CFG_PARAMS['chirpMode'] = int(List[5])

        if 'profileCfg' in line:
            profileIdx_buf.append(int(List[1]))
            ADC_PARAMS['startFreq'] = float(List[2])
            freqSlope_buf.append(float(List[8]))
            numAdcSamples_buf.append(int(List[10]))
            adcSampleRate_buf.append(float(List[11]))
            idleTime = float(List[3])
            rampEndTime = float(List[5])
            ADC_PARAMS['idleTime'] = idleTime
            ADC_PARAMS['adc_valid_start_time'] = float(List[4])
            ADC_PARAMS['rampEndTime'] = rampEndTime
            ADC_PARAMS['freq_slope'] = freqSlope_buf[0]
            ADC_PARAMS['txStartTime'] = float(List[9])
            ADC_PARAMS['samples'] = numAdcSamples_buf[0]
            ADC_PARAMS['sample_rate'] = adcSampleRate_buf[0]

        if 'frameCfg' in line:
            CFG_PARAMS['chirpStartIdx'] = int(List[1])
            CFG_PARAMS['chirpEndIdx'] = int(List[2])
            numOfChirps_buf.append(CFG_PARAMS['chirpEndIdx'] - CFG_PARAMS['chirpStartIdx'] + 1)
            numLoops_buf.append(int(List[3]))
            CFG_PARAMS['numSubframes'] = 1
            ADC_PARAMS['chirps'] = numLoops_buf[0]
            ADC_PARAMS['frame_periodicity'] = float(List[5])

        if 'advFrameCfg' in line:
            CFG_PARAMS['numSubframes'] = int(List[1])
            CFG_PARAMS['txAntMask'] = 1

        if 'subFrameCfg' in line:
            numOfChirps_buf.append(int(List[4]))
            numLoops_buf.append(int(List[5]))
            ADC_PARAMS['chirps'] = numLoops_buf[0]
            ADC_PARAMS["subFrameNum"] = int(List[1])
            ADC_PARAMS["forceProfileIdx"] = int(List[2])
            ADC_PARAMS["chirpStartIdx"] = int(List[3])
            ADC_PARAMS["burstPeriodicity"] = int(List[6])
            ADC_PARAMS["chirpStartIdxOffset"] = int(List[7])
            ADC_PARAMS["numOfBurst"] = int(List[8])
            ADC_PARAMS["numOfBurstLoops"] = int(List[9])
            ADC_PARAMS["subFramePeriodicity"] = int(List[10])

            ADC_PARAMS["numOfChirps"] = numOfChirps_buf[0]


        if 'lvdsStreamCfg' in line:
            lvdsCfg_headerEn_buf.append(int(List[2]))
            lvdsCfg_dataFmt_buf.append(int(List[3]))
            lvdsCfg_userBufEn_buf.append(int(List[4]))

        if 'CQSigImgMonitor' in line:
            SigImgNumSlices_buf.append(int(List[2]))

        if 'CQRxSatMonitor' in line:
            RxSatNumSlices_buf.append(int(List[4]))

    config.close()

    ####################################
    ######## Parser rxAnt config #######
    ####################################
    rxAntMask = CFG_PARAMS['rxAntMask']

    rxChanEn = []
    rxChanEn.append(rxAntMask & 1)
    rxChanEn.append((rxAntMask >> 1) & 1)
    rxChanEn.append((rxAntMask >> 2) & 1)
    rxChanEn.append((rxAntMask >> 3) & 1)
    # print(rxChanEn)

    txAntMask = CFG_PARAMS['txAntMask']
    print(rxAntMask,txAntMask)
    txChanEn = []
    txChanEn.append(txAntMask & 1)
    txChanEn.append((txAntMask >> 1) & 1)
    txChanEn.append((txAntMask >> 2) & 1)
    # print(txChanEn)

    numRxChan = 0
    chanIdx_buf = []
    for chanIdx in range(4):
        if rxChanEn[chanIdx] == 1:
            chanIdx_buf.append(chanIdx)
            numRxChan = numRxChan + 1
    CFG_PARAMS['numRxChan'] = numRxChan

    numTxChan = 0
    for chanIdx in range(3):
        if txChanEn[chanIdx] == 1:
            numTxChan = numTxChan + 1
    CFG_PARAMS['numTxChan'] = numTxChan
    ####################################
    ######## Parser lvds config ########
    ####################################
    Raw_file_numSubframes = 0
    Raw_file_subframeIdx_buf = []
    Raw_file_sessionFlag = ""

    ADC_file_numSubframes = 0
    ADC_file_subframeIdx_buf = []
    ADC_file_sessionFlag = ""

    CC9_file_numSubframes = 0
    CC9_file_subframeIdx_buf = []
    CC9_file_sessionFlag = ""

    # Based on the 1st subframe's lvdsStreamCfg CLI (headerEn, dataFmt and userBufEn)

    # if the 1st subframe has no header (headerEn = 0):
    # > in this case, HW session ADC only (dataFmt = 1) and no SW session (userBufEn = 0) is the only valid configuration combination.
    # > <prefix>_Raw_<x>.bin is generated to record HW session of the 1st subframe.
    # > in advanced subframe case, rest 3 subframes must have same lvdsStreamCfg as the 1st subframe, and record to <prefix>_Raw_<x>.bin as well.

    # if the 1st subframe has header (headerEn = 1) and HW session is ADC only (dataFmt = 1) or CP+ADC+CQ (dataFmt = 4):
    # > <prefix>_hdr_0ADC_<x>.bin is generated to record HW session of the 1st subframe. in advanced subframe case if any of rest 3 subfrmes has HW session, will be recorded to <prefix>_hdr_0ADC_<x>.bin as well.
    # > <prefix>_hdr_0CC9_<x>.bin will be generated to record SW session if any subframes has SW session (userBufEn = 1).

    # if the 1st subframe has header (headerEn = 1) and no HW session (dataFmt = 0):
    # > in this case, the 1st subframe must have SW session (userBufEn = 1)
    # > <prefix>_hdr_0ADC_<x>.bin is generated to record SW session of the 1st subframe. In advanced subframe case if any of rest 3 subframes has SW session, will be recorded to <prefix>_hdr_0ADC_<x>.bin as well.
    # > in advanced subframe case <prefix>_hdr_0CC9_<x>.bin will be generated to record HW session if any of rest 3 subframes has HW session (dataFmt = 1 or dataFmt = 4).

    CFG_PARAMS['datacard_dataLoggingMode'] = "multi"
    if lvdsCfg_headerEn_buf[0] == 0:
        CFG_PARAMS['datacard_dataLoggingMode'] = "raw"

    if lvdsCfg_headerEn_buf[0] == 0:
        if lvdsCfg_dataFmt_buf[0] == 1 and lvdsCfg_userBufEn_buf[0] == 0:
            if CFG_PARAMS['datacard_dataLoggingMode'] == "raw":
                # Raw file
                Raw_file_numSubframes = Raw_file_numSubframes + 1
                Raw_file_subframeIdx_buf.append(0)
                Raw_file_sessionFlag = "HW"
            elif CFG_PARAMS['datacard_dataLoggingMode'] == "multi":
                returen_value = TC_FAIL
                print("Error: no header can not be in multi mode!")
            else:
                returen_value = TC_FAIL
                print("Error: Undefined CFG_PARAMS['datacard_dataLoggingMode']!")
        else:
            returen_value = TC_FAIL
            print("Error: Invalid lvdsStreamCfg")
    elif lvdsCfg_headerEn_buf[0] == 1:
        if lvdsCfg_dataFmt_buf[0] == 1 or lvdsCfg_dataFmt_buf[0] == 4:  # 1:ADC 4:CP+ADC+CQ
            ADC_file_sessionFlag = "HW"
            CC9_file_sessionFlag = "SW"
            ADC_file_numSubframes = ADC_file_numSubframes + 1
            ADC_file_subframeIdx_buf.append(0)
            if lvdsCfg_userBufEn_buf[0] == 1:
                CC9_file_numSubframes = CC9_file_numSubframes + 1
                CC9_file_subframeIdx_buf.append(0)
        elif lvdsCfg_dataFmt_buf[0] == 0:  # no ADC no HW
            ADC_file_sessionFlag = "SW"
            CC9_file_sessionFlag = "HW"
            if lvdsCfg_userBufEn_buf[0] == 1:
                ADC_file_numSubframes = ADC_file_numSubframes + 1
                ADC_file_subframeIdx_buf.append(0)
            else:
                returen_value = TC_FAIL
                print("Error: subframe 0 has no HW and SW")
        else:
            print("subframe has a invalid dataFmt config")
    else:
        returen_value = TC_FAIL
        print("Error: Invalid lvdsCfg_headerEn_buf[0]")

    # Rest of 3 subframes if advanced subframe case
    for subframeIdx in range(1, CFG_PARAMS['numSubframes']):
        if lvdsCfg_dataFmt_buf[subframeIdx] == 1 or lvdsCfg_dataFmt_buf[subframeIdx] == 4:  # 1:ADC 4:CP+ADC+CQ
            if ADC_file_sessionFlag == "HW":
                ADC_file_numSubframes = ADC_file_numSubframes + 1
                ADC_file_subframeIdx_buf.append(subframeIdx)
            if CC9_file_sessionFlag == "HW":
                CC9_file_numSubframes = CC9_file_numSubframes + 1
                CC9_file_subframeIdx_buf.append(subframeIdx)
        if lvdsCfg_userBufEn_buf[subframeIdx] == 1:
            if ADC_file_sessionFlag == "SW":
                ADC_file_numSubframes = ADC_file_numSubframes + 1
                ADC_file_subframeIdx_buf.append(subframeIdx)
            if CC9_file_sessionFlag == "SW":
                CC9_file_numSubframes = CC9_file_numSubframes + 1
                CC9_file_subframeIdx_buf.append(subframeIdx)

    ADC_PARAMS['rx'] = CFG_PARAMS['numRxChan']
    ADC_PARAMS['tx'] = CFG_PARAMS['numTxChan']
    ADC_PARAMS['IQ'] = 2
    ADC_PARAMS['bytes'] = 2

    '''
    For HW data, the inter-chirp duration should be sufficient to stream out the desired amount of data. 
    For example, if the HW data-format is ADC and HSI header is enabled, then the total amount of data 
    generated per chirp is:(numAdcSamples * numRxChannels * 4 (size of complex sample) + 
    52 [sizeof(HSIDataCardHeader_t) + sizeof(HSISDKHeader_t)] ) 
    rounded up to multiples of 256 [=sizeof(HSIHeader_t)] bytes.

    The chirp time Tc in us = idle time + ramp end time in the profile configuration. 
    For n-lane LVDS with each lane at a maximum of B Mbps,
    maximum number of bytes that can be send per chirp = Tc * n * B / 8 
    which should be greater than the total amount of data generated per chirp i.e
    Tc * n * B / 8 >= round-up(numAdcSamples * numRxChannels * 4 + 52, 256).
    E.g if n = 2, B = 600 Mbps, idle time = 7 us, ramp end time = 44 us, numAdcSamples = 512, numRxChannels = 4, 
    then 7650 >= 8448 is violated so this configuration will not work. 
    If the idle-time is doubled in the above example, then we have 8700 > 8448, so this configuration will work.

    For SW data, the number of bytes to transmit each sub-frame/frame is:
    52 [sizeof(HSIDataCardHeader_t) + sizeof(HSISDKHeader_t)] + sizeof(MmwDemo_LVDSUserDataHeader_t) [=8] +
    number of detected objects
    (Nd) * { sizeof(DPIF_PointCloudCartesian_t) [=16] + sizeof(DPIF_PointCloudSideInfo_t) [=4] }
    rounded up to multiples of 256 [=sizeof(HSIHeader_t)] bytes.
    or X = round-up(60 + Nd * 20, 256). So the time to transmit this data will be X * 8 / (n*B) us. 
    The maximum number of objects (Ndmax) that can be detected is defined in the DPC (DPC_OBJDET_MAX_NUM_OBJECTS). 
    So if Ndmax = 500, then time to transmit SW data is 68 us. 
    Because we parallelize this transmission with the much slower UART transmission, 
    and because UART transmission is also sending at least the same amount of information as the LVDS, 
    the LVDS transmission time will not add any burdens on the processing budget beyond the overhead of 
    reconfiguring and activating the CBUFF session (this overhead is likely bigger than the time to transmit).

    The total amount of data to be transmitted in a HW or SW packet must be greater than the minimum 
    required by CBUFF, which is 64 bytes or 32 CBUFF Units 
    (this is the definition CBUFF_MIN_TRANSFER_SIZE_CBUFF_UNITS in the CBUFF driver implementation). 
    If this threshold condition is violated, 
    the CBUFF driver will return an error during configuration 
    and the demo will generate a fatal exception as a result. 
    When HSI header is enabled, the total transfer size is ensured to be at least 256 bytes, 
    which satisfies the minimum. 
    If HSI header is disabled, for the HW session, this means that numAdcSamples * numRxChannels * 4 >= 64. 
    Although mmwavelink allows minimum number of ADC samples to be 2, the demo is supported for numAdcSamples >= 64. 
    So HSI header is not required to be enabled for HW only case. 
    But if SW session is enabled, without the HSI header, the bytes in each packet will be 8 + Nd * 20. 
    So for frames/sub-frames where Nd < 3, the demo will generate exception. 
    Therefore HSI header must be enabled if SW is enabled, this is checked in the CLI command validation.
    '''
    LVDSDataSizePerChirp = numAdcSamples_buf[0] * CFG_PARAMS['numRxChan'] * ADC_PARAMS['IQ'] * ADC_PARAMS[
        'bytes'] + 52
    LVDSDataSizePerChirp = math.ceil(LVDSDataSizePerChirp / 256) * 256
    nlane = 2
    B = 600
    maxSendBytesPerChirp = (idleTime + rampEndTime) * nlane * B / 8
    # print(ADC_PARAMS)

    # ADC collection Time
    ADC_PARAMS["adcCollectionTime"] = ADC_PARAMS["samples"] / ADC_PARAMS["sample_rate"] * 1e3
    #
    ADC_PARAMS["lightSpeed"] = 3e8  # 299792458 # m/s
    ADC_PARAMS["wavelength"] = ADC_PARAMS["lightSpeed"] / (ADC_PARAMS["startFreq"] * 1e9)  # m

    ADC_PARAMS["maxRange"] = (ADC_PARAMS["lightSpeed"] * 0.8 * ADC_PARAMS['sample_rate']) / (
            2 * ADC_PARAMS["freq_slope"] * 1e9)

    # Sweep BW (useful) MHz
    ADC_PARAMS["bandWidth"] = ADC_PARAMS["freq_slope"] * ADC_PARAMS["rampEndTime"]

    ADC_PARAMS["band_width_use"] = ((ADC_PARAMS["freq_slope"] * 1e6 *
                                     ADC_PARAMS["samples"])) / (1e3 * ADC_PARAMS["sample_rate"])

    ADC_PARAMS["rangeResolution"] = ADC_PARAMS["lightSpeed"] / (2 * 1e6 * ADC_PARAMS["band_width_use"])

    ADC_PARAMS["maxVelocityExtended"] = ADC_PARAMS["wavelength"] / (
                4 * (ADC_PARAMS["idleTime"] + ADC_PARAMS["rampEndTime"]) * 1e-6)
    ADC_PARAMS["maxVelocity"] = ADC_PARAMS["wavelength"] / (4 * ADC_PARAMS["adcCollectionTime"] * 1e-6)

    ADC_PARAMS["frameTimeaTotal"] = (ADC_PARAMS["idleTime"] + ADC_PARAMS["rampEndTime"]) \
                                    * 1e-6 * ADC_PARAMS["chirps"] * ADC_PARAMS["tx"]

    ADC_PARAMS["frameTimeaActive"] = ADC_PARAMS["adcCollectionTime"] * 1e-6 * ADC_PARAMS["chirps"] * ADC_PARAMS["tx"]

    if "numOfsubFrames" in ADC_PARAMS:
        ADC_PARAMS["dopplerResolution"] = ADC_PARAMS["lightSpeed"]/(ADC_PARAMS["startFreq"] * 1e9 * 2
                                        * ADC_PARAMS["numOfChirps"] * ADC_PARAMS["chirps"] *
                                        (ADC_PARAMS["idleTime"] + ADC_PARAMS["rampEndTime"]) * 1e-6)
    else:
        ADC_PARAMS["dopplerResolution"] = ADC_PARAMS["wavelength"] / (2*ADC_PARAMS["frameTimeaTotal"])

    return (LVDSDataSizePerChirp, maxSendBytesPerChirp, ADC_PARAMS, CFG_PARAMS)


def parser_raw_adc_data(raw_bin_file, config_file_name, isMIMO=False, isBeamforming=False):
    """ parser raw adc .bin data
    Args:
        raw_bin_file: input raw adc bin data file
        config_file_name: config file

    Returns: [Frames, Chirps, TX, RX, Samples]
             or [Frames, Chirps, VirtualAnts, Samples]

    """
    _, _, ADC_PARAMS, _ = read_config(config_file_name)

    adc_data = np.fromfile(raw_bin_file, dtype=np.int16)
    adc_data = np.reshape(adc_data, (-1, ADC_PARAMS['chirps'], ADC_PARAMS['tx'],
                                     ADC_PARAMS['rx'], ADC_PARAMS['samples'] // 2, ADC_PARAMS['IQ'], 2))

    adc_data = np.transpose(adc_data, (0, 1, 2, 3, 4, 6, 5))
    adc_data = np.reshape(adc_data, (-1, ADC_PARAMS['chirps'], ADC_PARAMS['tx'],
                                     ADC_PARAMS['rx'], ADC_PARAMS['samples'], ADC_PARAMS['IQ']))

    # [Frames, Chirps, TX, RX, Samples]
    adc_data = (1j * adc_data[:, :, :, :, :, 0] + adc_data[:, :, :, :, :, 1]).astype(np.complex64)

    if isMIMO:
        # [Frames * Chirps * VirtualAnts * Samples]
        adc_data = np.reshape(adc_data[:, :, 0:ADC_PARAMS['tx'], :, :],
                              (-1, ADC_PARAMS['chirps'], ADC_PARAMS['tx'] * ADC_PARAMS['rx'], ADC_PARAMS['samples']))

    if isBeamforming:
        adc_data = np.mean(adc_data, axis=2)
    return adc_data
