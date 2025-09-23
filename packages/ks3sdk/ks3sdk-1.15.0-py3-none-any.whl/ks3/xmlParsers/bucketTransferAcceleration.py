from ks3.responseResult import ResponseMetadata


class BucketTransferAcceleration:

    def __init__(self, enabled=None, *args, **kwargs):
        self.enabled = 'true' if enabled else 'false'

        self.response_metadata = ResponseMetadata(**kwargs)

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'Enabled':
            self.enabled = value
        setattr(self, name, value)

    def to_xml(self):
        s = u'<TransferAccelerationConfiguration>'
        if self.enabled is not None:
            s += '<Enabled>%s</Enabled>' % self.enabled
        s += '</TransferAccelerationConfiguration>'
        return s