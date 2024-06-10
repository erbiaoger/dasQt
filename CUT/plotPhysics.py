import sys
sys.path.insert(0, '../')
import pathlib
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio

import matplotlib
matplotlib.use('Agg')  # 使用非 GUI 后端

from dasQt import das

# 定义处理单个文件的函数
def process_file(file, save_path):

    all = sio.loadmat(file)

    # d_bp = all['d_bp']
    # d_fk = all['d_fk2'].T
    d_curvelet = all['d_curvelet'].T
    data = d_curvelet

    scale = 0.001

    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    ax.axis("off")
    ax.imshow(data, cmap='RdBu', aspect='auto', 
              vmin=-scale, vmax=scale, interpolation='bilinear')
    ax.margins(0)
    fig.savefig(f'{save_path/file.stem}.png', bbox_inches='tight', pad_inches=0, dpi=1000)
    plt.close()

def main():
    dir_path = pathlib.Path('/Users/zhiyuzhang/MyProjects/dasQt/utools')
    files = sorted(dir_path.glob('*.mat'))
    print(len(files), 'files')

    save_path = pathlib.Path('/Users/zhiyuzhang/MyProjects/dasQt/CUT/physics_fig')
    save_path.mkdir(parents=True, exist_ok=True)
    for file in files:
        process_file(file, save_path)
        

if __name__ == '__main__':
    print('start')
    main()
    print('end')