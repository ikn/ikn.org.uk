import os
import shutil
import urllib.parse

import jinja2

from . import (
    files as files_page_builder,
    autotemplates as autotemplates_page_builder,
    gw2 as gw2_page_builder,
    util,
)

LOG_TAG = 'site'


class Site:
    def __init__ (self, files_path, dest_path, base_link_path='/'):
        self.files_path = files_path
        self.data_path = os.path.join(self.files_path, 'data')
        self.templates_path = os.path.join(self.files_path, 'templates')

        self.page = util.Page(dest_path, base_link_path)
        self.resources_page = self.page.child('resources')
        self.stylesheets_page = self.resources_page.child('css')
        self.scripts_page = self.resources_page.child('js')
        self.images_page = self.resources_page.child('img')
        self.style_images_page = self.images_page.child('style')

    def link (self, rel_path):
        return urllib.parse.quote(self.page.child(rel_path).link)

    def _init_jinja (self):
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.templates_path))

    def render_template (self, src_rel_path, dest_page, template_args={}):
        full_template_args = {'site': self, 'util': util}
        full_template_args.update(template_args)

        template = self._jinja_env.get_template(src_rel_path)
        rendered_template = template.render(full_template_args)
        dest_page.create_parent()
        with open(dest_page.path, 'w') as f:
            f.write(rendered_template)

    def render_page_template (self, page_id, page_title,
                              template_args={}, js_deps=()):
        full_template_args = {
            'page_id': page_id, 'page_title': page_title,
            'js_deps': js_deps,
        }
        full_template_args.update(template_args)

        for src_rel_path, dest_page in (
            (
                f'css/{page_id}.css.j2',
                self.stylesheets_page.child(f'{page_id}.css')
            ),
            (
                f'js/{page_id}.js.j2',
                self.scripts_page.child(f'{page_id}.js')
            ),
            (
                f'page/{page_id}.html.j2',
                self.page.child(f'{page_id}/index.html')
            ),
        ):
            try:
                self.render_template(
                    src_rel_path, dest_page, full_template_args)
            except jinja2.exceptions.TemplateNotFound:
                pass

    def build (self):
        shutil.rmtree(self.page.path, ignore_errors=True)
        self._jinja_env = self._init_jinja()

        for page_builder in (
            files_page_builder,
            autotemplates_page_builder,
            gw2_page_builder,
        ):
            util.log(LOG_TAG, f'start {page_builder.PAGE_ID}')
            page_builder.build(self)
