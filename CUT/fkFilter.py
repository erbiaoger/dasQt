import numpy as np
from scipy.fftpack import fft2, ifft2, fftshift, ifftshift

def fkFilter(d, va, vb, vc, vd, pass_flag):
    """
    F-K domain filtering.

    Parameters:
    d : input data, a 2D array with dimensions [nt,nx]
    va, vb, vc, vd : velocities to control the filtering area (va < vb < vc < vd)
    pass_flag : determines the filtering behavior
                1 -> pass frequencies within [vb, vc]
                0 -> pass frequencies outside (va, vd)

    Returns:
    d : output data after F-K domain filtering
    """
    # 获取输入数据的尺寸
    nt, nx = d.shape
    # 计算频率和波数域的采样点数，采用2的幂次方以优化FFT计算速度
    nk = 2 * 2 ** np.ceil(np.log2(nx))
    nf = 2 ** np.ceil(np.log2(nt))
    # 对输入数据进行二维傅里叶变换，并且将变换后的数据中心移动到数组的中心
    m = fftshift(fft2(d, (int(nf), int(nk))))
    # 计算频率和波数的间隔
    dw = 1 / nf
    dk = 1 / nk

    # 定义一个微小的波数以避免除以零
    mink = np.sqrt(2) * dk * 1.19209290e-07

    # 计算频率的一半，用于后面的处理
    nw = int(nf // 2) + 1

    # 初始化滤波后的数据矩阵
    mmd = np.zeros((nw, int(nk)))

    # 遍历所有频率和波数点
    for iw in range(1, nw + 1):
        w = dw * (iw - 1)  # 当前的频率
        for ik in range(1, int(nk) + 1):
            k = -0.5 + (ik - 1) * dk  # 当前的波数
            k = abs(k) + mink  # 确保波数为正且不为零
            vel = w / k  # 计算相速度

            # 根据相速度和给定的速度阈值调整滤波系数
            if vel >= va and vel <= vb:
                fac = 1.0 - np.sin(0.5 * np.pi * (vel - va) / (vb - va))
            elif vel >= vb and vel <= vc:
                fac = 0.0
            elif vel >= vc and vel <= vd:
                fac = np.sin(0.5 * np.pi * (vel - vc) / (vd - vc))
            else:
                fac = 1.0

            if pass_flag:
                fac = 1.0 - fac  # 如果pass_flag为1，则反转滤波系数

            # 应用滤波系数到对应的频率和波数点
            mmd[iw-1, ik-1] = m[iw + nw - 3, ik-1] * fac

    # 将滤波后的数据进行翻转以匹配原始数据的排列
    mmp = np.flip(np.flip(mmd, 0), 1)

    # 将翻转后的数据与原数据合并，完成滤波操作
    m = np.concatenate((mmp[1:nw-1, :], mmd[0:nw, :]), axis=0)

    # 将中心移动回原位置
    m = ifftshift(m)

    # 进行逆傅里叶变换，并只取实部作为最终的滤波结果
    d = np.real(ifft2(m))
    # 裁剪数据以匹配原始输入数据的尺寸
    d = d[0:nt, 0:nx]

    return d


# Example usage:
# dout = fkfilter(d, 0, 0.5, 1, 1.5, 1)


if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt

    # from fkFilter import fkFilter

    # fkFilter(d, va, vb, vc, vd, pass_flag)

    # Create a simple 2D synthetic data
    nt = 100
    nx = 100
    d = np.zeros((nt, nx))
    for it in range(nt//2-10, nt//2+10):
        # for ix in range(nx//2-10, nx//2+10):
        d[it, int(it * 0.2)] = 1



    # Apply F-K domain filtering
    va = 10
    vb = 20
    vc = 30
    vd = 40
    pass_flag = 1
    da = fkFilter(d, va, vb, vc, vd, pass_flag)

    print(d.shape)

    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.imshow(np.abs(d), cmap='gray')
    ax1.set_title('Original')
    ax2.imshow(np.abs(da), cmap='gray')
    ax2.set_title('Filtered')
    plt.show()
