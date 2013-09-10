from future.utils.six import text_type


class UnmatchedStepError(Exception):
    pass


class Context(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError("'{}' object has no attribute '{}'".format(
                self.__class__.__name__, name))

    def __setattr__(self, name, value):
        self[name] = value


def combined_match_dict(match):
    match_dict = Context(match.groupdict())
    match_dict.update(enumerate(match.groups(), start=1))
    return match_dict


def u(bytes_or_str):
    if not isinstance(bytes_or_str, text_type):
        return bytes_or_str.decode('utf-8')
    return bytes_or_str
