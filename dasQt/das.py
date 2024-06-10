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
import obspy
import pathlib
import numpy as np
# import numba as nb
from tqdm import tqdm
from scipy import fft
from scipy import signal
import matplotlib.pyplot as plt
from PIL import Image
from ultralytics import YOLO
from sklearn.linear_model import LinearRegression
from scipy.stats import linregress
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.colors as colors
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams['font.size'] = 16


from dasQt.utools.config import loadConfig, saveConfig
from dasQt.utools.readh5 import readh5
from dasQt.utools.readdat import readdat
from dasQt.CrossCorrelation import DAS_module
from dasQt.CrossCorrelation.dispersion import get_dispersion
from dasQt.CrossCorrelation.norm_trace import normalize_data
from dasQt.CarClass.Radon import Radon
from dasQt.CarClass.norm_trace1 import norm_trace
from dasQt.filter.bpFilter import bpFilter
from dasQt.filter.fkDip import fkDip
from dasQt.filter.filter import butterworth
from dasQt.Cog.cog import ncf_corre_cog
from dasQt.CarClass.curves_class import pickPoints, autoSeparation, deleteSmallClass, showClass, getVelocity, classCar
from dasQt.Logging.logPy3 import HandleLog


class DAS():
    def __init__(self) -> None:
        # data 
        self.data            : np.ndarray = None
        self.nt              : int        = None
        self.nx              : int        = None
        self.dt              : int        = None
        self.dx              : int        = None
        self.speed           : float       = 0.25 # 1x 2x 3x 0.5x 0.25x
        self.startX          : int        = 0
        self.fIndex          : int        = 0
        self.display_T       : float       = 10.0   # display time [s]
        self.scale           : float       = 1.0
        self.cc              : np.ndarray = None
        self.dispersion_list : list[str]  = []
        self.colormap        : str        = 'rainbow'

        # Process bool
        self.bool_cut         : bool = False
        self.bool_downSampling: bool = False
        self.bool_filter       : bool = False
        self.bool_columnFK    : bool = False
        self.bool_rowFK       : bool = False
        self.bool_saveCC      : bool = False
        self.bool_saveFig     : bool = False
        self.bool_upcc        : bool = False
        self.bool_downcc      : bool = False
        

        # Car Class
        self.threshold: float  = 0.01
        self.skip_Nch : int   = 2
        self.skip_Nt  : int   = 1000
        self.maxMode  : int   = 10
        self.minCarNum: int   = 15
        self.to       : float  = 0.01
        self.mode     : str   = 'max'

        # Dispersion
        self.indexClick      : int  = 0
        self.dispersion_parse: dict = {}
        self.radon_parse     : dict = {}
        self.logger = HandleLog(os.path.split(__file__)[-1].split(".")[0], path=os.getcwd(), level="info")
        
        self.model = YOLO('./dasQt/YOLO/best.pt')


    #-----------------------------------------------------------
    #
    # Load Data
    #
    #-----------------------------------------------------------

    def readData(self, filename: str='./Data/SR_2023-07-20_09-09-38_UTC.h5') -> None:
        """read data from h5 or dat file"""
        self.fname       = filename
        file_path         = pathlib.Path(self.fname)
        self.DP_filename  = './DPdata/' + file_path.stem + '_dispersion.h5'

        # fileType = os.path.splitext(filename)[-1]
        fileType = file_path.suffix

        if fileType == '.h5':
            self.data, self.dx, self.dt, self.nt, self.nx = readh5(filename)
            self.color_value = 1000.
        elif fileType == '.dat':
            self.data, self.dx, self.dt, self.nt, self.nx = readdat(filename)
            self.color_value = 0.5
        else:
            self.logger.error("File Type Error!")
            raise ValueError("File Type Error!")

        self.profile_X   = np.arange(self.nx) * self.dx
        self.pre_data   = self.data.copy()
        self.radon_data = self.data.copy()
        filepath         = pathlib.Path(filename)

        self.process()
        self.logger.info(f"\n{filepath.name} read done!")
        self.logger.info(f"\nnt: {self.nt}, nx: {self.nx}, dt: {self.dt}, dx: {self.dx}")
        if self.bool_saveFig:
            self.saveFig(colormap=self.colormap)


    def openFolder(self, foldername: str='./das/') -> list[str]:
        self.foldername = foldername
        self.fnames     = sorted(os.listdir(foldername))
        self.logger.info(f"open {foldername} done!")

        return self.fnames


    def getFileID(self, fname: str) -> None:
        """get the file index by file name"""
        for index, value in enumerate(self.fnames):
            if value == fname:
                self.fIndex = index
                break

        self.logger.debug(f"{fname} is the {self.fIndex}s file")


    def process(self) -> None:
        """process data after read"""
        if self.bool_cut:
            self.cutData(self.profile_Xmin, self.profile_Xmax)
        if self.bool_downSampling:
            self.downSampling(self.initNumDownSampling)
        if self.bool_filter:
            self.RawDataBpFilter(self.fmin, self.fmin1, self.fmax, self.fmax1)
        if self.bool_columnFK:
            self.RawDataFKFilterColumn(self.w_column)
        if self.bool_rowFK:
            self.RawDataFKFilterRow(self.w_row)


    def readNextData(self) -> None:
        if self.fnames:
            self.fIndex += 1
            try:
                self.fname = self.fnames[self.fIndex]
                self.readData(os.path.join(self.foldername, self.fname))
                self.logger.debug(f"next file is {self.fname}")
            except IndexError:
                self.logger.error("Index Error!")
                raise IndexError("Index Error!")

    #-----------------------------------------------------------
    #
    # Process Data
    #
    #-----------------------------------------------------------

    def rawData(self) -> None:
        """reset the data to the original data"""
        self.data = self.pre_data.copy()


    def downSampling(self, intNumDownSampling=2) -> None:
        """Down Sampling"""
        self.initNumDownSampling = intNumDownSampling
        self.data                = self.data[::intNumDownSampling, :]
        self.dt                  = self.dt * intNumDownSampling
        self.nt                  = self.data.shape[0]


    def cutData(self, Xmin, Xmax) -> None:
        """Cut the data by Xmin and Xmax"""
        self.profile_Xmin = Xmin; self.profile_Xmax = Xmax
        X = np.arange(self.nx) * self.dx

        Xmin_Num = np.abs(float(Xmin) - X).argmin()
        if Xmax == 'end':
            Xmax_Num = self.nx
        else:
            Xmax_Num = np.abs(float(Xmax) - X).argmin()

        self.data = self.data[:, Xmin_Num:Xmax_Num]
        self.profile_X = X[Xmin_Num:Xmax_Num]
        self.nx = self.data.shape[1]
        self.logger.info("Cut Data Done!")



    def RawDataBpFilter(self, fmin, fmin1, fmax, fmax1) -> None:
        """"Bandpass filter for raw data"""
        self.fmin = fmin; self.fmin1 = fmin1; self.fmax = fmax; self.fmax1 = fmax1
        self.data = bpFilter(self.data, self.dt, fmin, fmin1, fmax, fmax1)

    def RawDataFKFilterColumn(self, w=0.05) -> None:
        self.w_column = w
        data = fkDip(self.data, w)
        self.data = self.data - data

    def RawDataFKFilterRow(self, w=0.05) -> None:
        self.w_row = w
        data = fkDip(self.data.T, w)
        self.data = self.data - data.T


    def caculateCC(self, dispersion_parse=None, scale=1, allstacks1=None):
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

        
        # ---------------------------input parameters---------------------------------#
        # FOR "COHERENCY" PLEASE set freq_norm to "rma", time_norm to "no" and cc_method to "xcorr"
        dt                   = self.dt
        sps                  = 1/dt                             # current sampling rate
        samp_freq            = 1/dt                             # targeted sampling rate
        cha1                 = np.abs(float(dispersion_parse['cha1']) - self.profile_X).argmin()
        cha2                 = np.abs(float(dispersion_parse['cha2']) - self.profile_X).argmin()
        self.dispersion_cha1 = cha1
        self.dispersion_cha2 = cha2
        self.logger.debug(f"cha1: {cha1}, cha2: {cha2}")

        cc_len               = dispersion_parse['cc_len']       # correlate length in second(sec)
        maxlag               = dispersion_parse['maxlag']       # lags of cross-correlation to save (sec)
        data                 = self.data[:, cha1:cha2].copy()
        cha_list             = np.array(range(cha1, cha2))
        nsta                 = len(cha_list)
        n_pair               = int(nsta*(data.shape[0]*dt//cc_len))
        n_lag                = int(maxlag * samp_freq * 2 + 1)

        corr_full            = np.zeros([n_lag, n_pair], dtype=np.float32)
        stack_full           = np.zeros([1, n_pair], dtype=np.int32)

        prepro_para     = { 
            'sps'          : 1/dt,                              # current sampling rate
            'npts_chunk'   : cc_len * sps,                      # correlate length in second(sec)
            'nsta'         : nsta,                              # number of stations
            'cha_list'     : cha_list,                          # channel list
            'samp_freq'    : 1/dt,                              # targeted sampling rate
            'freqmin'      : dispersion_parse['freqmin'],       # pre filtering frequency bandwidth
            'freqmax'      : dispersion_parse['freqmax'],       # note this cannot exceed Nquist freq
            'freq_norm'    : dispersion_parse['freq_norm'],     # 'no' for no whitening, or 'rma' for running-mean average, 'phase_only' for sign-bit normalization in freq domain.
            'time_norm'    : dispersion_parse['time_norm'],     # 'no' for no normalization, or 'rma','one_bit' for normalization in time domain
            'cc_method'    : dispersion_parse['cc_method'],     # 'xcorr' for pure cross correlation, 'deconv' for deconvolution;
            'smooth_N'     : dispersion_parse['smooth_N'],      # moving window length for time domain normalization if selected (points)
            'smoothspect_N': dispersion_parse['smoothspect_N'], # moving window length to smooth spectrum amplitude (points)
            'maxlag'       : dispersion_parse['maxlag'],        # lags of cross-correlation to save (sec)
            'max_over_std' : dispersion_parse['max_over_std']   # threahold to remove window of bad signals: set it to 10*9 if prefer not to remove them
        }
        # TODO: load and save config
        # def default() -> None:
        #     if self.bool_loadCCconfig:
        #         prepro_para = loadConfig(cc_config_pathname)

        
        # def save() -> None:
        #     if self.bool_saveCCconfig
        #         saveConfig(prepro_para, cc_config_pathname)

        # -------------------------------------------------开始计算---------------------------------------------------
        mm1  = data.shape[0]
        mm   = int(mm1*dt//cc_len)
        mm10 = int(1/dt*cc_len)
        for imin in tqdm(range(1,mm+1), desc="Processing", ncols=100):
            tdata=data[((imin-1)*mm10):imin*mm10, :]

            # preprocess the raw data
            trace_stdS, dataS = DAS_module.preprocess_raw_make_stat(tdata ,prepro_para)
            # do normalization if needed
            white_spect = DAS_module.noise_processing(dataS, prepro_para)
            Nfft        = white_spect.shape[1]
            Nfft2       = Nfft                                             // 2
            data_white  = white_spect[:, :Nfft2]
            del dataS, white_spect
            # find the good data
            ind = np.where((trace_stdS < prepro_para['max_over_std']) &
                        (trace_stdS > 0) &
                        (np.isnan(trace_stdS) == 0))[0]
            if not len(ind):
                raise ValueError('the max_over_std criteria is too high which results in no data')
            sta         = cha_list[ind]
            white_spect = data_white[ind]

            iiS = 0
            # smooth the source spectrum
            sfft1 = DAS_module.smooth_source_spect(white_spect[iiS], prepro_para)
            # correlate one source with all receivers
            corr, tindx = DAS_module.correlate(sfft1, white_spect[iiS:], prepro_para, Nfft)

            # update the receiver list
            tsta         = sta[iiS:]
            receiver_lst = tsta[tindx]
            iS           = int((cha2 * 2 - cha1 - sta[iiS] + 1) * (sta[iiS] - cha1) / 2)

            # stacking one minute
            corr_full[:, (imin-1)*nsta:imin*nsta] += corr.T

        data_liner = np.zeros((n_lag, nsta))
        for iiN in range(0, mm):
            data_liner = data_liner + corr_full[:, iiN * nsta:(iiN + 1) * nsta]
        data_liner = data_liner / mm
        data_liner = normalize_data(data_liner)
        
        # return allstacks1, data_liner
        return data_liner


    def caculateCCAll(self, ax) -> None:
        """caculate dispersion for all files with stack"""

        data_list = []
        for dispersionfile in self.dispersion_list:
            with h5py.File(dispersionfile, 'r') as f:
                data = f['dispersion'][:]
                dt = f['dt'][()]
                dx = f['dx'][()]
            
            data_list.append(data)
        
        data = np.array(data_list)
        print(data.shape)
        n, nt, nx = data.shape
        data = data.reshape(n, -1)

        stack_para = {
            'samp_freq': 1/dt,
            'npts_chunk': nt,
            'nsta': nx,
            'stack_method': 'linear'
        }

        allstacks1 = DAS_module.stacking(data,stack_para)
        nt, nx = allstacks1.shape
        if self.bool_downcc:
            self.ccAll = allstacks1[nt//2:, :]
        elif self.bool_upcc:
            self.ccAll = allstacks1[:nt//2, :]
        else:
            self.ccAll = allstacks1

        ax0 = ax.imshow(allstacks1, cmap='RdBu_r', aspect='auto', origin='lower', extent=[0, nx, -nt//2*dt, nt//2*dt])

        with h5py.File(self.DP_filename, 'w') as f:
            f.create_dataset('dispersion', data=allstacks1)
            f.create_dataset('dt', data=dt)
            f.create_dataset('dx', data=dx)
        
        self.logger.info("ImShow Cross-correlation All Done!")
    






    def muteData(d, dx, dt, Xmin, Ymin, Xmax, Ymax, mode='up', slope=0.0):
        # Xmin = 20
        # Ymin = 0.0
        # Xmax = 150
        # Ymax = 0.7

        X = np.arange(0, d.shape[1]*dx, dx)
        Y = np.arange(0, d.shape[0]*dt, dt)

        x2, y2 = np.abs(float(Xmin) - X).argmin(), np.abs(float(Ymin) - Y).argmin()
        x3, y3 = np.abs(float(Xmax) - X).argmin(), np.abs(float(Ymax) - Y).argmin()
        print(x2, y2, x3, y3)
        if slope == 0.0:
            # 计算斜边的斜率
            slope = (y3 - y2) / (x3 - x2)

        if mode == 'up':
            # 逐行赋值
            for x in range(x2, d.shape[1]):
                # 根据斜率和行号计算这一行中斜边对应的列号
                y = int(slope * (x - x2) + y2)
                # 将从起始列到斜边对应列的元素赋值为 0
                d[:y + 1, x] = 0
        elif mode == 'down':
            # 逐行赋值
            for x in range(0, d.shape[1]):
                # 根据斜率和行号计算这一行中斜边对应的列号
                y = int(slope * (x - x2) + y2)
                # 将从起始列到斜边对应列的元素赋值为 0
                d[y + 1:, x] = 0
        
        return d, slope

    def saveCC(self) -> None:
        """save dispersion data"""
        # filename = os.path.splitext(self.fname)[-2] + '_dispersion.mseed'
        filename = self.DP_filename

        with h5py.File(filename, 'w') as f:
            f.create_dataset('dispersion', data=self.cc)
            f.create_dataset('dt', data=self.dt)
            f.create_dataset('dx', data=self.dx)

        self.logger.info(f"Save Dispersion Done! {filename}")


    def norm_trace(self) -> None:
        """"normalize trace"""
        cha1 = self.radon_parse['cha1']
        cha2 = self.radon_parse['cha2']

        self.radon_data[:, cha1:cha2] = norm_trace(self.radon_data[:, cha1:cha2])
        self.logger.info("normal trace")


    def radonBpFilter(self) -> None:
        """"radon data bandpass filter"""
        fmin  = self.radon_parse['fmin']
        fmin1 = self.radon_parse['fmin1']
        fmax  = self.radon_parse['fmax']
        fmax1 = self.radon_parse['fmax1']
        cha1  = self.radon_parse['cha1']
        cha2  = self.radon_parse['cha2']
        
        self.radon_data[:, cha1:cha2] = bpFilter(self.radon_data[:, cha1:cha2], self.dt, fmin, fmin1, fmax, fmax1)
        # self.radon_data[:, cha1:cha2] = bpFilter(self.radon_data[:, cha1:cha2], self.dt, 0.01,0.1,1,2)
        self.logger.info(f"bp filter: fmin: {fmin}, f")

    def signalTrace(self, trace):
        idx = np.abs(self.profile_X - trace).argmin()
        data = self.data[:, idx]

        delta = self.dt
        npts = len(data) 
        t = delta * np.arange(npts)
        xf = fft.fftfreq(npts, delta)
        yf = fft.fft(data)

        return t, data, np.abs(xf), np.abs(yf)

    # TODO: CC Data get Up
    def getUpCC(self, up) -> None:
        """get up cross-correlation"""
        self.bool_upcc = up

    def getDownCC(self, down) -> None:
        """get down cross-correlation"""
        self.bool_downcc = down



    def selfGetDispersion(self, cmin=10., cmax=1000.0, dc=5., fmin=4.0, fmax=18.0):
        if self.bool_downcc:
            nt, nx = self.cc.shape
            cc = self.cc[:nt//2, :]
        elif self.bool_upcc:
            nt, nx = self.cc.shape
            cc = self.cc[nt//2:, :]
        else:
            cc = self.cc

        f, c, img, U, t = get_dispersion(cc, self.dx, self.dt, 
                                             cmin, cmax, dc, fmin, fmax)
        
        for i in range(img.shape[1]):
            img[:,i] /= np.max(img[:,i])
        
        return f, c, img**5, U, t

    def selfGetDispersionAll(self, Cmin=10., Cmax=1000.0, dc=5., fmin=4.0, fmax=18.0):
        if self.bool_downcc:
            nt, nx = self.ccAll.shape
            cc = self.ccAll[:nt//2, :]
        elif self.bool_upcc:
            nt, nx = self.ccAll.shape
            cc = self.ccAll[nt//2:, :]
        else:
            cc = self.ccAll

        f, c, img, U, t = get_dispersion(cc, self.dx, self.dt, 
                                             Cmin, Cmax, dc, fmin, fmax)
        
        for i in range(img.shape[1]):
            img[:,i] /= np.max(img[:,i])
        
        return f, c, img**5, U, t





    # def caculateCog(self, data, nch, win, nwin, overlap, offset):
    #     """caculate the normalized cross-correlation function (NCF) for ambient noise data"""
    #     ncf = np.zeros((win, nch))
    #     ncf_all  = np.zeros((win,nch))

    #         data, dx, dt, _, _ = readdat(file)
    #         print(file.name)
    #         data = data
    #         nt, nx = data.shape
    #         nch = nx

    #         ncf_shot=ncf_corre_cog(data,nch,win,nwin,overlap,offset1)
    #         ncf_all=ncf_all+ncf_shot
    #         ncf_shot=ncf_corre_cog(data,nch,win,nwin,overlap,offset2)
    #         ncf_all2=ncf_all2+ncf_shot

    def caculateCogAll(self, Ndata, nch, win, nwin, overlap, offset, fmin1=2., fmin2=3., fmax1=20., fmax2=21., ylim=None):
        files = self.fnames
        path = pathlib.Path(self.fname).parent
        id = self.fIndex
        
        
        ncf_all  = np.zeros((win,nch))
        for file in files[id:id+Ndata]:
            self.readData(path/file)
            data = self.pre_data.copy()
            ncf_shot = ncf_corre_cog(data, nch, win, nwin, overlap, offset)
            ncf_all = ncf_all + ncf_shot

        ncf_all = np.fft.fftshift(ncf_all, axes=0)  # Shift along the first axis (similar to MATLAB's dimension 1)
        ncf_all = ncf_all + np.flip(ncf_all, axis=0)  # Flip and add along the first axis

        dt = self.dt
        a1 = bpFilter(ncf_all,dt,fmin1,fmin2,fmax1,fmax2)
        a1 = normalize_data(a1)
        a1 = a1[a1.shape[0]//2:,:]

        return a1

    def imshowCog(self, ax, Ndata, win, nwin, overlap, offset, fmin1=2., fmin2=3., fmax1=20., fmax2=21., ylim=None, vmin=None, vmax=None):
        nch = self.nx
        if ylim is None:
            cog = self.caculateCogAll(Ndata, nch, win, nwin, overlap, offset, fmin1, fmin2, fmax1, fmax2, ylim)
            self.cog = cog
            ax.imshow(cog, cmap='Greys', aspect='auto', extent=[0, self.nx*self.dx, cog.shape[0]*self.dt, 0])
        else:
            cog = self.cog
            ax.imshow(cog, cmap='Greys', aspect='auto', extent=[0, self.nx*self.dx, cog.shape[0]*self.dt, 0], vmin=vmin, vmax=vmax)
        print(cog.shape, self.dt)
        
        
        ax.set_title(f'cog with offset={offset}')
        ax.set_xlabel('Distance (m)')
        ax.set_ylabel('Time (s)')
        # ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        if ylim is not None:
            ax.set_ylim(ylim)

        return ax


    #-----------------------------------------------------------
    #
    # Imshow Data
    #
    #-----------------------------------------------------------

    def imshowData(self, ax, indexTime=0, colormap='rainbow'):
        """"imshow raw data by indexTime and scale"""
        dt         = self.dt
        display_nt = self.display_T / self.dt
        indexTime  = int(indexTime / dt / 100)
        data       = self.data[int(indexTime): int(indexTime+display_nt)]
        self.logger.debug(f"dt: {dt}")
        self.colormap = colormap

        ax.imshow(data, 
                aspect = 'auto',
                origin = 'lower',
                cmap = colormap,
                extent = [self.profile_X[0], self.profile_X[-1], indexTime*dt, (indexTime+display_nt)*dt],
                vmin   = -self.color_value/self.scale,
                vmax   = self.color_value/self.scale)

        fname = os.path.basename(self.fname).split('.')[0]
        ax.set_xlabel('distance (m)')
        ax.set_ylabel('time (s)')
        ax.set_title(fname)

        return ax

    def saveFig(self, colormap='rainbow') -> None:
        fig = plt.figure()
        ax = fig.add_axes([0,0,1,1])
        ax.imshow(self.data, 
                aspect = 'auto',
                # origin = 'lower',
                cmap = colormap,
                vmin   = -self.color_value/self.scale,
                vmax   = self.color_value/self.scale)

        fname = pathlib.Path(self.fname).stem
        save_path = pathlib.Path('./figs/')
        save_path.mkdir(parents=True, exist_ok=True)
        figname = save_path / f'{fname}.png'
        self.yolo_figname = figname
        ax.axis("off")
        ax.margins(0)
        plt.savefig(figname, dpi=300)
        self.logger.info(f"Save {figname} Done!")
        plt.close()
        
        

    def imshowDataAll(self, ax):
        """"imshow all raw data in one figure"""
        data       = self.data
        dt         = self.dt
        nt         = self.nt
        self.logger.debug(f"dt: {dt}")

        ax.imshow(data, 
                aspect = 'auto',
                cmap   = 'rainbow',
                origin = 'lower',
                extent = [self.profile_X[0], self.profile_X[-1], 0, nt*dt],
                vmin   = -self.color_value/self.scale,
                vmax   = self.color_value/self.scale)

        fname = os.path.basename(self.fname).split('.')[0]
        ax.set_xlabel('distance (m)')
        ax.set_ylabel('time (s)')
        ax.set_title(fname)

        return ax


    def imshowCarClass(self, ax, scale=1, 
                       skip_Nch=2, skip_Nt=1000, threshold=0.1, mode='min',
                       maxMode=10, minCarNum=15, to=0.01,line=0.5):
        dt    = self.dt
        dx    = self.dx
        Nt    = self.nt
        Nch   = self.profile_X.shape[0]
        data  = self.data

        # x = np.linspace(0, Nch * dx, Nch)        # x-axis
        x = self.profile_X
        print(Nch, x.shape)
        t = np.linspace(0, Nt * dt, Nt)          # t-axis

        # pick points

        curves = pickPoints(data, Nch, Nt, skip_Nch=skip_Nch, skip_Nt=skip_Nt, threshold=threshold, model=mode)
        if curves is None:
            return 0

        # auto separation
        # to = 0.01, threshold of distance
        # maxMode = 10, 10 classes
        # minCarNum = 15, min car number in one class

        curves_km = autoSeparation(curves, to=to, maxMode=maxMode)
        id_list   = np.unique(curves_km[...,-1])
        class_num = len(id_list)

        curves_km = deleteSmallClass(curves_km, class_num, minCarNum=minCarNum)

        id_list   = np.unique(curves_km[...,-1])
        class_num = len(id_list)

        # get velocity
        velocities, id_list_a = getVelocity(curves_km, x, t, id_list)

        # class car
        id_list_b = classCar(curves_km, id_list, scale=line)
        self.logger.info(f"velocities: {velocities}")

        scale = self.color_value / self.scale
        ax = showClass(data, curves_km, id_list_b, t, x, ax, 
                       s='b)', title="Only Car", model='vel', velocities=velocities, 
                       vmin=-scale, vmax=scale)
        self.logger.info("ImShow CarClass Done!")

        return ax


    def imshowCC(self, ax, dispersion_parse=None, scale=1):
        scale = 0.5

        data_liner = self.caculateCC(dispersion_parse=dispersion_parse, 
                                                scale=scale, 
                                                allstacks1=0.0)
        
        self.cc = data_liner
        if self.indexClick == 0:
            self.pre_dispersion_data  = data_liner
            self.indexClick          += 1
        else:
            if self.pre_dispersion_data.shape != data_liner.shape:
                self.pre_dispersion_data = data_liner
                self.indexClick          = 0
                self.logger.debug(f"dp para changed, last index is {self.indexClick}, now index is 0")
            else:
                if self.bool_saveCC:
                    # self.pre_dispersion_data  = (self.pre_dispersion_data*self.indexClick + data_liner) / (self.indexClick+1)
                    self.dispersion_list.append(self.DP_filename)
                    self.indexClick          += 1
                    self.logger.debug(f"now index is {self.indexClick}")
        
        cha1 = self.profile_X[self.dispersion_cha1]
        cha2 = self.profile_X[self.dispersion_cha2]
        # nt   = self.pre_dispersion_data.shape[0]
        nt = data_liner.shape[0]


        ax0 = ax.imshow(data_liner, cmap='RdBu_r', aspect='auto', 
                  origin='lower', extent=[cha1, cha2, -nt//2*self.dt, nt//2*self.dt])

        ax.set_xlabel('distance (m)')
        ax.set_ylabel('time (s)')
        ax.set_title('Cross-correlation')
        # fig.colorbar(ax0, ax=ax)
        self.logger.info("ImShow Cross-correlation Done!")
        return ax


    def imshowRadon(self, ax, indexTime=0, scale=1):
        # scale = 1. / scale
        data = self.radon_data
        nt, nx = data.shape
        
        fmin  = self.radon_parse['fmin']
        fmin1 = self.radon_parse['fmin1']
        fmax  = self.radon_parse['fmax']
        fmax1 = self.radon_parse['fmax1']
        Vmin  = self.radon_parse['Vmin']
        Vmax  = self.radon_parse['Vmax']
        dv    = self.radon_parse['dv']
        df    = self.radon_parse['df']
        dt    = self.dt
        dx    = self.dx
        cha1  = self.radon_parse['cha1']
        cha2  = self.radon_parse['cha2']

        ml = Radon(data, dx, dt, Vmin, Vmax, dv, fmin, fmax, df)

        mn   = np.sum(ml, axis=1)
        mn   = mn / mn.std()
        inxm = np.argmax(mn)
        vv   = (np.arange(Vmin, Vmax + dv, dv)) * 3.6

        vmin = np.nanmin(ml)
        vmax = np.nanmax(ml)
        ax0 = ax.imshow(ml, cmap='RdBu_r', aspect='auto', 
                  origin='lower', extent=[fmin, fmax, Vmin*3.6, Vmax*3.6],
                  vmin=-vmin, vmax=vmax)
        
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Velocity (km/h)')
        ax.set_title(f'Car Velocity: {vv[inxm]:2f} km/h')
        # fig.colorbar(ax0, ax=ax)
        self.logger.info("ImShow Radon Done!")

        return ax


    #@nb.jit(nopython=False)
    def wigb(self, ax, indexTime=0):

        dt = self.dt
        dx = self.dx
        display_nt = self.display_T / self.dt

        data = self.data[int(indexTime): int(indexTime+display_nt)]

        # data = data / np.nanmax(data, axis=0)
        # nan_max = np.nanmax(data, axis=0)
        # nan_mean = np.nanmean(data, axis=0)
        # data = data - nan_mean
        nan_max = np.nanmax(np.abs(data), axis=0)
        data = data / nan_max

        nt, nx = data.shape

        x = np.arange(0, nx) * dx
        t = np.arange(int(indexTime), int(indexTime+display_nt)) * dt
        # scale = self.color_value/self.scale

        for i in range(nx):
            ax.plot(t, 0.8*data[:, i]+i, 'k', lw=0.5)

        ax.set_xlabel('time (s)')
        ax.set_ylabel('channel')
        fname = os.path.basename(self.fname).split('.')[0]
        ax.set_title(fname)
        return ax


    def imshowDispersion(self, ax, cmin, cmax, dc, fmin, fmax):
        
        f, c, img, U, t = self.selfGetDispersion(cmin, cmax, dc, fmin, fmax)
        
        bar2 = ax.imshow(img[:,:],aspect='auto',origin='lower',extent=(f[0],f[-1],c[0],c[-1]), 
                cmap='jet', interpolation='bilinear')

        ax.grid(linestyle='--',linewidth=2)
        ax.set_xlabel('Frequency (Hz)', fontsize=14)
        ax.set_ylabel('Phase velocity (m/s)', fontsize=14)
        ax.tick_params(axis = 'both', which = 'major', labelsize = 14)
        ax.tick_params(axis = 'both', which = 'minor', labelsize = 14)

        # fig.colorbar(bar1, ax=ax1, orientation='vertical', label='Amplitude')
        # fig.colorbar(bar2, ax=ax, orientation='vertical', label='Normalized amplitude')


    def imshowDispersionAll(self, ax, Cmin, Cmax, dc, fmin, fmax):
        f, c, img, U, t = self.selfGetDispersionAll(Cmin, Cmax, dc, fmin, fmax)
        
        bar2 = ax.imshow(img[:,:],aspect='auto',origin='lower',extent=(f[0],f[-1],c[0],c[-1]),
                cmap='jet', interpolation='bilinear')
        
        ax.grid(linestyle='--',linewidth=2)
        ax.set_xlabel('Frequency (Hz)', fontsize=14)
        ax.set_ylabel('Phase velocity (m/s)', fontsize=14)
        ax.tick_params(axis = 'both', which = 'major', labelsize = 14)
        

    def getSlope(self, tt, xx, mode='sklearn'):
        tt = tt.reshape(-1, 1)
        if mode == 'sklearn':
            model = LinearRegression()
            model.fit(tt, xx)
            slope = model.coef_[0]
            # intercept = model.intercept_
        elif mode == 'scipy':
            slope = linregress(tt.flatten(), xx.flatten()).slope
        elif mode == 'numpy':
            slope, intercept = np.polyfit(tt.flatten(), xx.flatten(), 1)
            # print('斜率: ', slope)
            # print('截距: ', intercept)

        return slope


    def getMaskXY(self, result, mode='sklearn'):
        T = np.linspace(0, 60, 512)
        X = np.linspace(0, 150, 512)
        vels = []
        if result.masks is None:
            return vels
        for mask in result.masks:
            mask = mask.data.cpu().numpy()
            _, x, y = np.where(mask == 1)
            tt = T[x]
            xx = X[y]
            slope = self.getSlope(tt, xx, mode=mode)

            vel = slope*3.6
            vels.append(vel)

        return vels

    
    def imshowYolo(self, fig):
        ax1 = fig.add_subplot(121)
        img = Image.open(self.yolo_figname)
        img = np.array(img)
        ax1.imshow(img, aspect='auto', extent=[self.profile_X[0], self.profile_X[-1], self.nt*self.dt, 0])
        ax1.set_xlabel('Distance (m)')
        ax1.set_ylabel('Time (s)')
        ax1.set_title('Velocity')
        
        result = self.model(self.yolo_figname, nms=True, iou=0.75, conf=0.65)[0]
        vels = self.getMaskXY(result)

        masks = result.masks.data.cpu().numpy()
        masks_len = len(masks)
        bb = np.zeros_like(masks[0])
        for ii in range(masks_len):
            masks[ii][masks[ii] > 0] = vels[ii]
            bb[masks[ii] > 0] = vels[ii]

        # TODO:
        # aa = np.sum(masks, axis=0)
        aa = bb
        # bb = np.zeros_like(masks[0])
        # for ii in range(masks_len):
        #     cc = bb.copy()
        #     dd = masks[ii][masks[ii] > 0]
            
            
            
            
        
        matrix_filtered = np.where(aa > 0, aa, np.nan)

        ax2 = fig.add_subplot(122)
        # 设置归一化的范围为20到100
        norm = colors.Normalize(vmin=30, vmax=55)
        # 选择一个色彩映射
        cmap = plt.cm.gnuplot2

        im = ax2.imshow(matrix_filtered, cmap=cmap, norm=norm, aspect='auto', extent=[self.profile_X[0], self.profile_X[-1], self.nt*self.dt, 0])
        ax2.set_xlabel('Distance (m)')
        ax2.set_ylabel('Time (s)')
        ax2.set_title('Velocity')

        # 对色阶条独立设置位置和大小
        divider = make_axes_locatable(ax2)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        cb = plt.colorbar(im, cax=cax)
        cb.set_label('Velocity (km/h)')

        fig.tight_layout()

        return fig

