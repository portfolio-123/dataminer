import utils.misc as misc
import p123.data.cons as cons


"""
Functions for validation human readable values against API requirements
"""


def screen_rules(rules):
    if not misc.is_list(rules):
        return False
    for rule in rules:
        if not misc.is_str(rule):
            return False
    return True


def from_mapping(value, **kwargs):
    return misc.is_str(value) and value.lower() in kwargs['mapping']


def from_mapping_any(value, **kwargs):
    return value in kwargs['mapping']


def universe(univ):
    if misc.is_str(univ):
        return True
    elif not misc.is_dict(univ):
        return False

    rules = None
    starting_universe = None
    for key, value in univ.items():
        if key == 'Rules':
            if not misc.is_list(value):
                return '"Rules" property is invalid'
            rules = value
        elif key == 'Starting Universe':
            if not misc.is_number(value) and (not misc.is_str(value) or not value):
                return '"Starting Universe" property is invalid'
            starting_universe = value
        else:
            return f'Unexpected "{key}" property'

    if not rules:
        return '"Rules" property is missing'
    else:
        for key, value in enumerate(rules):
            if not misc.is_number(value) and (not misc.is_str(value) or not value):
                return f'"Rules" item #{key + 1} is empty'

    if starting_universe is None:
        return '"Starting Universe" property is missing'

    return True


def ranking_system(ranking):
    if misc.is_str(ranking) or misc.is_int(ranking):
        return True
    elif not misc.is_dict(ranking):
        return False

    return ranking_system_dict(ranking)


def ranking_system_dict(ranking):
    nodes = ranking.get('Nodes')
    if nodes is None:
        return '"Nodes" property required'

    is_list = misc.is_list(nodes)
    if not is_list and not misc.is_str(nodes):
        return '"Nodes" property must be a list or a string containing a XML structure'

    for key, value in ranking.items():
        if key == 'Nodes':
            pass
        elif key == 'Rank' and is_list:
            if not misc.is_str(value) or value not in ('Lower', 'Higher', 'Summation'):
                return '"Rank" property is invalid'
        elif key == 'Method':
            if not misc.is_str(value) or value.lower() not in cons.RANKING_METHOD:
                return '"Method" property is invalid'
        else:
            return f'Unexpected "{key}" property'

    if is_list:
        ret = screen_ranking_nodes(nodes)
        if not misc.is_bool(ret) or not ret:
            return ret

    return True


def screen_ranking(ranking):
    if misc.is_str(ranking) or misc.is_int(ranking):
        return True
    elif not misc.is_dict(ranking):
        return False

    has_formula = 'Formula' in ranking
    has_nodes = 'Nodes' in ranking
    if not has_formula and not has_nodes:
        return '"Formula"/"Nodes" property required'
    if has_formula and has_nodes:
        return '"Formula" and "Nodes" properties cannot be mixed'

    if has_formula:
        formula = ranking.get('Formula')
        if not misc.is_number(formula) and (not misc.is_str(formula) or not formula):
            return '"Formula" property is invalid'

        for key, value in ranking.items():
            if key == 'Formula':
                pass
            elif key == 'Lower is Better':
                if not misc.is_bool(value):
                    return '"Lower is Better" property is invalid'
            else:
                return f'Unexpected "{key}" property'

        return True
    else:
        return ranking_system_dict(ranking)


def screen_ranking_node_error(breadcrumbs, node_idx=None, node_type=None, error=None):
    ret = breadcrumbs
    if node_idx is not None:
        ret += ' > {} ({})'.format(node_type if node_type is not None else 'Node', node_idx + 1)
    ret += ': ' + error
    return ret


