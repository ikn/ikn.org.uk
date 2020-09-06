import os
import json

import gw2buildutil

from .. import util as siteutil
from . import (
    util as gw2util,
    builds as builds_page_builder,
    compositions as compositions_page_builder,
)

LOG_TAG = 'gw2'
PAGE_ID = 'gw2'


class Gw2Site:
    def __init__ (self, site):
        self.site = site
        self.data_path = os.path.join(self.site.data_path, PAGE_ID)
        self.icons_page = self.site.images_page.child(PAGE_ID).child('icon')

    def _init_tags (self):
        tags_definitions_path = os.path.join(
            self.data_path, 'tags-definitions.json')
        with open(tags_definitions_path) as f:
            tags_data = json.load(f)

        tags = {}
        for name, data in tags_data.items():
            tags[name] = gw2util.Tag(self, name, data['build icon'])
        return tags

    def _load_builds (self):
        builds_config_path = os.path.join(self.data_path, 'builds.json')
        with open(builds_config_path) as builds_config_f:
            builds_config = json.load(builds_config_f)
        builds_base_path = os.path.expanduser(builds_config['path'])
        categories = ['active', '3rd party']

        builds = {}
        for category in categories:
            path = os.path.join(builds_base_path, category)
            for in_name in os.listdir(path):
                build_meta = gw2buildutil.parse.parse_title(in_name)
                with open(os.path.join(path, in_name), 'r') as f_in:
                    builds[in_name] = (
                        gw2buildutil.parse.parse_body(f_in, build_meta))

        return builds

    def render_page_template (self, page_id, page_title,
                              template_args={}, js_deps=()):
        full_template_args = {
            'gw2site': self, 'gw2util': gw2util,
        }
        full_template_args.update(template_args)

        self.site.render_page_template(
            f'{PAGE_ID}/{page_id}', page_title, full_template_args, js_deps)

    def build (self):
        self.builds = self._load_builds()
        siteutil.log(LOG_TAG, len(self.builds), 'builds')
        self.tags = self._init_tags()

        for page_builder in (builds_page_builder, compositions_page_builder):
            siteutil.log(LOG_TAG, f'start {page_builder.PAGE_ID}')
            page_builder.build(self)


def build (site):
    Gw2Site(site).build()
