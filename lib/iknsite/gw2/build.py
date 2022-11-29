import logging
import collections
import html

import gw2buildutil

from . import util as gw2util

logger = logging.getLogger(__name__)
PAGE_ID = 'build'
PAGE_ID_PREFIX = 'builds/'
PAGE_TITLE_PREFIX = 'Guild Wars 2 build: '


def build (gw2site):
    textbody_renderer = gw2buildutil.textbody.Renderer(
        gw2buildutil.textbody.RenderFormat.RST_HTML, {'heading level': 3})

    with gw2buildutil.api.storage.FileStorage() as api_storage:
        for build in gw2site.builds.values():
            logger.info(f'render {build.metadata}')
            dest_page_id = PAGE_ID_PREFIX + gw2util.get_build_id(build)
            page_title = PAGE_TITLE_PREFIX + str(build.metadata)

            texts = {}
            if build.intro.description is not None:
                texts['desc'] = textbody_renderer.render(
                    build.intro.description, build.metadata, api_storage)
            if build.notes is not None:
                texts['notes'] = textbody_renderer.render(
                    build.notes, build.metadata, api_storage)
            if build.usage is not None:
                texts['usage'] = textbody_renderer.render(
                    build.usage, build.metadata, api_storage)

            gw2site.render_page_template(PAGE_ID, page_title, {
                'build': build,
                'texts': texts,
            }, dest_page_id=dest_page_id)
