import p123.data.validate as validation
import p123.data.transform as transform
import p123.data.cons as cons
import p123.mapping.init as init
import utils.misc as misc
import functools


SCREEN = {
    'Rules': {
        'field': 'rules',
        'isValid': validation.screen_rules,
        'type': 'screen',
        'transform': transform.screen_rules
    },
    'Long Rules': {
        'field': 'rules',
        'isValid': validation.screen_rules,
        'type': 'screen',
        'transform': transform.screen_long_rules
    },
    'Short Rules': {
        'field': 'rules',
        'isValid': validation.screen_rules,
        'type': 'screen',
        'transform': transform.screen_short_rules
    },
    'Hedge Rules': {
        'field': 'rules',
        'isValid': validation.screen_rules,
        'type': 'screen',
        'transform': transform.screen_hedge_rules
    },
    'Method': {
        'field': 'method',
        'isValid': functools.partial(validation.from_mapping, mapping=cons.SCREEN_METHOD),
        'type': 'screen',
        'transform': functools.partial(transform.from_mapping, mapping=cons.SCREEN_METHOD)
    },
    'Max Num Holdings': {
        'field': 'maxNumHoldings',
        'isValid': misc.is_int,
        'type': 'screen'
    },
    'Benchmark': {
        'field': 'benchmark',
        'isValid': misc.is_str,
        'type': 'screen'
    },
    'Universe': {
        'field': 'universe',
        'isValid': validation.universe,
        'type': 'screen',
        'transform': transform.universe
    },
    'Ranking': {
        'field': 'ranking',
        'isValid': validation.screen_ranking,
        'type': 'screen',
        'transform': transform.screen_ranking
    },
    'Currency': {
        'field': 'currency',
        'isValid': validation.currency,
        'type': 'screen'
    }
}

SCREEN_RUN = {
    'Screen': {
        'type': 'screen',
        'field': 'screen',
        'isValid': misc.is_int
    },
    'As of Date': {
        'field': 'asOfDt',
        'isValid': validation.date,
        'transform': transform.date,
        'required': True
    },
    'End Date': {
        'field': 'endDt',
        'isValid': validation.date,
        'transform': transform.date
    }
}
SCREEN_RUN.update(SCREEN)

SCREEN_RUN_SETTINGS = init.SETTINGS.copy()
SCREEN_RUN_SETTINGS.update(SCREEN_RUN)

SCREEN_BACKTEST_SHARED = {
    'Screen': {
        'type': 'screen',
        'field': 'screen',
        'isValid': misc.is_int
    },
    'Trans Price': {
        'field': 'transPrice',
        'isValid': functools.partial(validation.from_mapping, mapping=cons.SCREEN_ROLLING_BACKTEST_TRANS_PRICE),
        'transform': functools.partial(transform.from_mapping, mapping=cons.SCREEN_ROLLING_BACKTEST_TRANS_PRICE)
    },
    'Max Pos Pct': {
        'field': 'maxPosPct',
        'isValid': misc.is_number
    },
    'Slippage': {
        'field': 'slippage',
        'isValid': misc.is_number
    },
    'Long Weight': {
        'field': 'longWeight',
        'isValid': misc.is_number
    },
    'Short Weight': {
        'field': 'shortWeight',
        'isValid': misc.is_number
    },
    'Start Date': {
        'field': 'startDt',
        'isValid': validation.date,
        'transform': transform.date
    },
    'End Date': {
        'field': 'endDt',
        'isValid': validation.date,
        'transform': transform.date
    }
}

SCREEN_ROLLING_BACKTEST = {
    'Frequency': {
        'field': 'frequency',
        'isValid': functools.partial(validation.from_mapping, mapping=cons.SCREEN_ROLLING_BACKTEST_FREQ),
        'transform': functools.partial(transform.from_mapping, mapping=cons.SCREEN_ROLLING_BACKTEST_FREQ)
    },
    'Holding Period': {
        'field': 'holdingPeriod',
        'isValid': validation.screen_rolling_backtest_holding_period
    }
}
SCREEN_ROLLING_BACKTEST.update(SCREEN_BACKTEST_SHARED)

SCREEN_BACKTEST = {
    'Rank Tolerance': {
        'field': 'rankTolerance',
        'isValid': misc.is_number
    },
    'Carry Cost': {
        'field': 'carryCost',
        'isValid': misc.is_number
    },
    'Rebalance Frequency': {
        'field': 'rebalFreq',
        'isValid': functools.partial(validation.from_mapping, mapping=cons.SCREEN_BACKTEST_FREQ),
        'transform': functools.partial(transform.from_mapping, mapping=cons.SCREEN_BACKTEST_FREQ)
    },
    'Risk Stats Period': {
        'field': 'riskStatsPeriod',
        'isValid': functools.partial(validation.from_mapping, mapping=('monthly', 'weekly', 'daily'))
    }
}
SCREEN_BACKTEST.update(SCREEN_BACKTEST_SHARED)

SCREEN_BACKTEST_SETTINGS = init.SETTINGS.copy()
SCREEN_BACKTEST_SETTINGS.update(SCREEN_BACKTEST)
SCREEN_BACKTEST_SETTINGS.update(SCREEN)

ROLLING_SCREEN = {}
ROLLING_SCREEN.update(SCREEN)
ROLLING_SCREEN.update(SCREEN_ROLLING_BACKTEST)

ROLLING_SCREEN_SETTINGS = init.SETTINGS.copy()
ROLLING_SCREEN_SETTINGS.update(ROLLING_SCREEN)
ROLLING_SCREEN_SETTINGS['Include Results'] = {
    'isValid': misc.is_bool
}

ROLLING_SCREEN_ITERATIONS = init.ITERATIONS.copy()
ROLLING_SCREEN_ITERATIONS.update(ROLLING_SCREEN)


RANK_PERF = {}
RANK_PERF.update(SCREEN)
RANK_PERF.update(SCREEN_BACKTEST)
del RANK_PERF['Rules'],\
    RANK_PERF['Long Rules'],\
    RANK_PERF['Short Rules'],\
    RANK_PERF['Hedge Rules'],\
    RANK_PERF['Max Num Holdings'],\
    RANK_PERF['Screen'],\
    RANK_PERF['Trans Price'],\
    RANK_PERF['Max Pos Pct'],\
    RANK_PERF['Long Weight'],\
    RANK_PERF['Short Weight'],\
    RANK_PERF['Rank Tolerance'],\
    RANK_PERF['Carry Cost'],\
    RANK_PERF['Risk Stats Period']
RANK_PERF['Method'] = RANK_PERF['Method'].copy()
RANK_PERF['Method']['isValid'] = functools.partial(validation.from_mapping, mapping=cons.RANK_PERF_METHOD)
RANK_PERF['Minimum Price'] = {
    'field': 'rules',
    'isValid': misc.is_number,
    'type': 'screen',
    'transform': transform.rank_perf_min_price
}

RANK_PERF_SETTINGS = {
    'Buckets': {
        'isValid': validation.rank_perf_buckets,
        'required': True
    }
}
RANK_PERF_SETTINGS.update(init.SETTINGS)
RANK_PERF_SETTINGS.update(RANK_PERF)

RANK_PERF_ITERATIONS = init.ITERATIONS.copy()
RANK_PERF_ITERATIONS.update(RANK_PERF)
