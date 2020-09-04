import os

from . import util

LOG_TAG = 'autotemplates'
PAGE_ID = 'autotemplates'


def build (site):
    templates_path = os.path.abspath(os.path.join(site.templates_path, 'auto'))

    for path, dirs, files in os.walk(templates_path):
        for filename in files:
            src_path = os.path.abspath(os.path.join(path, filename))
            rel_path = os.path.relpath(src_path, templates_path)

            if filename.startswith('.'):
                util.log(LOG_TAG, f'skipping hidden file: {rel_path}')
                continue
            elif rel_path.endswith('.html.j2'):
                page_id = rel_path[:-len('.html.j2')]
                if page_id == 'index' or page_id.endswith('/index'):
                    dest_rel_path = f'{page_id}.html'
                else:
                    dest_rel_path = f'{page_id}/index.html'
                template_args = {'page_id': page_id}
            elif rel_path.endswith('.j2'):
                dest_rel_path = rel_path[:-len('.j2')]
                template_args = {}
            else:
                raise ValueError(f'not a template: {rel_path}')
            dest_page = site.page.child(dest_rel_path)

            util.log(LOG_TAG, f'render {rel_path}')
            site.render_template(f'auto/{rel_path}', dest_page, template_args)
