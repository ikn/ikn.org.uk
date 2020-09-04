import os
import shutil

PAGE_ID = 'files'


def build (site):
    shutil.copytree(os.path.join(site.files_path, 'files'), site.page.path)
