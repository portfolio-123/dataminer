import p123.data.validate as validation
import p123.data.transform as transform
import p123.mapping.init as init
import p123.data.cons as cons
import utils.misc as misc
import functools


FREQ = {item['label']: item['value'] for item in cons.FREQ[1:]}
SETTINGS = {
    'Start Date': {
        'field': 'startDt',
        'isValid': validation.date,
        'transform': transform.date,
        'required': True
    },
    'End Date': {
        'field': 'endDt',
        'isValid': validation.date,
        'transform': transform.date
    },
    'Frequency': {
        'field': 'frequency',
        'isValid': functools.partial(validation.from_mapping, mapping=FREQ),
        'transform': functools.partial(transform.from_mapping, mapping=FREQ)
    },
    'P123 UIDs': {
        'field': 'p123Uids',
        'isValid': validation.data_p123_uids,
        'transform': transform.data_items
    },
    'Tickers': {
        'field': 'tickers',
        'isValid': validation.data_tickers_cusips,
        'transform': transform.data_items
    },
    'Cusips': {
        'field': 'cusips',
        'isValid': validation.data_tickers_cusips,
        'transform': transform.data_items
    },
    'Gvkeys': {
        'field': 'gvkeys',
        'isValid': validation.data_tickers_cusips,
        'transform': transform.data_items
    },
    'Ciks': {
        'field': 'ciks',
        'isValid': validation.data_tickers_cusips,
        'transform': transform.data_items
    },
    'Formulas': {
        'isValid': validation.data_univ_formulas,
        'required': True
    },
    'Include Names': {
        'field': 'includeNames',
        'isValid': misc.is_bool
    },
    'Currency': {
        'field': 'currency',
        'isValid': validation.currency
    },
    'Region': {
        'field': 'region',
        'isValid': misc.is_str
    },
    'Ignore Errors': {
        'field': 'ignoreErrors',
        'isValid': misc.is_bool
    }
}
SETTINGS.update(init.SETTINGS)

UNIVERSE_SETTINGS = {
    'Start Date': {
        'isValid': validation.date,
        'transform': transform.date,
        'required': True
    },
    'End Date': {
        'isValid': validation.date,
        'transform': transform.date
    },
    'Frequency': {
        'isValid': functools.partial(
            validation.from_mapping, mapping={item['label']: item['value'] for item in cons.FREQ[1:]})
    },
    'Universe': {
        'field': 'universe',
        'isValid': validation.universe,
        'transform': transform.universe,
        'required': True
    },
    'Formulas': {
        'isValid': validation.data_univ_formulas,
        'required': True
    },
    'Include Names': {
        'field': 'includeNames',
        'isValid': misc.is_bool
    },
    'Currency': {
        'field': 'currency',
        'isValid': validation.currency
    }
}
UNIVERSE_SETTINGS.update(init.SETTINGS)
