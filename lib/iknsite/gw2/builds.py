import logging
import collections
import html

import gw2buildutil

from .. import util

logger = logging.getLogger(__name__)
PAGE_ID = 'builds'
PAGE_TITLE = 'Guild Wars 2 builds'

# in display order
SPECS = [
    'warrior',
    'berserker',
    'spellbreaker',
    'bladesworn',
    'guardian',
    'dragonhunter',
    'firebrand',
    'willbender',
    'revenant',
    'herald',
    'renegade',
    'vindicator',
    'ranger',
    'druid',
    'soulbeast',
    'untamed',
    'thief',
    'daredevil',
    'deadeye',
    'specter',
    'engineer',
    'scrapper',
    'holosmith',
    'mechanist',
    'necromancer',
    'reaper',
    'scourge',
    'harbinger',
    'elementalist',
    'tempest',
    'weaver',
    'catalyst',
    'mesmer',
    'chronomancer',
    'mirage',
    'virtuoso',
]
BUILD_GAME_MODES = {
    gw2buildutil.build.GameModes.RAIDS: {},
    gw2buildutil.build.GameModes.DUNGEONS: {},
    gw2buildutil.build.GameModes.OPEN_WORLD: {},
    gw2buildutil.build.GameModes.PVP: {},
    gw2buildutil.build.GameModes.WVW: {},
}

RAIDS_BUILD_ROLES = {
    'power': {
        'name': 'Power DPS',
        'labels': {'power'},
    },
    'condi': {
        'name': 'Condition DPS',
        'labels': {'condi'},
    },
    'boon': {
        'name': 'Boon support',
        'desc': 'Boon duration is optimised for raids, not fractals.',
        'labels': {'might', 'quickness', 'alacrity'}
    },
    'heal': {
        'name': 'Healing',
        'desc': ('These builds supply healing and some dps, without quickness '
                 'or alacrity.  They can be used in any composition, but work '
                 'great in roles where you can\'t always reliably share boons, '
                 'such as tanking or kiting on some encounters.'),
        'labels': {'healing'},
    },
    'specialised': {
        'name': 'Specialised role',
        'labels': {'deimos kite'},
    },
}

BUILD_BOON_SUPPORT_GROUPS = {
    'quickness dps': {
        'name': 'Quickness DPS',
        'labels': lambda labels: ('quickness' in labels and
                                  'healing' not in labels and
                                  ('power' in labels or 'condi' in labels)),
    },
    'alacrity dps': {
        'name': 'Alacrity DPS',
        'labels': lambda labels: ('alacrity' in labels and
                                  'healing' not in labels and
                                  ('power' in labels or 'condi' in labels)),
    },
    'quickness healing': {
        'name': 'Quickness healing',
        'labels': lambda labels: 'quickness' in labels and 'healing' in labels
    },
    'alacrity healing': {
        'name': 'Alacrity healing',
        'labels': lambda labels: 'alacrity' in labels and 'healing' in labels
    },
}

PVP_BUILD_ROLES = {
    'damage': {
        'name': 'Damage',
        'labels': {'damage'},
    },
    'support': {
        'name': 'Support',
        'labels': {'support'},
    },
    'duelist': {
        'name': 'Duelist',
        'labels': {'duelist'},
    },
    'roamer': {
        'name': 'Roamer',
        'labels': {'roamer'}
    },
}


def game_mode_desc (mode):
    sentences = []
    if len(mode.value.suitable_game_modes) > 1:
        sentences.append(
            'Suitable for use in: ' +
            html.escape(', '.join(mode.value.suitable_game_modes) + '.'))
    if 'desc' in BUILD_GAME_MODES[mode]:
        sentences.append(BUILD_GAME_MODES[mode]['desc'])
    return '  '.join(sentences) if sentences else None


def build_role (roles, build):
    for label in build.metadata.labels:
        for role, role_defn in roles.items():
            if label in role_defn['labels']:
                return role
    raise ValueError(f'no role defined for build: {build.metadata.title}')


def role_grouping_method (roles, subgrouping_method):
    return {
        'groups': list(roles.keys()),
        'group label': lambda role: roles[role]['name'],
        'group html desc': lambda role: roles[role].get('desc'),
        'build group': lambda build: build_role(roles, build),
        'subgroup method': subgrouping_method,
    }


def build_boon_support_group (build):
    for group, group_defn in BUILD_BOON_SUPPORT_GROUPS.items():
        if group_defn['labels'](build.metadata.labels):
            return group
    raise ValueError('no boon support group defined for build: '
                     f'{build.metadata.title}')


BUILD_GROUPING_METHOD_BOON_SUPPORT = {
    'groups': list(BUILD_BOON_SUPPORT_GROUPS.keys()),
    'group label': lambda group: BUILD_BOON_SUPPORT_GROUPS[group]['name'],
    'group html desc':
        lambda group: BUILD_BOON_SUPPORT_GROUPS[group].get('desc'),
    'build group': build_boon_support_group,
    'subgroup method': lambda group: None,
}
GAME_MODE_SUBGROUP_METHODS = {
    gw2buildutil.build.GameModes.RAIDS: role_grouping_method(
        RAIDS_BUILD_ROLES,
        lambda group: (BUILD_GROUPING_METHOD_BOON_SUPPORT
                       if group == 'boon' else None)
    ),
    gw2buildutil.build.GameModes.PVP: role_grouping_method(
        PVP_BUILD_ROLES, lambda group: None),
}
BUILD_GROUPING_METHOD_GAME_MODE = {
    'groups': list(BUILD_GAME_MODES.keys()),
    'group label': lambda mode: mode.value.name,
    'group html desc': game_mode_desc,
    'build group': lambda build: build.metadata.game_mode,
    'subgroup method': lambda group: GAME_MODE_SUBGROUP_METHODS.get(group),
}


def sort_builds (build):
    return SPECS.index(build.metadata.profession.id_
                       if build.metadata.elite_spec is None
                       else build.metadata.elite_spec.id_)


def build_groups (builds, grouping_method):
    grouped_builds = {group: [] for group in grouping_method['groups']}
    for build in builds:
        grouped_builds[grouping_method['build group'](build)].append(build)

    group_defns = []
    for group, group_builds in grouped_builds.items():
        subgrouping_method = grouping_method['subgroup method'](group)
        if subgrouping_method is None:
            key = 'builds'
            child_builds = sorted(group_builds, key=sort_builds)
        else:
            key = 'groups'
            child_builds = build_groups(group_builds, subgrouping_method)
        if child_builds:
            group_defns.append({
                'label': grouping_method['group label'](group),
                'html desc': grouping_method['group html desc'](group),
                key: child_builds,
            })
    return group_defns


def build (gw2site):
    grouped_builds = build_groups(list(gw2site.builds.values()),
                                  BUILD_GROUPING_METHOD_GAME_MODE)
    logger.info(f'{len(gw2site.builds)} builds')
    gw2site.render_page_template(PAGE_ID, PAGE_TITLE, {
        'grouped_builds': grouped_builds,
    })
