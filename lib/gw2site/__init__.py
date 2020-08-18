import os
import json
import shutil

import jinja2

from . import compositions as compositions_page, util

LOG_TAG = 'site'


class Site:
    def __init__ (self, builds, files_path, dest_path, base_link_path='/'):
        self.builds = builds
        util.log(LOG_TAG, len(builds), 'builds')
        self.files_path = files_path
        self.source_resources_path = os.path.join(files_path, 'resources')
        self.page = util.Page(dest_path, base_link_path)
        self.builds_page = self.page.child('builds')
        self.resources_page = self.page.child('resources')
        self.stylesheets_page = self.resources_page.child('css')
        self.scripts_page = self.resources_page.child('js')
        self.build_icons_page = self.resources_page.child('build-icon')

    def _init_tags (self):
        tags_definitions_path = os.path.join(
            self.files_path, 'tags-definitions.json')
        with open(tags_definitions_path) as f:
            tags_data = json.load(f)

        tags = {}
        for name, data in tags_data.items():
            tags[name] = util.Tag(self, name, data['build icon'])
        return tags

    def _init_jinja (self):
        templates_path = os.path.join(self.files_path, 'templates')
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_path))

    def render_page_template (self, page_id, page_title, template_args,
                              js_deps=()):
        full_template_args = {
            'site': self, 'util': util,
            'page_id': page_id, 'page_title': page_title,
            'js_deps': js_deps,
        }
        full_template_args.update(template_args)

        for src_rel_path, dest_page in (
            (
                f'page/{page_id}.html.j2',
                self.page.child(f'{page_id}.html')
            ),
            (
                f'css/{page_id}.css.j2',
                self.stylesheets_page.child(f'{page_id}.css')
            ),
        ):
            try:
                template = self._jinja_env.get_template(src_rel_path)
            except jinja2.exceptions.TemplateNotFound:
                pass
            else:
                rendered_template = template.render(full_template_args)
                with open(dest_page.path, 'w') as f:
                    f.write(rendered_template)

    def build (self):
        shutil.rmtree(self.page.path, ignore_errors=True)
        shutil.copytree(self.source_resources_path, self.resources_page.path)
        self.tags = self._init_tags()
        self._jinja_env = self._init_jinja()

        util.log(LOG_TAG, 'start compositions')
        compositions_page.build(self)
