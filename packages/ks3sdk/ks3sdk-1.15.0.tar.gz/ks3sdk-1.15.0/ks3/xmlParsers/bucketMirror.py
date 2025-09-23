# -*- coding: utf-8 -*-
from ks3.responseResult import ResponseMetadata


class BucketMirror(object):
    def __init__(self, use_default_robots=None, async_mirror_rule=None, sync_mirror_rules=None, *args, **kwargs):
        self.version = "V3"
        self.use_default_robots = use_default_robots
        self.async_mirror_rule = async_mirror_rule
        self.sync_mirror_rules = sync_mirror_rules

        self.response_metadata = ResponseMetadata(**kwargs)

    def keys(self):
        return ('version', 'use_default_robots', 'async_mirror_rule', 'sync_mirror_rules')

    def __getitem__(self, item):
        if item == 'async_mirror_rule':
            rule = dict(getattr(self, item))
            if rule.get('mirror_type') is None:
               rule.pop('mirror_type')
            return rule
        if item == 'sync_mirror_rules':
            rules_dict = []
            for value in getattr(self, item):
                rule = dict(value)
                if rule.get('mirror_type') is None:
                    rule.pop('mirror_type')
                rules_dict.append(rule)
            return rules_dict
        return getattr(self, item)


class SavingSetting(object):
    def __init__(self, acl=None):
        self.acl = acl


class AsyncMirrorRule(object):
    def __init__(self, mirror_urls=None, saving_setting=None, mirror_type=None):
        if mirror_urls is None:
            mirror_urls = []
        self.mirror_urls = mirror_urls
        self.saving_setting = saving_setting
        self.mirror_type = mirror_type

    @classmethod
    def rule_with_acl(cls, mirror_urls=None, saving_setting_acl=None, mirror_type=None):
        if mirror_urls is None:
            mirror_urls = []
        saving_setting = SavingSetting(acl=saving_setting_acl)
        return cls(mirror_urls=mirror_urls, saving_setting=saving_setting, mirror_type=mirror_type)

    def keys(self):
        return 'mirror_urls', 'saving_setting', 'mirror_type'

    def __getitem__(self, item):
        if item == 'saving_setting':
            return getattr(self, item).__dict__
        return getattr(self, item)


class SyncMirrorRules(object):
    def __init__(self, match_condition=None, mirror_url=None, mirror_request_setting=None, saving_setting=None, mirror_type=None):
        self.saving_setting = saving_setting
        self.mirror_request_setting = mirror_request_setting
        self.mirror_url = mirror_url
        self.match_condition = match_condition
        self.mirror_type = mirror_type

    @classmethod
    def rules_with_prefix_acl(cls, key_prefixes=None, mirror_url=None, mirror_request_setting=None, saving_setting_acl=None, mirror_type=None):
        saving_setting = SavingSetting(acl=saving_setting_acl)
        match_condition = MatchCondition(key_prefixes=key_prefixes)
        return cls(match_condition=match_condition, mirror_url=mirror_url, mirror_request_setting=mirror_request_setting, saving_setting=saving_setting, mirror_type=mirror_type)

    def keys(self):
        return 'saving_setting', 'mirror_request_setting', 'mirror_url', 'match_condition', 'mirror_type'

    def __getitem__(self, item):
        if item == 'mirror_request_setting':
            return dict(getattr(self, item))
        if item == 'saving_setting' or item == 'match_condition':
            return getattr(self, item).__dict__
        return getattr(self, item)

class MirrorRequestSetting(object):
    def __init__(self, pass_query_string=None, follow3xx=None, header_setting=None):
        self.pass_query_string = pass_query_string
        self.follow3xx = follow3xx
        self.header_setting = header_setting

    def keys(self):
        return ('pass_query_string', 'follow3xx', 'header_setting')

    def __getitem__(self, item):
        if item == 'header_setting':
            return dict(getattr(self, item))
        return getattr(self, item)

class HeaderSetting(object):
    def __init__(self, set_headers=None, remove_headers=None, pass_all=None, pass_headers=None):
        if pass_headers is None:
            pass_headers = []
        if remove_headers is None:
            remove_headers = []
        if set_headers is None:
            set_headers = []
        self.set_headers = set_headers
        self.remove_headers = remove_headers
        self.pass_all = pass_all
        self.pass_headers = pass_headers

    def keys(self):
        return ('set_headers', 'remove_headers', 'pass_all', 'pass_headers')

    def __getitem__(self, item):
        return getattr(self, item)

# 回源条件
class MatchCondition(object):
    def __init__(self, http_codes=None, key_prefixes=""):
        if http_codes is None:
            http_codes = ["404"]
        self.http_codes = http_codes
        self.key_prefixes = key_prefixes