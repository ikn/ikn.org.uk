import os
import json
import shutil

PAGE_ID = 'doc'


def build (site):
    config_path = os.path.join(site.data_path, 'doc.json')
    with open(config_path) as config_f:
        config = json.load(config_f)
    for doc in config:
        shutil.copytree(os.path.expanduser(doc['src path']),
                        site.page.child(doc['dest path']).path)
