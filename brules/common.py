class UnmatchedStepError(Exception):
    pass


class AttrDict(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError("'{}' object has no attribute '{}'".format(
                self.__class__.__name__, name))

    def __setattr__(self, name, value):
        self[name] = value


def combined_match_dict(match):
    match_dict = AttrDict(match.groupdict())
    match_dict.update(enumerate(match.groups(), start=1))
    return match_dict
