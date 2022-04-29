import os
import json
import logging
import time

from gw2buildutil import defnfile, api as gw2api

from . import (
    util as gw2util,
    builds as builds_page_builder,
    roles as roles_page_builder,
)

logger = logging.getLogger(__name__)
PAGE_ID = 'gw2'

CRAWL_MAX_AGE_SECONDS = 60 * 60 * 24 * 1


class Gw2Site:
    def __init__ (self, site):
        self.site = site
        self.data_path = os.path.join(self.site.data_path, PAGE_ID)
        self.icons_page = self.site.images_page.child(PAGE_ID).child('icon')
        self._crawl_time_path = os.path.join(self.site.cache_path,
                                             'gw2-crawl-time')

    def _init_tags (self):
        tags_definitions_path = os.path.join(
            self.data_path, 'tags-definitions.json')
        with open(tags_definitions_path) as f:
            tags_data = json.load(f)

        tags = {}
        for name, data in tags_data.items():
            tags[name] = gw2util.Tag(self, name, data['build icon'])
        return tags

    def _get_crawl_time (self):
        try:
            with open(self._crawl_time_path) as f:
                return int(f.read())
        except (FileNotFoundError, ValueError) as e:
            return 0

    def _set_crawl_time (self, t):
        with open(self._crawl_time_path, 'w') as f:
            f.write(str(int(t)))

    def _load_builds (self):
        builds_config_path = os.path.join(self.data_path, 'builds.json')
        with open(builds_config_path) as builds_config_f:
            builds_config = json.load(builds_config_f)
        builds_base_path = os.path.expanduser(builds_config['path'])
        categories = ['6 - active', '5 - ready']

        if self._get_crawl_time() < (time.time() - CRAWL_MAX_AGE_SECONDS):
            gw2api.crawl.crawl()
            self._set_crawl_time(time.time())

        builds = {}
        with gw2api.storage.FileStorage() as api_storage:
            for category in categories:
                path = os.path.join(builds_base_path, category)
                for in_name in os.listdir(path):
                    build_meta = defnfile.parse_title(in_name, api_storage)
                    with open(os.path.join(path, in_name), 'r') as f_in:
                        builds[in_name] = (
                            defnfile.parse_body(f_in, build_meta, api_storage))

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
        logger.info(f'{len(self.builds)} builds')
        self.tags = self._init_tags()

        for page_builder in (builds_page_builder, roles_page_builder):
            logger.info(f'start {page_builder.PAGE_ID}')
            page_builder.build(self)


def build (site):
    Gw2Site(site).build()
