from ks3.responseResult import ResponseMetadata


class BucketDataRedundancySwitch:
    def __init__(self, data_redundancy_type=None, switch_time=None, *args, **kwargs):
        self.data_redundancy_type = data_redundancy_type
        self.switch_time = switch_time

        self.response_metadata = ResponseMetadata(**kwargs)

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'DataRedundancyType':
            self.data_redundancy_type = value
        if name == 'SwitchTime':
            self.switch_time = value
        setattr(self, name, value)

    def to_xml(self):
        s = u'<BucketDataRedundancySwitch>'
        if self.data_redundancy_type is not None:
            s += '<DataRedundancyType>%s</DataRedundancyType>' % self.data_redundancy_type
        if self.switch_time is not None:
            s += '<SwitchTime>%s</SwitchTime>' % self.switch_time
        s += '</BucketDataRedundancySwitch>'
        return s