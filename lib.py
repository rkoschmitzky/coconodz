import json


class SafeOpen(object):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.f = None

    def __enter__(self):
        try:
            self.f = open(*self.args, **self.kwargs)
            return self.f
        except:
            raise IOError('Could not open %s' % self.args)

    def __exit__(self, *exc_info):
        if self.f:
            self.f.close()


def write_json(filePath, data):
    with SafeOpen(filePath, 'w') as f:
        f.write(json.dumps(data))


def read_json(filePath):
    with SafeOpen(filePath, 'r') as f:
        data = None
        try:
            data = json.loads(f.read())
            return data
        except ValueError:
            return data