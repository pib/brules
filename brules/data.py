import inspect


class Provider(object):
    def get_data_points(self):
        return {val.key: val
                for key, val in inspect.getmembers(self, inspect.ismethod)
                if hasattr(val, 'is_data_point')}

    @staticmethod
    def data_point(key=None, name=None, doc=None):
        def fill_in(fn):
            fn.key = key or fn.__name__
            fn.name = name or fn.key
            fn.doc = doc or fn.__doc__
            fn.is_data_point = True
            return fn

        if callable(key):
            fn, key = key, None
            return fill_in(fn)

        return fill_in

    @staticmethod
    def data_point_class(key=None, name=None, doc=None):
        """ Construct a Provider instance with a single data point
        provided by the passed-in function
        """

        provider = Provider()

        decorate = Provider.data_point(key, name, doc)

        def make(fn):
            if decorate != fn:
                fn = decorate(fn)

            setattr(provider, fn.key, fn)
            return provider

        if callable(key):
            return make(decorate)

        return make
