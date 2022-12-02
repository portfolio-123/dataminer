from p123api import Client
import utils.misc as misc
import datetime
import p123.data.cons as cons

"""
Functions for transforming human readable values into API compatible parameters
(may require extra API calls - API universe)
"""


# noinspection PyUnusedLocal
def date(*, value: datetime.date, **kwargs):
    return misc.parse_date(value).strftime('%Y-%m-%d')


def universe(*, value, settings: dict, api_client: Client):
    if misc.is_str(value):
        return value

    params = {'type': settings['Type'], 'startingUniverse': value['Starting Universe'], 'rules': value['Rules']}
    api_client.universe_update(params)
    return 'ApiUniverse'


# noinspection PyUnusedLocal
def screen_rules(*, value, **kwargs):
    return list({'formula': formula} for formula in value)


# noinspection PyUnusedLocal
def screen_long_rules(*, value, **kwargs):
    return list({'formula': formula, 'type': 'long'} for formula in value)


# noinspection PyUnusedLocal
def screen_short_rules(*, value, **kwargs):
    return list({'formula': formula, 'type': 'short'} for formula in value)


# noinspection PyUnusedLocal
def screen_hedge_rules(*, value, **kwargs):
    return list({'formula': formula, 'type': 'hedge'} for formula in value)


def screen_ranking(*, value, settings: dict, api_client: Client):
    if misc.is_str(value) or misc.is_int(value):
        return value

    params = {}
    if 'Formula' in value:
        params['formula'] = value['Formula']
        if 'Lower is Better' in value:
            params['lowerIsBetter'] = value['Lower is Better']
    else:
        nodes = value['Nodes']
        if misc.is_list(nodes):
            nodes = screen_ranking_nodes_to_xml(nodes, main_rank=value.get('Rank'))

        rank_params = {'type': settings['Type'], 'nodes': nodes}
        if 'Method' in value:
            rank_params['rankingMethod'] = cons.RANKING_METHOD[value['Method'].lower()]
        api_client.rank_update(rank_params)
        params = 'ApiRankingSystem'

    return params


def escape_xml_attr(data):
    return data.replace('"', '&quot;')


def screen_ranking_nodes_to_xml(nodes, level=1, main_rank=None):
    xml = ''
    if level == 1:
        xml += '<RankingSystem RankType="{}">'.format(misc.coalesce(main_rank, 'Higher'))
    nodes_cnt = len(nodes)
    equal_weight = round(100 / nodes_cnt, 4)
    for idx, node in enumerate(nodes):
        node_type = node['Type']
        weight = node.get('Weight')
        if not weight:
            weight = equal_weight if idx < nodes_cnt - 1 or nodes_cnt == 1 else 100 - equal_weight * (nodes_cnt - 1)
        rank = misc.coalesce(node.get('Rank'), 'Higher')

        if node_type == 'Composite':
            name = escape_xml_attr(misc.coalesce(node.get('Name'), node_type))
            xml += '\n{}<Composite Name="{}" Weight="{}%" RankType="{}">'\
                .format('\t' * level, name, weight, rank)
            xml += screen_ranking_nodes_to_xml(node['Nodes'], level + 1)
            xml += '\n{}</Composite>'.format('\t' * level)
        else:
            formula = node['Formula']
            name = escape_xml_attr(misc.coalesce(node.get('Name'), formula)[:50])
            if node_type == 'Conditional':
                xml += '\n{}<Conditional Name="{}" Weight="{}%" RankType="{}">' \
                    .format('\t' * level, name, weight, rank)
                xml += '\n{}<Formula>{}</Formula>'.format('\t' * (level + 1), formula)
                xml += '\n{}<Boolean Name="True">'.format('\t' * (level + 1))
                xml += screen_ranking_nodes_to_xml(node['True Nodes'], level + 2)
                xml += '\n{}</Boolean>'.format('\t' * (level + 1))
                xml += '\n{}<Boolean Name="False">'.format('\t' * (level + 1))
                xml += screen_ranking_nodes_to_xml(node['False Nodes'], level + 2)
                xml += '\n{}</Boolean>'.format('\t' * (level + 1))
                xml += '\n{}</Conditional>'.format('\t' * level)
            elif node_type == 'StockFormula':
                xml += '\n{}<StockFormula Name="{}" Weight="{}%" RankType="{}" Scope="{}">' \
                    .format('\t' * level, name, weight, rank, misc.coalesce(node.get('Scope'), 'Universe'))
                xml += '\n{}<Formula>{}</Formula>'.format('\t' * (level + 1), formula)
                xml += '\n{}</StockFormula>'.format('\t' * level)
            else:
                xml += '\n{}<{} Name="{}" Weight="{}%" RankType="{}">' \
                    .format('\t' * level, node_type, name, weight, rank)
                xml += '\n{}<Formula>{}</Formula>'.format('\t' * (level + 1), formula)
                xml += '\n{}</{}>'.format('\t' * level, node_type)
    if level == 1:
        xml += '\n</RankingSystem>'
    return xml


def from_mapping(*, value: str, **kwargs):
    return kwargs['mapping'][value.lower()]


# noinspection PyUnusedLocal
def rank_perf_min_price(*, value, **kwargs):
    return [{'formula': f'close(0) >= {value}'}]


# noinspection PyUnusedLocal
def data_items(*, value, **kwargs):
    if misc.is_int(value):
        value = [value]
    elif misc.is_str(value):
        value = value.split(' ')
    return value
