from prettytable import PrettyTable

class URLMapping(object):
    __slots__ = (
        'url', 'method', 'headers', 'response', 'type'
    )

    def __init__(self, data):
        for attr, value in data.items():
            if callable(value):
                setattr(self, attr, value())
            else:
                setattr(self, attr ,value)
        
        for value in self.__slots__:
            if not getattr(self, value, None):
                if value == 'method':
                    setattr(self, value, 'GET')
                if value == 'response':
                    setattr(self, value, 'json')
                if value == 'headers':
                    setattr(self, value, {})
                if value == 'type':
                    setattr(self, value, 'default')

    def __str__(self):
        return str(type(self)) + ' '.join([
            "{attr}:{val}".format(attr=value, val=getattr(self, value)) for value in self.__slots__])

    __repr__ = __str__


