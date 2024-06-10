import sys
sys.path.insert(0, '../')
import pathlib
from concurrent.futures import ProcessPoolExecutor
from scipy import io as sio

from dasQt import das

# 定义处理单个文件的函数
def process_file(file, save_path):
    das1 = das.DAS()
    das1.readData(file)
    # das1.RawDataBpFilter(0.01, 0.02, 2.0, 2.1)
    data = das1.data[:, 73:-1]
    dx = das1.dx
    dt = das1.dt

    sio.savemat(f'{save_path/file.stem}.mat', {'data': data, 'dx': dx, 'dt': dt})


def main():
    # dir_path = pathlib.Path('/Volumes/CSIM_LAB/DATA/DAS/govlink/吉大20230720/2023-07-24')
    dir_path = pathlib.Path('/Volumes/CSIM_LAB/DATA/Car-JLU-2024-01-31/ovlink/2024-01-31')
    files = sorted(dir_path.glob('*.dat'))[100:]
    print(len(files), 'files')

    save_path = pathlib.Path('2024-01-31-mat')
    save_path.mkdir(parents=True, exist_ok=True)

    with ProcessPoolExecutor(max_workers=4) as executor:
        for file in files:
            executor.submit(process_file, file, save_path)
            # break


if __name__ == '__main__':
    print('start')
    main()
