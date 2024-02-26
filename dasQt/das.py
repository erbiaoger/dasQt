"""
    * @file: das.py
    * @version: v1.0.0
    * @author: Zhiyu Zhang
    * @desc: 
    * @date: 2023-07-25 10:09:34
    * @Email: erbiaoger@gmail.com
    * @url: erbiaoger.site

"""

import os
import h5py
import numpy as np
# import numba as nb
from tqdm import tqdm
import matplotlib.pyplot as plt
from scipy import signal
import pathlib

from dasQt.CrossCorrelation import DAS_module
from dasQt.filter.filter import butterworth
from dasQt.norm_trace import normalize_data
from dasQt.CarClass.Radon import Radon
from dasQt.norm_trace1 import norm_trace
from dasQt.filter.bp_filter import bp_filter
from dasQt.CarClass.curves_class import pickPoints, autoSeparation, deleteSmallClass, showClass, getVelocity, classCar
from dasQt.Logging.logPy3 import HandleLog
from dasQt.Logging.logPy import Logger

#import threading

class DAS():
    def __init__(self):
        self.data = None
        self.nt = None
        self.nx = None
        self.dt = None
        self.dx = None
        self.display_nt = 10000
        self.speed = 0.25 # 1x 2x 3x 0.5x 0.25x
        self.startX = 0
        self.fIndex = 0
        
        # Car Class
        self.threshold = 0.01
        self.skip_Nch = 2
        self.skip_Nt = 1000

        self.maxMode = 10
        self.minCarNum = 15
        self.to = 0.01
        self.mode = 'max'
        
        self.dispersion_parse = {}
        self.indexClick = 0
        self.radon_parse = {}
        
        # self.logger = log_init(__file__[:-3])
        # self.logger = Logger(fname=__file__[:-3], path=os.getcwd()).logger

        self.logger = HandleLog(os.path.split(__file__)[-1].split(".")[0], path=os.getcwd())

        pass

    def readData(self, filename='./Data/SR_2023-07-20_09-09-38_UTC.h5'):
        self.fname = filename
        fileType = os.path.splitext(filename)[-1]
        if fileType == '.h5':
            # with h5py.File(filename, 'r') as f:
            #     StrainRate = f['/fa1-22070070/Source1/Zone1/StrainRate'][:]
            #     spacing = f['/fa1-22070070/Source1/Zone1'].attrs['Spacing']

            with h5py.File(filename, 'r') as f:
                for a in f:
                    StrainRate = f[f'/{a}/Source1/Zone1/StrainRate'][:]
                    spacing = f[f'/{a}/Source1/Zone1'].attrs['Spacing']


            #self.data = StrainRate.reshape(-1, StrainRate.shape[-1])
            self.dx = spacing[0]
            self.dt = spacing[1] * 1e-3
            nb, nt, nx = StrainRate.shape

            self.data = StrainRate[:, nt//2:, :].reshape(-1, nx)

            self.nt, self.nx = self.data.shape

            self.pre_data = self.data.copy()
            self.vmin = np.nanmin(self.data)
            self.vmax = np.nanmax(self.data)
            
            filepath = pathlib.Path(filename)
            self.logger.info(f"{filepath.name} read done!")
            self.logger.debug(f"nt: {self.nt}, nx: {self.nx}, dt: {self.dt}, dx: {self.dx}")

        elif fileType == '.dat':
            #filename = 'guangu/2023-07-20-18-40-58-out.dat'
            with open(filename, 'rb') as fid:
                D = np.fromfile(fid, dtype=np.float32)

            fs = D[10]
            self.dt = 1 / fs
            self.dx = D[13]
            self.nx = int(D[16])
            self.nt = int(fs * D[17])

            self.data = D[64:].reshape((self.nx, self.nt), order='F').T  # 使用Fortran顺序进行数据的reshape

            self.pre_data = self.data.copy()
            self.vmin = np.nanmin(self.data)
            self.vmax = np.nanmax(self.data)
            
            filepath = pathlib.Path(filename)
            self.logger.info(f"{filepath.name} read done!")
            self.logger.debug(f"nt: {self.nt}, nx: {self.nx}, dt: {self.dt}, dx: {self.dx}")
        else:
            self.logger.error("File Type Error!")
            raise ValueError("File Type Error!")



        self.radon_data = self.data.copy()



    def openFolder(self, foldername='./das/'):
        self.foldername = foldername
        self.fnames = sorted(os.listdir(foldername))
        
        self.logger.info(f"open {foldername} done!")
        
        return self.fnames
    
    def getFileID(self, fname):
        for index, value in enumerate(self.fnames):
            if value == fname:
                self.fIndex = index
                break

        self.logger.debug(f"{fname} is the {self.fIndex}s file")
        
        #TODO
    
    def readNextData(self):
        if self.fnames:
            self.fIndex += 1
            try:
                self.fname = self.fnames[self.fIndex]

                self.logger.debug(f"next file is {self.fname}")
                self.readData(os.path.join(self.foldername, self.fname))
            except IndexError:
                self.logger.error("Index Error!")
                raise IndexError("Index Error!")


    def bandpassData(self, fmin, fmax):
        """
        Bandpass filter the data
        """
        self.data = butterworth(self.data, cutoff=(fmin, fmax), fs=1/self.dt, order=6, btype='bandpass', axis=0)
        self.logger.info(f"Bandpass Done!")
        
    def rawData(self):
        self.data = self.pre_data.copy()

    def downSampling(self, intNumDownSampling=2):
        self.data = self.data[::intNumDownSampling, :]
        self.dt = self.dt * intNumDownSampling

    def cutData(self, Xmin, Xmax):
        """
        Cut the data
        """
        self.logger(f"Channel min: {Xmin_Num}, Cmax: {Xmax_Num}, Xmin: {float(Xmin)}, Xmax: {float(Xmax)}")
        
        if Xmin != 'start' and Xmax != 'end':
            X = np.arange(self.nx) * self.dx
            Xmin_Num = np.abs(float(Xmin) - X).argmin()
            Xmax_Num = np.abs(float(Xmax) - X).argmin()
            self.data[:, Xmin_Num:Xmax_Num] = np.nan
            
        elif Xmin == 'start':
            X = np.arange(self.nx) * self.dx
            Xmin_Num = 0
            Xmax_Num = np.abs(float(Xmax) - X).argmin()
            self.data[:, Xmin_Num:Xmax_Num] = np.nan
            
        elif Xmax == 'end':
            X = np.arange(self.nx) * self.dx
            Xmin_Num = np.abs(float(Xmin) - X).argmin()
            Xmax_Num = self.nx
            self.data[:, Xmin_Num:Xmax_Num] = np.nan
        
        self.logger.info("Cut Data Done!")


    def imshowData(self, ax, indexTime=0, scale=1):
        dt = self.dt
        self.logger.debug(f"dt: {dt}")
        dx = self.dx
        display_nt = self.display_nt
        nt = self.nt
        nx = self.nx
        scale = 0.1 / scale 
        data = self.data[int(indexTime): int(indexTime+display_nt)]

        ax.imshow(data, aspect='auto', cmap='rainbow',
                    origin='lower', extent=[0, nx*dx, indexTime*dt, (indexTime+display_nt)*dt],
                    vmin=self.vmin*scale, vmax=self.vmax*scale)
        ax.set_xlabel('distance [m]')
        ax.set_ylabel('time [s]')
        fname = os.path.basename(self.fname).split('.')[0]
        ax.set_title(fname)
        
        # self.logger.debug("ImShow Data Done!")

        return ax
    
    def imshowCarClass(self, ax, indexTime=0, scale=1, 
                       skip_Nch=2, skip_Nt=1000, threshold=0.1, model='min',
                       maxMode=10, minCarNum=15, to=0.01,):
        dt = self.dt
        dx = self.dx
        display_nt = self.display_nt
        Nt = self.nt
        Nch = self.nx
        scale = 0.1 / scale 
        data = self.data

        x = np.linspace(0, Nch * dx, Nch)        # x-axis
        t = np.linspace(0, Nt * dt, Nt)          # t-axis

        # pick points
        skip_Nch    = self.skip_Nch
        skip_Nt     = self.skip_Nt
        threshold   = self.threshold
        mode = self.mode
        
        curves = pickPoints(data, Nch, Nt, skip_Nch=skip_Nch, skip_Nt=skip_Nt, threshold=threshold, model=mode)
        if curves is None:
            ax = self.imshowData(ax, indexTime=indexTime, scale=scale)
            return ax
        
        
        # auto separation
        maxMode     = self.maxMode          # maxMode = 10, 10 classes
        minCarNum   = self.minCarNum        # minCarNum = 15, min car number in one class
        to          = self.to               # to = 0.01, threshold of distance
        
        curves_km = autoSeparation(curves, to=to, maxMode=maxMode)
        id_list = np.unique(curves_km[...,-1])
        class_num = len(id_list)

        curves_km = deleteSmallClass(curves_km, class_num, minCarNum=minCarNum)

        id_list = np.unique(curves_km[...,-1])
        class_num = len(id_list)
        
        # get velocity
        velocities, id_list_a = getVelocity(curves_km, x, t, id_list)
        
        # class car
        line = self.line
        id_list_b = classCar(curves_km, id_list, scale=line)

        self.logger.info(f"velocities: {velocities}")
        
        ax = showClass(data, curves_km, id_list_b, t, x, ax, 
                       s='b)', title="Only Car", model='vel', velocities=velocities, 
                       vmin=self.vmin*scale, vmax=self.vmax*scale)

        self.logger.info("ImShow CarClass Done!")

        return ax

    def imshowDispersion(self, fig, ax, dispersion_parse=None, indexTime=0, scale=1):
        # scale = 1. / scale
        scale = 0.5
        
        data_liner = self.caculateDispersion(dispersion_parse=dispersion_parse, scale=scale)
        # data_liner = data_liner / data_liner.std()

        if self.indexClick == 0:
            self.pre_dispersion_data = data_liner
            self.indexClick += 1
        else:
            if self.pre_dispersion_data.shape != data_liner.shape:
                self.pre_dispersion_data = data_liner
                self.logger.debug(f"dp para changed, last index is {self.indexClick}, now index is 0")
                self.indexClick = 0
                
            else:
                self.pre_dispersion_data = (self.pre_dispersion_data*self.indexClick + data_liner) / (self.indexClick+1)
                self.indexClick += 1
                self.logger.debug(f"now index is {self.indexClick}")
        
        cha1 = dispersion_parse['cha1']
        cha2 = dispersion_parse['cha2']
        nt = self.pre_dispersion_data.shape[0]
        vmin = np.nanmin(self.pre_dispersion_data)
        vmax = np.nanmax(self.pre_dispersion_data)

        ax0 = ax.imshow(self.pre_dispersion_data, cmap='RdBu_r', aspect='auto', 
                  origin='lower', extent=[cha1*self.dx, cha2*self.dx, -nt//2*self.dt, nt//2*self.dt])
        
        # ax.set_xlabel('distance [m]')
        # ax.set_ylabel('time [s]')
        ax.set_title('Dispersion')
        # fig.colorbar(ax0, ax=ax)
        
        self.logger.info("ImShow Dispersion Done!")



        return ax


    def imshowRadon(self, ax, indexTime=0, scale=1):
        # scale = 1. / scale
        data = self.radon_data
        nt, nx = data.shape
        
        fmin = self.radon_parse['fmin']
        fmin1 = self.radon_parse['fmin1']
        fmax = self.radon_parse['fmax']
        fmax1 = self.radon_parse['fmax1']
        Vmin = self.radon_parse['Vmin']
        Vmax = self.radon_parse['Vmax']
        dv = self.radon_parse['dv']
        df = self.radon_parse['df']
        dt = self.dt
        dx = self.dx
        cha1 = self.radon_parse['cha1']
        cha2 = self.radon_parse['cha2']

        ml = Radon(data, dx, dt, Vmin, Vmax, dv, fmin, fmax, df)
        
        mn = np.sum(ml, axis=1)
        mn = mn / mn.std()
        inxm = np.argmax(mn)
        vv = (np.arange(Vmin, Vmax + dv, dv)) * 3.6
        
        # peaks = scipy.signal.find_peaks(mn, height=5, distance=20, width=5)

        # plt.figure(figsize=(12, 5))
        # plt.plot(vv, mn)
        # for peak in peaks[0]:
        #     plt.axvline(vv[peak], color='r')
        
        vmin = np.nanmin(ml)
        vmax = np.nanmax(ml)
        ax0 = ax.imshow(ml, cmap='RdBu_r', aspect='auto', 
                  origin='lower', extent=[fmin, fmax, Vmin*3.6, Vmax*3.6],
                  vmin=-vmin, vmax=vmax)
        
        ax.set_xlabel('Frequency [m]')
        ax.set_ylabel('Velocity [km/h]')
        ax.set_title(f'Car Velocity: {vv[inxm]:2f} km/h')
        # fig.colorbar(ax0, ax=ax)
        self.logger.info("ImShow Radon Done!")

        return ax
        
    def norm_trace(self):
        cha1 = self.radon_parse['cha1']
        cha2 = self.radon_parse['cha2']

        self.radon_data[:, cha1:cha2] = norm_trace(self.radon_data[:, cha1:cha2])

        self.logger.info("normal trace")

    def radonBpFilter(self):
        fmin = self.radon_parse['fmin']
        fmin1 = self.radon_parse['fmin1']
        fmax = self.radon_parse['fmax']
        fmax1 = self.radon_parse['fmax1']
        cha1 = self.radon_parse['cha1']
        cha2 = self.radon_parse['cha2']
        
        self.radon_data[:, cha1:cha2] = self.bp_filter(self.radon_data[:, cha1:cha2], self.dt, fmin, fmin1, fmax, fmax1)
        # self.radon_data[:, cha1:cha2] = bp_filter(self.radon_data[:, cha1:cha2], self.dt, 0.01,0.1,1,2)

        self.logger.info(f"bp filter: fmin: {fmin}, f")
        
    def RawDataBpFilter(self, fmin, fmax):
        fmin = fmin
        fmin1 = fmin+0.1
        fmax = fmax
        fmax1 = fmax+1
        self.data = self.bp_filter(self.data, self.dt, fmin, fmin1, fmax, fmax1)
        

    # TODO: 
    def bp_filter(self, data, dt, fmin, fmin1, fmax, fmax1):
        """
        Bandpass filter the data
        """
        return bp_filter(data, dt, fmin, fmin1, fmax, fmax1)
        

    def caculateDispersion(self, dispersion_parse=None, scale=1):
        """dasQt/das.py made by Zhiyu Zhang JiLin University in 2024-01-05 17h.
        Parameters
        ----------
        sps : float, (1/self.dt)
            current sampling rate
        samp_freq : float, (1/self.dt)
            targeted sampling rate
        freqmin : float, (0.1)
            pre filtering frequency bandwidth预滤波频率带宽
        freqmax : float, (10)
            note this cannot exceed Nquist freq
        freq_norm : str, ('rma')
            'no' for no whitening, or 'rma' for running-mean average, 'phase_only' for sign-bit normalization in freq domain.
        time_norm : str, ('one_bit')
            'no' for no normalization, or 'rma', 'one_bit' for normalization in time domain
        cc_method : str, ('xcorr')
            'xcorr' for pure cross correlation, 'deconv' for deconvolution;
        smooth_N : int, (5)
            moving window length for time domain normalization if selected (points)
        smoothspect_N : int, (5)
            moving window length to smooth spectrum amplitude (points)
        maxlag : float, (0.5)   
            lags of cross-correlation to save (sec)
        max_over_std : float, (10**9)   
            threahold to remove window of bad signals: set it to 10*9 if prefer not to remove them
        cc_len : float, (5)
            correlate length in second(sec)
        cha1 : int, (31)
            start channel index for the sub-array
        cha2 : int, (70)
            end channel index for the sub-array
            

        Returns
        -------
        data_liner : ndarray
            DESCRIPTION.

        """


        dt = self.dt
        dx = self.dx
        display_nt = self.display_nt
        Nt = self.nt
        Nch = self.nx
        scale = 0.1 / scale 
        data = self.data
        
        dispersion_parse['sps'] = 1/dt
        dispersion_parse['samp_freq'] = 1/dt
        

        # ---------------------------input parameters---------------------------------#

        dt = self.dt

        # ---------------------------input parameters---------------------------------#
        sps             = dispersion_parse['sps']          # current sampling rate
        samp_freq       = dispersion_parse['samp_freq']    # targeted sampling rate
        freqmin         = dispersion_parse['freqmin']      # pre filtering frequency bandwidth
        freqmax         = dispersion_parse['freqmax']      # note this cannot exceed Nquist freq
        freq_norm       = dispersion_parse['freq_norm']    # 'no' for no whitening, or 'rma' for running-mean average, 'phase_only' for sign-bit normalization in freq domain.
        time_norm       = dispersion_parse['time_norm']    # 'no' for no normalization, or 'rma', 'one_bit' for normalization in time domain
        cc_method       = dispersion_parse['cc_method']    # 'xcorr' for pure cross correlation, 'deconv' for deconvolution;
        #FOR "COHERENCY" PLEASE set freq_norm to "rma", time_norm to "no" and cc_method to "xcorr"
        smooth_N        = dispersion_parse['smooth_N']     # moving window length for time domain normalization if selected (points)
        smoothspect_N   = dispersion_parse['smoothspect_N']# moving window length to smooth spectrum amplitude (points)
        maxlag          = dispersion_parse['maxlag']       # lags of cross-correlation to save (sec)
        # criteria for data selection
        max_over_std    = dispersion_parse['max_over_std'] # threahold to remove window of bad signals: set it to 10*9 if prefer not to remove them
        cc_len          = dispersion_parse['cc_len']       # correlate length in second(sec)
        cha1            = dispersion_parse['cha1']
        cha2            = dispersion_parse['cha2']
        self.logger.debug(f"cha1: {cha1}, cha2: {cha2}")

        data            = data[:, cha1:cha2]

        cha_list        = np.array(range(cha1, cha2))
        self.cha_list   = cha_list
        nsta            = len(cha_list)

        n_pair          = int(nsta*(data.shape[0]*dt//cc_len))
        n_lag           = int(maxlag * samp_freq * 2 + 1)

        prepro_para     = { 'freqmin': freqmin,
                            'freqmax': freqmax,
                            'sps': sps,
                            'npts_chunk': cc_len * sps,
                            'nsta': nsta,
                            'cha_list': cha_list,
                            'samp_freq': samp_freq,
                            'freq_norm': freq_norm,
                            'time_norm': time_norm,
                            'cc_method': cc_method,
                            'smooth_N': smooth_N,
                            'smoothspect_N': smoothspect_N,
                            'maxlag': maxlag,
                            'max_over_std': max_over_std}

        corr_full = np.zeros([n_lag, n_pair], dtype=np.float32)
        stack_full = np.zeros([1, n_pair], dtype=np.int32)



        # -------------------------------------------------开始计算---------------------------------------------------

        mm1=data.shape[0]
        mm=int(mm1*dt//cc_len)
        mm10=int(1/dt*cc_len)
        for imin in tqdm(range(1,mm+1), desc="Processing", ncols=100):
            tdata=data[((imin-1)*mm10):imin*mm10, :]

            # perform pre-processing

            # 进行预处理
            trace_stdS, dataS = DAS_module.preprocess_raw_make_stat(tdata ,prepro_para)
            # do normalization if needed
            white_spect = DAS_module.noise_processing(dataS, prepro_para)
            Nfft = white_spect.shape[1]
            Nfft2 = Nfft // 2
            data_white = white_spect[:, :Nfft2]
            del dataS, white_spect
            # 删选合适的道
            ind = np.where((trace_stdS < prepro_para['max_over_std']) &
                        (trace_stdS > 0) &
                        (np.isnan(trace_stdS) == 0))[0]
            if not len(ind):
                raise ValueError('the max_over_std criteria is too high which results in no data')
            sta = cha_list[ind]
            white_spect = data_white[ind]


            iiS=0
            # smooth the source spectrum
            sfft1 = DAS_module.smooth_source_spect(white_spect[iiS], prepro_para)
            # correlate one source with all receivers
            corr, tindx = DAS_module.correlate(sfft1, white_spect[iiS:], prepro_para, Nfft)

            # update the receiver list
            tsta = sta[iiS:]
            receiver_lst = tsta[tindx]

            iS = int((cha2 * 2 - cha1 - sta[iiS] + 1) * (sta[iiS] - cha1) / 2)

            # stacking one minute
            corr_full[:, (imin-1)*nsta:imin*nsta] += corr.T

            # time.sleep(0.01)

        data_liner = np.zeros((n_lag, nsta))
        for iiN in range(0, mm):
            data_liner = data_liner + corr_full[:, iiN * nsta:(iiN + 1) * nsta]
        data_liner = data_liner / mm
        data_liner = normalize_data(data_liner)
        
        return data_liner


    #@nb.jit(nopython=False)
    def wigb(self, ax, indexTime=0,scale=1):

        dt = self.dt
        dx = self.dx
        display_nt = self.display_nt
        scale = 1. / scale

        data = self.data[int(indexTime): int(indexTime+display_nt)]
        data = data / np.nanmax(data)
        nt, nx = data.shape

        x = np.arange(0, nx) * dx
        t = np.arange(0, nt) * dt + indexTime * dt

        for i in range(nx):
            ax.plot(2*data[:, i]+i, 'k', lw=0.5)

        ax.set_xlabel('time')
        ax.set_ylabel('channel')
        fname = os.path.basename(self.fname).split('.')[0]
        ax.set_title(fname)
        return ax
