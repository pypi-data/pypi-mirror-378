from ks3.responseResult import ResponseMetadata


class VpcAccessBlock:
    def __init__(self, rules=None, *args, **kwargs):
        if rules is None:
            rules = []
        self.rules = rules

        self.response_metadata = ResponseMetadata(**kwargs)

    def startElement(self, name, attrs, connection):
        if name == 'Rule':
            self.rules.append(Rule())
            return self.rules[-1]
        return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)

    def to_xml(self):
        s = u'<VpcAccessBlockConfiguration>'
        for i in self.rules:
            s += i.to_xml()
        s += '</VpcAccessBlockConfiguration>'
        return s


class Rule:
    def __init__(self, rule_id=None, region=None, vpc_ids=None, allow_access_buckets=None, enabled=None):
        if vpc_ids is None:
            vpc_ids = []
        if allow_access_buckets is None:
            allow_access_buckets = []

        self.rule_id = rule_id
        self.region = region
        self.vpc_ids = vpc_ids
        self.allow_access_buckets = allow_access_buckets
        self.enabled = enabled

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'RuleID':
            self.rule_id = value
        elif name == 'Region':
            self.region = value
        elif name == 'ID':
            self.vpc_ids.append(value)
        elif name == 'Name':
            self.allow_access_buckets.append(value)
        elif name == 'Status':
            self.enabled = True if value.lower() == 'enabled' else False
        else:
            setattr(self, name, value)

    def to_xml(self):
        s = u'<Rule>'
        if self.rule_id is not None:
            s += '<RuleID>{0}</RuleID>'.format(self.rule_id)
        if self.region is not None:
            s += '<Region>{0}</Region>'.format(self.region)
        if self.vpc_ids is not None and len(self.vpc_ids) > 0:
            s += '<VPC>'
            for i in self.vpc_ids:
                s += '<ID>{0}</ID>'.format(i)
            s += '</VPC>'
        if self.allow_access_buckets is not None and len(self.allow_access_buckets) > 0:
            s += '<BucketAllowAccess>'
            for i in self.allow_access_buckets:
                s += '<Name>{0}</Name>'.format(i)
            s += '</BucketAllowAccess>'
        if self.enabled is not None:
            s += '<Status>{0}</Status>'.format('Enabled' if self.enabled else 'Disabled')
        s += '</Rule>'
        return s