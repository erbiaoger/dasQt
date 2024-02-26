import logging.config
import logging
import yaml
import logging.config

import os
import pathlib
import logging

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


        # 读取日志配置文件内容
        yml_path = pathlib.Path(__file__).parent.absolute()/'logging.yml'
        with open(yml_path, 'r') as file_logging:
            dict_conf = yaml.load(file_logging, Loader=yaml.FullLoader)
        logging.config.dictConfig(dict_conf)

        logger = logging.getLogger(fname)    # 创建日志器logger并命名
        # logger.setLevel(logging.DEBUG)

        fileHandler = logging.FileHandler(os.path.join(path, log_file), mode='w')
        # fileHandler.setLevel(logging.DEBUG)
        consoleHandler = logging.StreamHandler()
        # consoleHandler.setLevel(logging.DEBUG)

        consoleHandler.setFormatter(formatter)
        fileHandler.setFormatter(formatter)

        logger.addHandler(fileHandler)
        logger.addHandler(consoleHandler)

        return logger


