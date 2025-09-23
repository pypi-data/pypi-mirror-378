import pathlib
import os

def get_env_variable(name, default=None):
    """安全地获取环境变量"""
    value = os.environ.get(name)
    if value is None:
        if default is None:
            raise ValueError(f"环境变量 {name} 未设置")
        return default
    return value

# MUSE所至目录
APP_LOCATE = str(pathlib.Path(os.path.abspath(__file__)).parent)
# DS的类型
DATASOURCE_TYPE = get_env_variable('MUSE_DATASOURCE_TYPE', 'FILE')
# 本地文件地址
DATA_PATH = get_env_variable('MUSE_FILE_LOCATE', APP_LOCATE + '/data')
# 数据中台地址
MID_BASE_URL = get_env_variable('MUSE_MID_BASE_URL', 'http://jixunet.top/jxdm_zyrisk')
# 数据中台资产标签组名称
ASSET_TAG_GROUP = get_env_variable('MUSE_ASSET_TAG_GROUP', "压测标签组")
# 数据中台产品标签组名称
PORT_TAG_GROUP = get_env_variable('MUSE_PORT_TAG_GROUP', "限额指标产品标签组")
# 数据中台指标库父级名称，可使用逗号表示多个开放的指标库
REPOSITORY_GROUP = get_env_variable('MUSE_REPOSITORY_GROUP', "API指标库")

if __name__ == '__main__':
    print(DATASOURCE_TYPE)
    print(DATA_PATH)
    print(MID_BASE_URL)
    print(ASSET_TAG_GROUP)
    print(PORT_TAG_GROUP)
    print(REPOSITORY_GROUP)