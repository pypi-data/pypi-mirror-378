import importlib
import pathlib

class Formatter:
    def __init__(self, name, get_default_config, make):
        self.name = name
        self._get_default_config = get_default_config
        self._make = make
        
    def get_default_config(self):
        return self._get_default_config()
    
    def make(self, model_by_name, metadata_by_element, out_dir, user_config=None):
        config = self.get_default_config()
        config.update(user_config or {})
        self._make(model_by_name, metadata_by_element, out_dir / self.name, config)

    
_FORMATTER_BY_NAME = None
    
# TODO: rename
def get_formatter_by_name():
    global _FORMATTER_BY_NAME
    if _FORMATTER_BY_NAME is None:
        temp_retval = {}
        from . import formatters
        formatters_dir = pathlib.Path(formatters.__path__[0])
        for dir_entry in formatters_dir.iterdir():
            if dir_entry.is_dir():
                module_name = dir_entry.name
            elif dir_entry.is_file() and dir_entry.suffixes == ['.py']:
                module_name = dir_entry.name[:-3]
            else:
                continue
            module = importlib.import_module(f'.{module_name}', formatters.__name__)
            formatter = getattr(module, 'FORMATTER', None)
            if formatter:
                assert isinstance(formatter, Formatter)
                assert formatter.name not in temp_retval
                temp_retval[formatter.name] = formatter
        _FORMATTER_BY_NAME = temp_retval
    return _FORMATTER_BY_NAME
