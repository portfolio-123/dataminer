import p123.data.validate as validation
import p123.data.transform as transform
import p123.data.cons as cons
import p123.mapping.init as mapping_init
import utils.misc as misc
import functools

RANKS_COMMON = {
    'Ranking System': {
        'field': 'rankingSystem',
        'isValid': validation.ranking_system,
        'transform': transform.screen_ranking,
        'required': True
    },
    'Universe': {
        'field': 'universe',
        'isValid': validation.universe,
        'transform': transform.universe
    },
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
    'Include Names': {
        'field': 'includeNames',
        'isValid': misc.is_bool
    },
    'Transaction Type': {
        'field': 'transType',
        'isValid': functools.partial(validation.from_mapping, mapping=cons.RANK_PERF_METHOD)
    },
    'Ranking Method': {
        'field': 'rankingMethod',
        'isValid': functools.partial(validation.from_mapping, mapping=cons.RANKING_METHOD),
        'transform': functools.partial(transform.from_mapping, mapping=cons.RANKING_METHOD)
    },
    # 'Industry': {
    #     'field': 'industry',
    #     'isValid': misc.is_str
    # },
    'Tickers': {
        'field': 'tickers',
        'isValid': misc.is_str
    },
    'Columns': {
        'isValid': functools.partial(validation.from_mapping, mapping=['ranks', 'composite', 'factor'])
    }
}
RANKS_COMMON.update(mapping_init.SETTINGS)

RANKS = RANKS_COMMON.copy()
RANKS['Additional Data'] = {
    'isValid': validation.data_univ_formulas
}
RANKS['Currency'] = {
    'field': 'currency',
    'isValid': validation.currency
}

RANKS_PERIOD = RANKS_COMMON.copy()
del RANKS_PERIOD['Columns']


RANKS_MULTI_SETTINGS = RANKS_COMMON.copy()
del RANKS_MULTI_SETTINGS['Start Date'], RANKS_MULTI_SETTINGS['End Date'], RANKS_MULTI_SETTINGS['Frequency'],\
    RANKS_MULTI_SETTINGS['Ranking System'], RANKS_MULTI_SETTINGS['Ranking Method'], RANKS_MULTI_SETTINGS['Columns']
RANKS_MULTI_SETTINGS['As of Date'] = {
    'field': 'asOfDt',
    'isValid': validation.date,
    'transform': transform.date,
    'required': True
}
RANKS_MULTI_ITERATIONS = mapping_init.ITERATIONS.copy()
RANKS_MULTI_ITERATIONS['Ranking System'] = RANKS_COMMON['Ranking System']
RANKS_MULTI_ITERATIONS['Ranking Method'] = RANKS_COMMON['Ranking Method']
