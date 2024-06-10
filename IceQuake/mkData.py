import sys
sys.path.insert(0, '../')
from dasQt import das
import numpy as np
import pathlib

import obspy
from datetime import datetime

das1 = das.DAS()

# read the data
das1.scale = 100
path_dir = pathlib.Path('/Volumes/CSIM_LAB/DATA/Car-JLU-2024-01-31/ovlink/2024-02-01')
files = list(path_dir.glob('*.dat'))
path_dir_new = pathlib.Path('/Volumes/CSIM_LAB/DATA/Car-JLU-2024-01-31/ovlink/new_2024-02-01')
path_dir_new.mkdir(exist_ok=True)


# das1.scale = 0.01
# path_dir = pathlib.Path('/Volumes/CSIM_LAB/DATA/nanhu-2024-02-01')
# files = list(path_dir.glob('*.h5'))
# path_dir_new = pathlib.Path('/Volumes/CSIM_LAB/DATA/nanhu-2024-02-01-mseed')
# path_dir_new.mkdir(exist_ok=True)

def mkStream(i, dt, d, dati):
    st = obspy.Stream()
    stats = obspy.core.Stats()
    stats.network = 'XX'
    stats.station = 'XX'
    stats.location = 'XX'
    stats.channel = 'Z'
    stats.filename = i
    stats.sampling_rate = 1/dt
    stats.starttime = obspy.UTCDateTime(dati)
    st.append(obspy.Trace(data=d, header=stats))
    
    return st

i = 0
files = sorted(files)[:] 
for file in files:
    das1.readData(file)
    starttime = file.stem
    dt_format = "%Y-%m-%d-%H-%M-%S"
    # dati = datetime.strptime(starttime[1:20], dt_format)  # 只获取前19个字符，这部分是日期和时间
    dati = datetime.strptime(starttime[:19], dt_format)  # 只获取前19个字符，这部分是日期和时间

    nt, nx = das1.data.shape
    file_dir = path_dir_new / file.stem
    file_dir.mkdir(exist_ok=True)
    for x in range(nx):
        st = mkStream(x, das1.dt, das1.data[:, x], dati)
        st.write(str(file_dir / f'{x:03}.mseed'), format='MSEED')
    i += 1
    print(i, file.stem, 'done')
    # if i == 10:
    #     break