def screen_ranking_nodes(nodes: list, breadcrumbs='Nodes'):
    total_weight = 0
    for idx, node in enumerate(nodes):
        if not misc.is_dict(node):
            return screen_ranking_node_error(breadcrumbs, idx, error='is invalid')

        if 'Type' not in node:
            return screen_ranking_node_error(breadcrumbs, idx, error='"Type" property is missing')

        node_type = node['Type']
        if not misc.is_str(node_type)\
                or node_type not in ('Composite', 'StockFormula', 'IndFormula', 'SecFormula', 'Conditional'):
            return screen_ranking_node_error(breadcrumbs, idx, error='"Type" property is invalid')

        weight = 0
        rank = None
        sub_nodes = None
        formula = None
        scope = None
        true_nodes = None
        false_nodes = None
        for key, value in node.items():
            if key == 'Type':
                pass
            elif key == 'Weight':
                if not misc.is_number(value) or value < 0:
                    return screen_ranking_node_error(breadcrumbs, idx, node_type, error='"Weight" property is invalid')
                weight = value
            elif key == 'Rank':
                if not misc.is_str(value):
                    return screen_ranking_node_error(breadcrumbs, idx, node_type, error='"Rank" property is invalid')
                rank = value
            elif key == 'Name':
                if not misc.is_number(value) and (not misc.is_str(value) or not value):
                    return screen_ranking_node_error(breadcrumbs, idx, node_type, error='"Name" property is invalid')
            elif key == 'Nodes' and node_type == 'Composite':
                if not misc.is_list(value):
                    return screen_ranking_node_error(breadcrumbs, idx, node_type, error='"Nodes" property is invalid')
                sub_nodes = value
            elif key == 'Formula' and node_type in ('Conditional', 'StockFormula', 'IndFormula', 'SecFormula'):
                if not misc.is_number(value) and (not misc.is_str(value) or not value):
                    return screen_ranking_node_error(breadcrumbs, idx, node_type, error='"Formula" property is invalid')
                formula = value
            elif key == 'Scope' and node_type == 'StockFormula':
                if not misc.is_str(value) or not len(value):
                    return screen_ranking_node_error(breadcrumbs, idx, node_type, error='"Scope" property is invalid')
                scope = value
            elif key == 'True Nodes' and node_type == 'Conditional':
                if not misc.is_list(value):
                    return screen_ranking_node_error(
                        breadcrumbs, idx, node_type, error='"True Nodes" property is invalid')
                true_nodes = value
            elif key == 'False Nodes' and node_type == 'Conditional':
                if not misc.is_list(value):
                    return screen_ranking_node_error(
                        breadcrumbs, idx, node_type, error='"False Nodes" property is invalid')
                false_nodes = value
            else:
                return f'Unexpected "{key}" property'

        if idx > 0 and (weight == 0) ^ (total_weight == 0):
            return screen_ranking_node_error(breadcrumbs, idx, node_type, error='Cannot mix 0 and non 0 weight nodes')
        total_weight += weight

        if node_type == 'Composite':
            if rank and rank not in ('Higher', 'Lower', 'Summation'):
                return screen_ranking_node_error(breadcrumbs, idx, node_type, '"Rank" property is invalid')
            if not sub_nodes:
                return screen_ranking_node_error(breadcrumbs, idx, node_type, error='"Nodes" property is missing')
            ret = screen_ranking_nodes(sub_nodes, f'{breadcrumbs} > {node_type} ({idx + 1})')
            if not misc.is_bool(ret) or not ret:
                return ret
        elif node_type in ('StockFormula', 'IndFormula', 'SecFormula'):
            if rank and rank not in ('Higher', 'Lower', 'Boolean'):
                return screen_ranking_node_error(breadcrumbs, idx, node_type, '"Rank" property is invalid')
            if formula is None:
                return screen_ranking_node_error(breadcrumbs, idx, node_type, '"Formula" property is missing')
            if scope and scope not in ('Universe', 'Industry', 'Sector'):
                return screen_ranking_node_error(breadcrumbs, idx, node_type, '"Scope" property is invalid')
        elif node_type == 'Conditional':
            if rank and rank not in ('Higher', 'Lower'):
                return screen_ranking_node_error(breadcrumbs, idx, node_type, '"Rank" property is invalid')
            if formula is None:
                return screen_ranking_node_error(breadcrumbs, idx, node_type, '"Formula" property is missing')
            if not true_nodes:
                return screen_ranking_node_error(breadcrumbs, idx, node_type, '"True Nodes" property is missing')
            ret = screen_ranking_nodes(true_nodes, f'{breadcrumbs} > {node_type} ({idx + 1}) True')
            if not misc.is_bool(ret) or not ret:
                return ret
            if not false_nodes:
                return screen_ranking_node_error(breadcrumbs, idx, node_type, '"False Nodes" property is missing')
            ret = screen_ranking_nodes(false_nodes, f'{breadcrumbs} > {node_type} ({idx + 1}) False')
            if not misc.is_bool(ret) or not ret:
                return ret
    return True


def screen_rolling_backtest_holding_period(val):
    return misc.is_int(val) and 1 <= val <= 730


def rank_perf_buckets(val):
    return misc.is_int(val) and 1 <= val <= 20


def data_p123_uids(val):
    if misc.is_int(val):
        val = [val]
    elif misc.is_str(val):
        val = val.split(' ')

    if not misc.is_list(val):
        return False

    for item in val:
        try:
            int(item)
        except ValueError:
            return False

    return True


def data_tickers_cusips(val):
    return misc.is_int(val) or misc.is_str(val) or misc.is_list(val)


def data_formula(val):
    return misc.is_int(val) or misc.is_str(val)


def date(val):
    return misc.parse_date(val) is not None


def data_univ_formulas(val):
    if not misc.is_list(val):
        return False
    for item in val:
        if not (misc.is_number(item) or misc.is_str(item) or (misc.is_dict(item) and len(item) == 1)):
            return False
    return True


def data_univ_as_of_date(val):
    if misc.is_list(val):
        for dt in val:
            if misc.parse_date(dt) is None:
                return False
        return True
    return misc.parse_date(val) is not None


def currency(val):
    return misc.is_str(val) and len(val) == 3
