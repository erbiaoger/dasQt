import os
import logging

"""
    * @file: logPy.py
    * @version: v1.0.0
    * @author: Zhiyu Zhang
    * @desc: 
    * @date: 2024-01-05 20:28:32
    * @Email: erbiaoger@gmail.com
    * @url: erbiaoger.site

"""



class Logger():
    def __init__(self, fname=None, path="./"):
        self.logger = self.log_init(fname, path)

    def log_init(self, fname=None, path="./"):
        """ 初始化日志器 """
        cur_dir = os.path.dirname(os.path.abspath(fname))
        file_basename = fname.split('/')[-1]
        log_file = "{}.log".format(file_basename)
        
        formatter = logging.Formatter(
            f'%(asctime)s %(levelname)s\t{file_basename}: %(lineno)d\t%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')

        logger = logging.getLogger(fname)    # 创建日志器logger并命名
        logger.setLevel(logging.DEBUG)

        fileHandler = logging.FileHandler(os.path.join(path, log_file), mode='w')
        fileHandler.setLevel(logging.DEBUG)
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.DEBUG)

        consoleHandler.setFormatter(formatter)
        fileHandler.setFormatter(formatter)

        logger.addHandler(fileHandler)
        logger.addHandler(consoleHandler)

        return logger


if __name__ == "__main__":
    logger = log_init(fname=__file__)
    for i in range(10):
        # logger.debug(f"test {i:02d}")
        # logger.info(f"test {i:02d}")
        logger.warning(f"test {i:02d}")
        # logger.error(f"test {i:02d}")
        # logger.critical(f"test {i:02d}")
        