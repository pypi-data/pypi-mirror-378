from muse.data_source.file_ds import FileDataSource
from muse.data_source.db_ds import DBDataSource
from muse.data_source.base import DataSourceInterface
from muse.muse_config import DATASOURCE_TYPE

class _DataSourceManager:
    _data_source = None
    def __init__(self):
        if DATASOURCE_TYPE.lower() == 'file':
            self._data_source = FileDataSource()
        else:
            self._data_source = DBDataSource()

    def init_ds(self, ds):
        if isinstance(ds, DataSourceInterface):
            self._data_source = ds
            ds_name = ds.get_datasource_name()
            print(f'加载数据源: "{ds_name}" ...... 成功!')
    def get_ds(self):
        return self._data_source

ds_manager = _DataSourceManager()