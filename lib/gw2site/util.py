import enum
import os
import sys
import pprint

from PIL import Image


def log (tag, *args):
    print(f'[\033[1;34m{tag}\033[0m]', *args, file=sys.stderr)


def _get_path (env_var, default_rel_path, app_name):
    default_path = os.path.join(os.path.expanduser('~'), default_rel_path)
    raw_path = os.environ.get(env_var, default_path)
    path = os.path.realpath(os.path.join(raw_path, app_name))
    os.makedirs(path, exist_ok=True)
    return path


def get_cache_path (app_name):
    return _get_path('XDG_CACHE_HOME', '.cache', app_name)


def get_resources_path (site):
    return resources_path


class Page:
    def __init__ (self, path, link):
        self.path = os.path.realpath(path)
        self.link = '/' + '/'.join(part for part in link.split('/') if part)

    def child (self, rel_path):
        return Page(os.path.join(self.path, rel_path),
                    self.link + '/' + rel_path)

    def create (self):
        os.makedirs(self.path, exist_ok=True)

    def as_image (self):
        return ImagePage(self.path, self.link)


class ImagePage (Page):
    def __init__ (self, path, link):
        Page.__init__(self, path, link)
        with Image.open(self.path) as image:
            self.width, self.height = image.size


class JsDependency (enum.Enum):
    JQUERY = 'jquery-3.5.1.slim.min'
    UTIL = 'util'


class Tag:
    def __init__ (self, site, name, build_icon):
        self.name = name
        self.build_icon_page = (
            site.build_icons_page.child(build_icon + '.png').as_image())


def get_build_tags (site, build):
    tag_names = []

    prof = build.metadata.profession
    if prof.elite_spec is not None:
        tag_names.append(prof.elite_spec)
    else:
        tag_names.append(prof.profession)

    tag_names.extend(build.metadata.labels)

    used_names = set()
    for name in tag_names:
        if name not in used_names and name in site.tags:
            yield site.tags[name]
        used_names.add(name)
