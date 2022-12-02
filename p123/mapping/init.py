import p123.data.validate as validation
import utils.misc as misc
import functools


MAIN = {
    'Operation': {
        'required': True
    },
    'On Error': {
        'isValid': functools.partial(validation.from_mapping, mapping=('stop', 'continue'))
    },
    'Precision': {
        'isValid': functools.partial(validation.from_mapping_any, mapping=(2, 3, 4))
    }
}

REQ_CONTEXT = {
    'Engine': {
        'field': 'engine',
        'isValid': functools.partial(validation.from_mapping, mapping=('legacy', 'current'))
    },
    'Vendor': {
        'field': 'vendor',
        'isValid': functools.partial(validation.from_mapping, mapping=('factset', 'compustat'))
    },
    'PIT Method': {
        'field': 'pitMethod',
        'isValid': functools.partial(validation.from_mapping,
                                     mapping=('prelim', 'complete', 'formula', 'factor', 'exclude'))
    },
    'Rank Mon': {
        'field': 'rankMon',
        'isValid': misc.is_str
    }
}

SETTINGS = {
    'Type': {
        'isValid': functools.partial(validation.from_mapping, mapping=('stock', 'etf'))
    }
}
SETTINGS.update(REQ_CONTEXT)

ITERATIONS = {
    'Name': {
        'isValid': misc.is_str
    }
}
ITERATIONS.update(REQ_CONTEXT)
