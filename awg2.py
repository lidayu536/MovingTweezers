from pyspcm import *
from spcm_tools import *
import sys
import numpy as np
from tweezer_synthesis import synthesis, normalize, convert_to_int, convert_to_int2

class AWG2():
    def __init__(self, address="/dev/spcm0"):
        self.address = address.encode()
        self.hCard = None
        self.buffer_size = 8192#2^13
        self.sample_rate = 1000
        self.amplitude = 1000
        self.llMemSamples = int64 (KILO_B(self.buffer_size))#2^23
        self.lBytesPerSample = int32 (0)
        self.lSetChannels = int32 (0)
        self.qwBufferSize = uint64 (self.llMemSamples.value * self.lBytesPerSample.value * self.lSetChannels.value)

    def open(self):
        self.hCard = spcm_hOpen (create_string_buffer (self.address))
        if self.hCard == None:
            sys.stdout.write("no card found...\n")
            exit (1)
        lCardType = int32 (0)
        spcm_dwGetParam_i32 (self.hCard, SPC_PCITYP, byref (lCardType))
        lSerialNumber = int32 (0)
        spcm_dwGetParam_i32 (self.hCard, SPC_PCISERIALNO, byref (lSerialNumber))
        lFncType = int32 (0)
        spcm_dwGetParam_i32 (self.hCard, SPC_FNCTYPE, byref (lFncType))
        sCardName = szTypeToName (lCardType.value)
        if lFncType.value == SPCM_TYPE_AO:
            sys.stdout.write("Found: {0} sn {1:05d}\n".format(sCardName,lSerialNumber.value))
        else:
            sys.stdout.write("This is an example for D/A cards.\nCard: {0} sn {1:05d} not supported by example\n".format(sCardName,lSerialNumber.value))
            spcm_vClose (self.hCard)
            exit (1)

    def set_sample_rate(self, sample_rate):
            self.sample_rate = sample_rate

    def set_buffer_size(self, buffer_size):
        self.buffer_size = buffer_size
        self.llMemSamples = int64 (KILO_B(self.buffer_size))

    def config(self):
        spcm_dwSetParam_i64 (self.hCard, SPC_SAMPLERATE, MEGA(self.sample_rate))
        spcm_dwSetParam_i32 (self.hCard, SPC_CLOCKOUT,   0)
        qwChEnable = uint64 (1+2)

        llLoops = int64 (0) # loop continuously

        spcm_dwSetParam_i32 (self.hCard, SPC_CARDMODE,    SPC_REP_STD_CONTINUOUS)
        spcm_dwSetParam_i64 (self.hCard, SPC_CHENABLE,    qwChEnable)
        spcm_dwSetParam_i64 (self.hCard, SPC_MEMSIZE,     self.llMemSamples)
        spcm_dwSetParam_i64 (self.hCard, SPC_LOOPS,       llLoops)
        spcm_dwSetParam_i64 (self.hCard, SPC_ENABLEOUT0,  1)
        spcm_dwSetParam_i64 (self.hCard, SPC_ENABLEOUT1,  1)

        spcm_dwGetParam_i32 (self.hCard, SPC_CHCOUNT,     byref (self.lSetChannels))
        
        spcm_dwGetParam_i32 (self.hCard, SPC_MIINST_BYTESPERSAMPLE,  byref (self.lBytesPerSample))
        # setup the trigger mode
        # (SW trigger, no output)

        spcm_dwSetParam_i32 (self.hCard, SPC_TRIG_ORMASK,      SPC_TMASK_SOFTWARE)
        spcm_dwSetParam_i32 (self.hCard, SPC_TRIG_ANDMASK,     0)
        spcm_dwSetParam_i32 (self.hCard, SPC_TRIG_CH_ORMASK0,  0)
        spcm_dwSetParam_i32 (self.hCard, SPC_TRIG_CH_ORMASK1,  0)
        spcm_dwSetParam_i32 (self.hCard, SPC_TRIG_CH_ANDMASK0, 0)
        spcm_dwSetParam_i32 (self.hCard, SPC_TRIG_CH_ANDMASK1, 0)
        spcm_dwSetParam_i32 (self.hCard, SPC_TRIGGEROUT,       0)
###try
        if spcm_dwSetParam_i32 (self.hCard, SPCM_X0_AVAILMODES)|SPCM_XMODE_ASYNCOUT!=0:
            spcm_dwSetParam_i32 (self.hCard, SPCM_X0_MODE,SPCM_XMODE_ASYNCOUT)
        if spcm_dwSetParam_i32 (self.hCard, SPCM_X1_AVAILMODES)|SPCM_XMODE_ASYNCOUT!=0:
            spcm_dwSetParam_i32 (self.hCard, SPCM_X1_MODE,SPCM_XMODE_ASYNCOUT)
###
        lChannel = int32 (0)
        spcm_dwSetParam_i32 (self.hCard, SPC_AMP0 + lChannel.value * (SPC_AMP1 - SPC_AMP0), int32 (self.amplitude))
        self.qwBufferSize = uint64 (self.llMemSamples.value * self.lBytesPerSample.value * self.lSetChannels.value)

    def arbitrary_synthesis(self, waveform1, waveform2, time_out):
        if len(waveform1) != self.llMemSamples.value or len(waveform2) != self.llMemSamples.value:
            raise ValueError
        a = convert_to_int2(normalize(waveform1))
        if not a.flags['C_CONTIGUOUS']:
            a=np.ascontiguousarray(a, dtype=a.dtype)
        b = convert_to_int2(normalize(waveform2))
        if not b.flags['C_CONTIGUOUS']:
            b=np.ascontiguousarray(b, dtype=b.dtype)
        ab=a+b*(2**16)
        pnBuffer = ab.ctypes.data_as(ptr32)

        sys.stdout.write("Starting the DMA transfer and waiting until data is in board memory\n")
        spcm_dwDefTransfer_i64 (self.hCard, SPCM_BUF_DATA, SPCM_DIR_PCTOCARD, int32 (0), pnBuffer, uint64 (0), self.qwBufferSize)
        spcm_dwSetParam_i32 (self.hCard, SPC_M2CMD, M2CMD_DATA_STARTDMA | M2CMD_DATA_WAITDMA)
        sys.stdout.write("... data has been transferred to board memory\n")
        spcm_dwSetParam_i32 (self.hCard, SPC_TIMEOUT, time_out)
        sys.stdout.write("\nStarting the card and waiting for ready interrupt\n(continuous and single restart will have timeout)\n")
        dwError = spcm_dwSetParam_i32 (self.hCard, SPC_M2CMD, M2CMD_CARD_START | M2CMD_CARD_ENABLETRIGGER | M2CMD_CARD_WAITREADY)
        if dwError == ERR_TIMEOUT:
            spcm_dwSetParam_i32 (self.hCard, SPC_M2CMD, M2CMD_CARD_STOP)

    def close(self):
        spcm_vClose (self.hCard)



            
