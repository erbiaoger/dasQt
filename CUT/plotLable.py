
import sys
sys.path.insert(0, '../')
import pathlib
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor

import matplotlib
matplotlib.use('Agg')  # 使用非 GUI 后端
from scipy import io as sio

# 定义处理单个文件的函数
def process_file(file, save_path):

    a = sio.loadmat(file)
    # print(a.keys())
    data = a['data2']
    name = str(save_path/pathlib.Path(file).stem) + '.png'

    scale = 0.001

    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    ax.axis("off")
    ax.imshow(data, cmap='rainbow', aspect='auto', 
              vmin=-scale, vmax=scale, interpolation='bilinear')
    ax.margins(0)
    fig.savefig(name, bbox_inches='tight', pad_inches=0, dpi=1000)
    plt.close()



def main():
    dir_path = pathlib.Path('/Users/zhiyuzhang/Desktop/new2/')
    file_list = [str(file) for file in sorted(dir_path.glob('*.mat'))]

    out_file_names = [
        line for line in file_list if '-out' in line
    ]
    without_out_file_names = [
        line for line in file_list if '-out' not in line
    ]
    files = without_out_file_names
    # files = out_file_names


    save_path = pathlib.Path('/Users/zhiyuzhang/Desktop/new_rainbow/trainB')
    save_path.mkdir(parents=True, exist_ok=True)

    with ProcessPoolExecutor(max_workers=4) as executor:
        for file in files:
            executor.submit(process_file, file, save_path)
            # break


if __name__ == '__main__':
    print('start')
    main()
