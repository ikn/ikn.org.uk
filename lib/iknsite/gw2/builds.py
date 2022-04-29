import logging
import collections
import html

import gw2buildutil

from .. import util

logger = logging.getLogger(__name__)
PAGE_ID = 'builds'
PAGE_TITLE = 'Guild Wars 2 builds'

# in display order
PROFESSIONS = [
    'warrior',
    'guardian',
    'revenant',
    'ranger',
    'thief',
    'engineer',
    'necromancer',
    'elementalist',
    'mesmer',
]
BUILD_GAME_MODES = {
    gw2buildutil.build.GameModes.RAIDS: {},
    gw2buildutil.build.GameModes.FRACTALS: {},
    gw2buildutil.build.GameModes.DUNGEONS: {},
    gw2buildutil.build.GameModes.OPEN_WORLD: {},
    gw2buildutil.build.GameModes.PVP: {},
    gw2buildutil.build.GameModes.WVW: {},
}

BUILD_ROLES = {
    'power': {
        'name': 'Power DPS',
        'desc': 'Critical hit chance is optimised for raids, not fractals.',
        'labels': {'power'},
    },
    'condi': {
        'name': 'Condition DPS',
        'labels': {'condi'},
    },
    'boon': {
        'name': 'Boon support',
        'desc': ('Boon duration is optimised for raids, not fractals.  See '
                 'also the <a href="../roles"> list of raid roles</a>.'),
        'labels': {
            'boons',
            'might',
            'some might',
            'squad might',
            'some squad might',
            'quickness',
            'some quickness',
            'squad quickness',
            'some squad quickness',
            'alacrity',
            'some alacrity',
            'squad alacrity',
            'some squad alacrity',
        }
    },
    'heal': {
        'name': 'Healing',
        'desc': ('These builds are intended for use in a role where you can\'t '
                 'also reliably share boons or deal damage, such as tanking or '
                 'kiting on some bosses.'),
        'labels': {'healing', 'support'},
    },
    'hybrid': {
        'name': 'Hybrid role',
        'desc': ('Other builds may fill multiple roles, but they\'re optimised '
                 'primarily for one role over the others.  These builds, on '
                 'the other hand, aren\'t fully optimised for any single '
                 'role.'),
        'labels': {'hybrid'},
    },
    'specialised': {
        'name': 'Specialised role',
        'labels': {'deimos kite'},
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


def build_role (build):
    for label in build.metadata.labels:
        for role, role_defn in BUILD_ROLES.items():
            if label in role_defn['labels']:
                return role
    raise ValueError(f'no role defined for build: {build.metadata.title}')


# number of builds required to group by next method
BUILD_GROUPING_THRESHOLD = 10
BUILD_GROUPING_METHODS = [
    {
        'groups': list(BUILD_GAME_MODES.keys()),
        'group label': lambda mode: mode.value.name,
        'group html desc': game_mode_desc,
        'build group': lambda build: build.metadata.game_mode,
    },
    {
        'groups': list(BUILD_ROLES.keys()),
        'group label': lambda role: BUILD_ROLES[role]['name'],
        'group html desc': lambda role: BUILD_ROLES[role].get('desc'),
        'build group': build_role,
    }
]


def sort_builds (build):
    return PROFESSIONS.index(build.metadata.profession.id_)


def build_groups (builds, grouping_methods):
    if not grouping_methods or len(builds) < BUILD_GROUPING_THRESHOLD:
        return sorted(builds, key=sort_builds)

    grouping_method = grouping_methods[0]
    grouped_builds = {group: [] for group in grouping_method['groups']}
    for build in builds:
        grouped_builds[grouping_method['build group'](build)].append(build)

    group_defns = []
    for group, group_builds in grouped_builds.items():
        child_builds = build_groups(group_builds, grouping_methods[1:])
        if child_builds:
            group_defns.append({
                'label': grouping_method['group label'](group),
                'html desc': grouping_method['group html desc'](group),
                ('groups' if isinstance(child_builds[0], dict) else 'builds'):
                    child_builds
            })
    return group_defns


def build (gw2site):
    grouped_builds = build_groups(list(gw2site.builds.values()),
                                  BUILD_GROUPING_METHODS)

    logger.info(f'{len(gw2site.builds)} builds')
    logger.info(f'{len(grouped_builds)} build groups')

    gw2site.render_page_template(PAGE_ID, PAGE_TITLE, {
        'grouped_builds': grouped_builds,
    })
