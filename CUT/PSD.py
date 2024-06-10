import scipy.signal as signal
import obspy
import matplotlib.pyplot as plt
import numpy as np
import pathlib
from concurrent.futures import ProcessPoolExecutor
from dasQt import das

# dir_path = pathlib.Path('/Volumes/CSIM_LAB/DATA/Car-JLU-2024-01-31/ovlink/2024-02-01')
# files = sorted(dir_path.glob('*.dat'))
# print(len(files), 'files')
# file = files[10]
# das1 = das.DAS()
# das1.readData(file)


def plotPSD(tr, t, PSD, name):
    with plt.style.context('ggplot'):
        fig, ax = plt.subplots(2, 1, figsize=(10, 6))
        ax[0].plot(t, tr.data, 'k')
        ax[0].set_xlabel('Time (s)')
        ax[0].set_ylabel('Amplitude')
        ax[0].set_title('Signal')
        ax[1].plot(PSD[0], PSD[1], 'r', label='PSD')
        ax[1].set_xlabel('frequence (Hz)')
        ax[1].set_ylabel('PSD ($V^2/Hz$)')
        # ax[1].set_xscale('log')
        # ax[1].set_yscale('log')
        ax[1].set_title(f'PSD of {name}')
        plt.tight_layout()
        plt.savefig(f'./PSD/{name}.png', dpi=300)
        # plt.show()
        plt.close()

def process_file(file):
    # file = path_dir_new1 / '070.mseed'
    d = obspy.read(file)
    tr = d[0]
    df = tr.stats.sampling_rate
    dt = 1/df

    data = tr.data[int(2000//dt):] # int(2500//dt)
    t = np.arange(0, len(data)/df, 1/df)
    tr.data = data

    PSD = signal.welch(tr.data, fs=tr.stats.sampling_rate)
    plotPSD(tr, t, PSD, int(file.stem) * 2.0)



if __name__ == '__main__':
    path_dir_new1 = pathlib.Path('/Volumes/CSIM_LAB/DATA/Car-JLU-2024-01-31/ovlink/new_2024-02-01-all')
    with ProcessPoolExecutor(max_workers=4) as executor:
        for file in sorted(path_dir_new1.glob('*.mseed')):
            executor.submit(process_file, file)
