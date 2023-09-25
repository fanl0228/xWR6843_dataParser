""" 可解析的参数，只能解析非级联的参数
    parameters["profileId"]
    parameters["startFreq"]
    parameters["idleTime"]
    parameters["rampEndTime"]
    parameters["freqSlopeConst"]
    parameters["numAdcSamples"]
    parameters["digOutSampleRate"]
    parameters["rxGain"]
    parameters["chirpStartIdx"]
    parameters["chirpEndIdx"]
    parameters["numChirps"]
    parameters["numFrames"]
    parameters["framePeriodicity"]
    parameters["numTxUsed"]
    parameters["numRx"]
    parameters["numADCBits"]
    parameters["bytes"]
    parameters["adcOutputFmt"]

    parameters["numRangeBins"]
    parameters["rangeResolution"]
    parameters["rangeIdxToMeters"]

    parameters["numDopplerBins"]
    parameters["velocityResolution"]
    parameters["maxRange"]
    parameters["maxVelocity"]
"""

# Function to parse the data inside the configuration file
import os


def parse_config_file(config_file_name):
    parameters = {}  # Initialize an empty dictionary to store the configuration parameters

    # Read the configuration file and send it to the board
    config = [line.rstrip('\r\n') for line in open(config_file_name)]
    for i in config:
        # Split the line
        splitWords = i.split(" ")

        if "%" in splitWords[0]:
            continue
        # Get the information about the profile configuration
        elif "profileCfg" in splitWords[0]:
            parameters["profileId"] = int(float(splitWords[1]))
            parameters["startFreq"] = int(float(splitWords[2]))
            parameters["idleTime"] = float(splitWords[3])
            parameters["rampStartTime"] = float(splitWords[4])
            parameters["rampEndTime"] = float(splitWords[5])
            parameters["txOutPower"] = float(splitWords[6])
            parameters["txPhaseShifter"] = float(splitWords[7])
            parameters["freqSlopeConst"] = float(splitWords[8])
            parameters["txStartTime"] = float(splitWords[9])
            parameters["numAdcSamples"] = int(splitWords[10])
            parameters["digOutSampleRate"] = float(splitWords[11])
            parameters["hpfCornerFreq1"] = float(splitWords[12])
            parameters["hpfCornerFreq2"] = float(splitWords[13])
            parameters["rxGain"] = int(splitWords[14])
            numAdcSamplesRoundTo2 = 1
            while parameters["numAdcSamples"] > numAdcSamplesRoundTo2:
                numAdcSamplesRoundTo2 = numAdcSamplesRoundTo2 * 2

        # Get the information about the frame configuration
        elif "frameCfg" in splitWords[0]:
            parameters["chirpStartIdx"] = int(splitWords[1])
            parameters["chirpEndIdx"] = int(splitWords[2])
            parameters["numChirps"] = int(splitWords[3])
            parameters["numFrames"] = int(splitWords[4])
            parameters["framePeriodicity"] = float(splitWords[5])
            parameters["numTxUsed"] = parameters["chirpEndIdx"] - parameters["chirpStartIdx"] + 1

        elif "advFrameCfg" in splitWords[0]:
            parameters["numOfsubFrames"] = int(splitWords[1])
        elif "subFrameCfg" in splitWords[0]:
            parameters["subFrameNum"] = int(splitWords[1])
            parameters["forceProfileIdx"] = int(splitWords[2])
            parameters["chirpStartIdx"] = int(splitWords[3])
            parameters["numOfChirps"] = int(splitWords[4])
            parameters["numChirps"] = int(splitWords[5])
            parameters["burstPeriodicity"] = int(splitWords[6])
            parameters["chirpStartIdxOffset"] = int(splitWords[7])
            parameters["numOfBurst"] = int(splitWords[8])
            parameters["numOfBurstLoops"] = int(splitWords[9])
            parameters["framePeriodicity"] = int(splitWords[10])
            parameters["numTxUsed"] = 1


        # Get the information of channel
        elif "channelCfg" in splitWords[0]:
            if 15 == int(splitWords[1]):
                parameters["numRx"] = 4
            elif 7 == int(splitWords[1]):
                parameters["numRx"] = 3
            elif 3 == int(splitWords[1]):
                parameters["numRx"] = 2
            elif 8 == int(splitWords[1]) or 1 == int(splitWords[1]):
                parameters["numRx"] = 1
            else:
                print("ERROR... Rx Channel failed...\n")


        elif "adcCfg" in splitWords[0]:
            if 2 == int(splitWords[1]):
                parameters["numADCBits"] = 16
                parameters["bytes"] = 2
            elif 1 == int(splitWords[1]):
                parameters["numADCBits"] = 14
                parameters["bytes"] = 2
            elif 0 == int(splitWords[1]):
                parameters["numADCBits"] = 12
                parameters["bytes"] = 2
            else:
                print("ERROR... adcCfg numADCBits failed...")

            if 0 == int(splitWords[2]):
                parameters["adcOutputFmt"] = 1 # real
            elif 1 == int(splitWords[2]):
                parameters["adcOutputFmt"] = 2 # complex 1x
            elif 2 == int(splitWords[2]):
                parameters["adcOutputFmt"] = 4 # complex 2x
            else:
                print("ERROR... adcCfg adcOutputFmt failed...")

    # ADC collection Time
    parameters["adcCollectionTime"] = parameters["numAdcSamples"] / parameters["digOutSampleRate"] * 1e3

    # Combine the read data to obtain the configuration parameters
    if "numOfsubFrames" in parameters:
        numChirpsPerFrame =parameters["numOfChirps"] * parameters["numChirps"]
        parameters["numDopplerBins"] = numChirpsPerFrame
    else:
        numChirpsPerFrame = (parameters["chirpEndIdx"] - parameters["chirpStartIdx"] + 1) * parameters["numChirps"]
        parameters["numDopplerBins"] = numChirpsPerFrame / parameters["numRx"]

    parameters["numRangeBins"] = numAdcSamplesRoundTo2

    parameters["lightSpeed"] = 3e8 #299792458 # m/s

    # Fs = 80% * digOutSampleRate
    # Max Distance (80%) m

    parameters["wavelength"] = parameters["lightSpeed"] / (parameters["startFreq"] * 1e9)  # m

    parameters["maxRange"] = (parameters["lightSpeed"] * 0.8 * parameters["digOutSampleRate"]) / (
                                2 * parameters["freqSlopeConst"] * 1e9)

    # Sweep BW (useful) MHz
    parameters["bandWidth"] = parameters["freqSlopeConst"] * parameters["rampEndTime"]

    parameters["band_width_use"] = ((parameters["freqSlopeConst"] * 1e6 *
                                    parameters["numAdcSamples"])) / (1e3 * parameters["digOutSampleRate"])

    parameters["rangeResolution"] = parameters["lightSpeed"] / (2 * 1e6 * parameters["band_width_use"])

    parameters["maxVelocityExtended"] = parameters["wavelength"] / (4 * (parameters["idleTime"] + parameters["rampEndTime"]) * 1e-6)
    parameters["maxVelocity"] = parameters["wavelength"] / (4 * parameters["adcCollectionTime"] * 1e-6)

    parameters["frameTimeaTotal"] = (parameters["idleTime"] + parameters["rampEndTime"]) \
                                    * 1e-6 * parameters["numChirps"] * parameters["numTxUsed"]

    parameters["frameTimeaActive"] = parameters["adcCollectionTime"] * 1e-6 * parameters["numChirps"] * parameters["numTxUsed"]

    if "numOfsubFrames" in parameters:
        parameters["velocityResolution"] = parameters["lightSpeed"]/(parameters["startFreq"] * 1e9 * 2
                                        * parameters["numOfChirps"] * parameters["numChirps"] *
                                        (parameters["idleTime"] + parameters["rampEndTime"]) * 1e-6)
    else:
        parameters["velocityResolution"] = parameters["wavelength"] / (2*parameters["frameTimeaTotal"])

    # 参数验证
    # assert parameters["rampEndTime"] > parameters["adcCollectionTime"]
    # assert parameters["bandWidth"] > 4000
    # assert 1e3*parameters["frameTimeaTotal"] > parameters["framePeriodicity"]

    print("% ====================================================================")
    print("% Carrier frequency     GHz                        {}".format(parameters["startFreq"]))
    print("% % Ramp Slope    MHz/us                           {}".format(parameters["freqSlopeConst"]))
    print("% Num ADC Samples                                  {}".format(parameters["numAdcSamples"]))
    print("% ADC Sampling Rate ksps                           {}".format(parameters["digOutSampleRate"]))
    print("% ADC Collection Time   us                         {}".format(parameters["adcCollectionTime"]))
    print("% Extra ramp time required (start time) us         {}".format(parameters["rampStartTime"]))
    print("% Chirp duration (end time) us                     {}".format(parameters["rampEndTime"]))
    print("% Chirp time (end time - start time)    us         {}".format(parameters["rampEndTime"] - parameters["rampStartTime"]))
    print("% Sweep BW (useful) MHz                            {}".format(parameters["band_width_use"]))
    print("% Total BW  MHz                                    {}".format(parameters["bandWidth"]))
    print("% Max beat freq (80% of ADC sampling rate)  KHz    {}".format(0.8*parameters["digOutSampleRate"]))
    print("% Max distance (80%)    m                          {}".format(parameters["maxRange"]))
    print("% Range resolution  m                              {}".format(parameters["rangeResolution"]))
    print("% Range resolution (meter per 1D-FFT bin)   m/bin  {}".format(parameters["rangeResolution"]))
    print("% Inter-chirp duration  us                         {}".format(parameters["idleTime"]))
    print("% Number of chirp intervals in frame    -          {}".format(parameters["numChirps"] * parameters["numTxUsed"]))
    print("% Number of TX (TDM MIMO)                          {}".format(parameters["numTxUsed"]))
    print("% Number of RX channels -                          {}".format(parameters["numRx"]))
    print("% Frame time (total)    ms                         {}".format(1e3*parameters["frameTimeaTotal"]))
    print("% Frame time (active)   ms                         {}".format(1e3*parameters["frameTimeaActive"]))
    print("% Range FFT size    -                              {}".format(parameters["numAdcSamples"]))
    print("% Doppler FFT size  -                              {}".format(parameters["numChirps"]))
    print("% Velocity resolution   m/s                        {}".format(parameters["velocityResolution"]))
    print("% Velocity resolution (m/s per 2D-FFT bin) m/s/bin {}".format(parameters["velocityResolution"]))
    print("% Velocity Maximum  m/s                            {}".format(parameters["maxVelocityExtended"]/2))
    print("% Extended Maximum Velocity m/s                    {}".format(parameters["maxVelocityExtended"]))
    print("% ====================================================================")
    return parameters


if __name__ == "__main__":
    cfg_file = os.path.join(os.getcwd(), "../Win_pyFPGA/Config_files/Demo_MIMO_raw_ip181.cfg")
    parameters = parse_config_file(cfg_file)
