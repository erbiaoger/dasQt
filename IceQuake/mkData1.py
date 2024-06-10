import sys
sys.path.insert(0, '../')
from dasQt import das
import numpy as np
import pathlib

import obspy
from datetime import datetime



# path_dir_new = pathlib.Path('/Volumes/CSIM_LAB/DATA/nanhu-2024-02-01-mseed')
# path_dir_new1 = pathlib.Path('/Volumes/CSIM_LAB/DATA/nanhu-2024-02-01-mseed-all')

path_dir_new = pathlib.Path('/Volumes/CSIM_LAB/DATA/Car-JLU-2024-01-31/ovlink/new_2024-02-01')
path_dir_new1 = pathlib.Path('/Volumes/CSIM_LAB/DATA/Car-JLU-2024-01-31/ovlink/new_2024-02-01-all')
path_dir_new1.mkdir(exist_ok=True)

dirs = sorted(path_dir_new.glob('*'))[1:]
dir = dirs[0]
files = []
for file in sorted(dir.glob('*.mseed')):
    files.append(file.name)

for file in files:
    i = 0
    for dir in dirs:
        st = obspy.read(str(dir / file))
        if i == 0:
            st_all = st.copy()
            i = 1
        else:
            st_all[0].data = np.hstack((st_all[0].data, st[0].data))

    print(f'{pathlib.Path(file).stem}.mseed')
    st_all.write(str(path_dir_new1 / f'{pathlib.Path(file).stem}.mseed'), format='MSEED')