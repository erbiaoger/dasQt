import numpy as np

def normalize_data(data):
    """
    归一化数据到指定的范围。

    参数：
    data: 包含数值的列表
    new_min: 新的最小值
    new_max: 新的最大值

    返回值：
    归一化后的数据列表
    """
    # 找到原始数据中的最小值和最大值
    max_values = np.max(np.abs(data), axis=0)
    data_norm = np.zeros(data.shape)
    for i in range(0, data.shape[0]):
        data_norm[i, :] = data[i, :] / max_values
    # 计算归一化后的数据
    return data_norm
