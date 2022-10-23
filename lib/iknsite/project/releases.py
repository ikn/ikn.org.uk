import os
import json
import glob
import hashlib
import subprocess
import logging

from .. import util

logger = logging.getLogger(__name__)


RELEASE_TYPES = [
    {'name': 'source', 'filename': '{project}-{version}.tar.gz'},
    {'name': 'Windows binary', 'filename': '{project}-win-{version}.zip'},
    {'name': 'Flash binary', 'filename': '{project}-{version}.swf'},
]

CHANGES_NAMES = ['CHANGES', 'CHANGES.md', 'ChangeLog']


class ReleaseData:
    def __init__ (self, version, date, type_, file_page, changes_page, sha256):
        self.version = version
        self.date = date
        self.type_ = type_
        self.file_page = file_page
        self.changes_page = changes_page
        self.sha256 = sha256


class Release:
    def __init__ (self, version, date, changes):
        self.version = version
        self.date = date
        self.changes = changes

    @staticmethod
    def project_name (page_id):
        return page_id.split('/')[-1]

    def for_page (self, site, page_id):
        project_page = site.page.child('download').child(page_id)
        project_name = Release.project_name(page_id)
        changes_page = None
        found = False

        for type_ in RELEASE_TYPES:
            file_page = project_page.child(type_['filename'].format(
                project=project_name, version=self.version))
            if file_page.exists():
                found = True
                sha256 = (util.hash_file(hashlib.sha256(), file_page.path)
                          .hexdigest())

                if self.changes is not None and changes_page is None:
                    changes_page = project_page.child(
                        f'{project_name}-changes-{self.version}.txt')
                    changes_page.create_parent()
                    with open(changes_page.path, 'w') as f:
                        f.write(self.changes)

                yield ReleaseData(self.version, self.date, type_['name'],
                                  file_page, changes_page, sha256)
        if not found:
            raise RuntimeError(
                f'no files found for {project_name} release {self.version}')


class Releases:
    def __init__ (self, releases):
        self._releases = releases

    def get (self, page_id):
        return self._releases[Release.project_name(page_id)]

    def get_latest (self, site, page_id):
        return self.get(page_id)[0].for_page(site, page_id)

    def get_old (self, site, page_id):
        for r in self.get(page_id)[1:]:
            yield from r.for_page(site, page_id)


def get_data (site):
    data_path = os.path.join(site.data_path, 'project.json')
    with open(data_path) as f:
        return json.load(f)


def get_src_paths (data):
    by_name = {}
    for cat in data['repository paths']:
        for src in glob.iglob(os.path.join(cat, '*', 'src')):
            by_name[os.path.basename(os.path.dirname(src))] = src
    return by_name


def git (path, *args):
    try:
        return subprocess.check_output(
            ['git', '--git-dir=' + os.path.join(path, '.git')] + list(args),
            stderr=subprocess.DEVNULL
        ).decode()
    except subprocess.CalledProcessError as e:
        if e.returncode == 128:
            # not a git project
            return None
        else:
            raise e


def get_git_tags (src_path):
    output = git(src_path, 'tag',
                 '--format=%(refname:lstrip=-1) %(committerdate:short)')
    if output is not None:
        for line in output.splitlines():
            parts = line.split(' ')
            yield {'version': parts[0], 'date': parts[1]}


def get_changes (src_path, version):
    for name in CHANGES_NAMES:
        full_text = git(src_path, 'show', f'{version}:{name}')
        if full_text is not None and full_text.strip():
            return full_text
    return None


def get_project_releases (site, data, name, src_path):
    tags = list(get_git_tags(src_path))
    changes = {tag['version']: get_changes(src_path, tag['version'])
               for tag in tags}
    num_changes = len([c for c in changes.values() if c is not None])
    logger.info(f'{name}: {len(tags)} releases, {num_changes} changes')
    releases = []
    for tag in tags:
        releases.append(Release(
            tag['version'], tag['date'], changes[tag['version']]))

    sort_key = lambda r: util.parse_version(
        r.version, data['version overrides'].get(name, {}))
    return sorted(releases, key=sort_key, reverse=True)


def get_releases (site):
    releases = {}
    data = get_data(site)
    src_paths = get_src_paths(data)
    logger.info(f'{len(src_paths)} projects')
    for name, src_path in src_paths.items():
        releases[name] = get_project_releases(site, data, name, src_path)
    return Releases(releases)
