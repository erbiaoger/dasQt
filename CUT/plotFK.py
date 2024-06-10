import sys
sys.path.insert(0, '../')
import pathlib
import numpy as np
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
import threading
import matplotlib
# matplotlib.use('Agg')  # 使用非 GUI 后端

from dasQt import das
from fkFilter import fkFilter


# 定义处理单个文件的函数
def process_file(file, save_path):
    das1 = das.DAS()
    das1.readData(file)
    das1.RawDataBpFilter(0.01, 0.02, 2.0, 2.1)
    data = das1.data[:, 73:-1]
    data = fkFilter(data, 0, 0.1, 1, 1.5, 1)
    print(data.shape)
    scale = 0.001

    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    ax.axis("off")
    ax.imshow(data, cmap='grey', aspect='auto', 
              vmin=-scale, vmax=scale, interpolation='bilinear')
    ax.margins(0)
    # fig.savefig(f'{save_path/file.stem}.png', bbox_inches='tight', pad_inches=0, dpi=40)
    # plt.close()
    plt.show()


def main():
    # dir_path = pathlib.Path('/Volumes/CSIM_LAB/DATA/DAS/govlink/吉大20230720/2023-07-24')
    dir_path = pathlib.Path('/Volumes/CSIM_LAB/DATA/Car-JLU-2024-01-31/ovlink/2024-02-01')
    files = sorted(dir_path.glob('*.dat'))
    save_path = pathlib.Path('2024-02-01-gray-FK')
    
    for file in files:
        process_file(file, save_path)
        break
    
if __name__ == '__main__':
    print('start')
    main()