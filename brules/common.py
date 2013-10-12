from collections import MutableMapping
from future.utils.six import text_type
from functools import partial

# ''.format_map() in Python 2.x
# from https://gist.github.com/zed/1384338
try:
    ''.format_map({})
except AttributeError:  # Python < 3.2
    import string

    def format_map(format_string, mapping, _format=string.Formatter().vformat):
        return _format(format_string, None, mapping)
    del string

    import ctypes as c

    class PyObject_HEAD(c.Structure):
        _fields_ = [
            ('HEAD', c.c_ubyte *
             (object.__basicsize__ - c.sizeof(c.c_void_p))),
            ('ob_type', c.c_void_p)
        ]

    _get_dict = c.pythonapi._PyObject_GetDictPtr
    _get_dict.restype = c.POINTER(c.py_object)
    _get_dict.argtypes = [c.py_object]

    def get_dict(obj):
        return _get_dict(obj).contents.value

    get_dict(str)['format_map'] = format_map
else:  # Python 3.2+
    def format_map(format_string, mapping):
        return format_string.format_map(mapping)


class UnmatchedStepError(Exception):

    def __init__(self, *args):
        super(UnmatchedStepError, self).__init__(*args)
        self.line = self.args[0]


class Context(MutableMapping):

    def __init__(self, *args, **kwargs):
        self._data_provider = kwargs.pop('data_provider', None)
        self._data = dict(*args, **kwargs)
        self._data_points = None

    def get_data_points(self):
        if self._data_points is None:
            if self._data_provider is not None:
                data_points = self._data_provider.get_data_points()
            else:
                data_points = {}
            for key in self._data:
                data_points[key] = partial(self._get_data_point, key)
            self._data_points = data_points

        return self._data_points.copy()

    # pylint: disable=W0613
    def _get_data_point(self, key, context):
        return self._data[key]

    def __eq__(self, other):
        return self._data == other

    def to_dict(self, recurse=False):
        if recurse:
            return {k: v(self) for k, v in self.get_data_points().items()}
        else:
            return self._data

    def __getitem__(self, key):
        try:
            return self._data[key]
        except KeyError:
            if self._data_provider is None:
                raise

        data_point_fn = self._data_provider.get_data_points()[key]
        value = self[key] = data_point_fn(self)
        return value

    def __setitem__(self, key, value):
        self._data_points = None
        self._data[key] = value

    def __delitem__(self, key):
        self._data_points = None
        del self._data[key]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError("'{}' object has no attribute '{}'".format(
                self.__class__.__name__, name))

    def __setattr__(self, name, value):
        if name.startswith('_') or name in self.__dict__:
            self.__dict__['_data_points'] = None
            self.__dict__[name] = value
        else:
            self[name] = value

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self._data)


def combined_match_dict(match):
    match_dict = Context(match.groupdict())
    match_dict.update(enumerate(match.groups(), start=1))
    return match_dict


def u(bytes_or_str):
    if not isinstance(bytes_or_str, text_type):
        return bytes_or_str.decode('utf-8')
    return bytes_or_str
