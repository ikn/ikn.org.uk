import enum
import os
import sys

from PIL import Image


def log (tag, *args):
    print(f'[\033[1;34m{tag}\033[0m]', *args, file=sys.stderr)


class Page:
    def __init__ (self, path, link):
        self.path = os.path.realpath(path)
        self.link = '/' + '/'.join(part for part in link.split('/') if part)

    def child (self, rel_path):
        return Page(os.path.join(self.path, rel_path),
                    self.link + '/' + rel_path)

    def create (self):
        os.makedirs(self.path, exist_ok=True)

    def create_parent (self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def exists (self):
        return os.path.exists(self.path)

    def as_image (self):
        return ImagePage(self.path, self.link)


class ImagePage (Page):
    def __init__ (self, path, link):
        Page.__init__(self, path, link)
        with Image.open(self.path) as image:
            self.width, self.height = image.size


class JsDependencies (enum.Enum):
    JQUERY = 'jquery-3.5.1.slim.min'
    UTIL = 'util'


class License:
    def __init__ (self, name, url):
        self.name = name
        self.url = url


class Licenses (enum.Enum):
    GPL_V2 = License('GPL2', 'https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html')
    GPL_V3 = License('GPL3', 'https://www.gnu.org/licenses/gpl-3.0-standalone.html')
    LGPL_V3 = License('LGPL3', 'https://www.gnu.org/licenses/lgpl-3.0.txt')
    BSD_NEW = License('BSD-new', 'http://www.opensource.org/licenses/BSD-3-Clause')
    EXPAT = License('Expat', 'http://www.opensource.org/licenses/mit-license.php')
    CC_BY_SA_V3 = License('CC BY-SA 3.0', 'http://creativecommons.org/licenses/by-sa/3.0/')
    CC_BY_NC_SA_V3 = License('CC BY-NC-SA 3.0', 'https://creativecommons.org/licenses/by-nc-sa/3.0/')
    CC0_V1 = License('CC0 1.0', 'http://creativecommons.org/publicdomain/zero/1.0/')
    MIR_OS = License('MirOS', 'https://www.mirbsd.org/MirOS-Licence')
    APACHE = License('Apache', 'http://www.apache.org/licenses/LICENSE-2.0.txt')
