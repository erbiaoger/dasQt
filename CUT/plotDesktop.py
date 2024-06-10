
import matplotlib.pyplot as plt
import numpy as np
from scipy import io as sio
import h5py


def plotFig(data):
    scale = 50

    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    ax.axis("off")
    ax.imshow(data, cmap='rainbow', aspect='auto', 
              vmin=-scale, vmax=scale, interpolation='bilinear')
    ax.margins(0)
    # fig.savefig(f'{save_path/file.stem}.png', bbox_inches='tight', pad_inches=0, dpi=40)
    # plt.close()
    plt.show()
    
def main():

    # data = sio.loadmat('/Users/zhiyuzhang/Desktop/eq-2.mat')['data']
    with h5py.File('/Users/zhiyuzhang/Desktop/eq-2.mat', 'r') as f:
        key = list(f.keys())
        for k in key:
            print(k)
            data = f[k][()]
            plotFig(data)


    
if __name__ == '__main__':
    main()
    print('end')