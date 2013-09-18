from collections import MutableMapping
from future.utils.six import text_type


class UnmatchedStepError(Exception):
    pass


class Context(MutableMapping):
    def __init__(self, *args, **kwargs):
        self._data = dict(*args, **kwargs)
        self.__dict__['data_provider'] = None

    def __eq__(self, other):
        return self._data == other

    def to_dict(self):
        return self._data

    def __getitem__(self, key):
        try:
            return self._data[key]
        except KeyError:
            if self.data_provider is None:
                raise

        data_point_fn = self.data_provider.get_data_points()[key]
        value = self[key] = data_point_fn(self)
        return value

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
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
            self.__dict__[name] = value
        else:
            self[name] = value

    def copy(self):
        new_inst = self.__class__()
        new_inst.update(self._data.copy())
        return new_inst


def combined_match_dict(match):
    match_dict = Context(match.groupdict())
    match_dict.update(enumerate(match.groups(), start=1))
    return match_dict


def u(bytes_or_str):
    if not isinstance(bytes_or_str, text_type):
        return bytes_or_str.decode('utf-8')
    return bytes_or_str
