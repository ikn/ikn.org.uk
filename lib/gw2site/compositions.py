import sys
import json
import os
import shutil
import collections

from PIL import Image
import gw2build
import gw2build.compositions

from . import util

LOG_TAG = 'compositions'
GAME_MODE = gw2build.definitions.game_modes['raids']
TARGET_BOONS = [ # ordering here determines roles display order
    gw2build.definitions.boons['might'],
    gw2build.definitions.boons['quickness'],
    gw2build.definitions.boons['alacrity'],
]
TARGET_UPTIME = 1.25
PAGE_ID = 'compositions'
PAGE_TITLE = 'Guild Wars 2 raids boon-share builds'
ROLE_ICON_UNFILLED_TRANSPARENCY = .3


def _role_icons_page (site):
    return site.resources_page.child('role-icon')


def _role_icon_page (site, role):
    return _role_icons_page(site).child(role.id_ + '.png')


class _RoleDisplayInfo:
    def __init__ (self, site, role):
        self.role = role
        self.icon_page = _role_icon_page(site, role).as_image()


def _render_role_icon_part (boon_icon, role_icon, uptime,
                            crop_l, crop_r, position_l):
    boon_icon_h = boon_icon.size[1]
    filled_h = int(boon_icon_h * min(1, uptime / TARGET_UPTIME))
    filled_icon = boon_icon.crop(
        (crop_l, boon_icon_h - filled_h, crop_r, boon_icon_h))
    unfilled_icon = boon_icon.crop(
        (crop_l, 0, crop_r, boon_icon_h - filled_h)
    ).convert('RGBA')
    unfilled_icon_transparent = unfilled_icon.copy()
    unfilled_icon_transparent.putalpha(0)
    unfilled_icon = Image.blend(unfilled_icon_transparent, unfilled_icon,
                                ROLE_ICON_UNFILLED_TRANSPARENCY)
    role_icon.paste(filled_icon, (position_l, boon_icon_h - filled_h))
    role_icon.paste(unfilled_icon, (position_l, 0))


def _render_role_icon (site, boon_icon_cache, role):
    role_boons = [boon for boon in TARGET_BOONS if role.provides_buff(boon)]
    for boon in role_boons:
        if boon not in boon_icon_cache:
            icon_path = site.tags[boon.id_].build_icon_page.path
            boon_icon_cache[boon] = Image.open(icon_path)

    role_icon_w = sum(boon_icon_cache[boon].size[0] for boon in role_boons)
    role_icon_h = max(boon_icon_cache[boon].size[1] for boon in role_boons)
    role_icon = Image.new('RGBA', (role_icon_w, role_icon_h),
                          (255, 255, 255, 0))

    position_l = 0
    for boon in role_boons:
        boon_icon = boon_icon_cache[boon]
        boon_icon_w = boon_icon.size[0]
        party_w = boon_icon_w // 2

        uptime5 = role.uptime(boon, gw2build.definitions.boon_targets['5'])
        _render_role_icon_part(boon_icon, role_icon, uptime5,
                               0, party_w, position_l)
        uptime10 = role.uptime(boon, gw2build.definitions.boon_targets['10'])
        _render_role_icon_part(boon_icon, role_icon, uptime10,
                               party_w, boon_icon_w, position_l + party_w)

        position_l += boon_icon_w
    role_icon.save(_role_icon_page(site, role).path)

    return (role_icon_w, role_icon_h)


def _role_sort_key (role):
    # roles providing earlier boons in TARGET_BOONS come earlier
    # smaller numbers of boons come earlier
    result = []
    found_boon = False
    for boon in reversed(TARGET_BOONS):
        if role.provides_buff(boon):
            result.insert(0, 0)
            found_boon = True
        elif found_boon:
            result.insert(0, 1)
        else:
            result.insert(0, -1)
    return result


def sort_roles (roles):
    return sorted(roles, key=_role_sort_key)


def _roles_display_info (site, comps):
    roles = {role for role in sum((comp.roles for comp in comps), [])}

    _role_icons_page(site).create()
    boon_icon_cache = {}
    max_icon_w = 0
    max_icon_h = 0
    for role in roles:
        icon_w, icon_h = _render_role_icon(site, boon_icon_cache, role)
        max_icon_w = max(max_icon_w, icon_w)
        max_icon_h = max(max_icon_h, icon_h)
    for icon in boon_icon_cache.values():
        icon.close()

    max_role_icon_size = (max_icon_w, max_icon_h)
    roles_display_info = collections.OrderedDict(
        (role.id_, _RoleDisplayInfo(site, role)) for role in sort_roles(roles))
    return (max_role_icon_size, roles_display_info)


def _comps_display_info (comps):
    return sorted(comps, key=lambda comp: len(comp.roles))


def build (site):
    config = gw2build.compositions.Configuration(
        target_buffs=TARGET_BOONS,
        target_uptime=TARGET_UPTIME)
    matching_builds = {name: build for name, build in site.builds.items()
                       if build.metadata.game_modes is GAME_MODE}
    roles = gw2build.compositions.Role.list_from_builds(
        matching_builds, config)
    comps = list(
        gw2build.compositions.generate_compositions(roles, config))

    max_role_icon_size, roles_display_info = _roles_display_info(site, comps)
    comps_display_info = _comps_display_info(comps)
    util.log(LOG_TAG, len(roles), 'roles')
    util.log(LOG_TAG, len(roles_display_info), 'used roles')
    util.log(LOG_TAG, len(comps), 'compositions')

    site.render_page_template(PAGE_ID, PAGE_TITLE, {
        'compositions_module': sys.modules[__name__],
        'builds': matching_builds,
        'roles': roles_display_info,
        'compositions': comps_display_info,
        'max_role_icon_size': max_role_icon_size,
    }, js_deps=[
        util.JsDependency.JQUERY,
        util.JsDependency.UTIL,
    ])
