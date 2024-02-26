import logging.config


import os
import logging

class Logger():
    def __init__(self, fname=None, path="./"):
        self.logger = self.log_init(fname, path)
        

    def log_init(fname=None, path="./"):
        """ 初始化日志器 """
        cur_dir = os.path.dirname(os.path.abspath(fname))
        file_basename = fname.split('/')[-1]
        log_file = "{}.log".format(file_basename)
    
        
        formatter = logging.Formatter(
            f'%(asctime)s %(levelname)s\t{file_basename}: %(lineno)d\t%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')

        # 读取日志配置文件内容
        logging.config.fileConfig('logging.conf')
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



# 将日志打印在控制台
logger.debug('打印日志级别：debug')
logger.info('打印日志级别：info')
logger.warning('打印日志级别：warning')
logger.error('打印日志级别：error')
logger.critical('打印日志级别：critical')