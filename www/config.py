# -*- coding:utf-8 -*-
'Configuration'
__autor__ = 'ZAM';

import config_default;

class Dict(dict):
    def __init__(self, name = (), value = (), **kw):
        Super(Dict, self).__init__(**kw);
        for k,v in zip(name, value):
            self[k] = v;
    
    def __getattr__(self, key):
        try:
            return self[key];
        except KeyError:
            raise AttributeError(r'\'Dict\' object has no attribute \'%s\''%(key));
    
    def __setattr__(self, key, value):
        self[key] = value;

def Merge(defaults, override):
    r = {};
    for k, v in defaults.items():
        if k in override:
            if isinstance(v, dict):
                r[k] = Merge(v, override[k]);
            else:
                r[k] = override[k];
        else:
            r[k] = v;
    return r;

def ToDict(d):
    D = Dict();
    for k, v in d.items():
        D[k] = ToDict(v) if isinstance(v, dict) else v;
    return D;

configs = config_default.configs;
try:
    import config_override;
    configs = Merge(configs, config_override.configs);
except ImportError:
    pass;
configs = ToDict(configs);
