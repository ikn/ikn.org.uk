class Tag:
    def __init__ (self, gw2site, name, icon):
        self.name = name
        self.icon_page = (
            gw2site.icons_page.child(icon + '.png').as_image())


def get_build_tags (gw2site, build):
    tag_names = []

    if build.metadata.elite_spec is not None:
        tag_names.append(build.metadata.elite_spec.id_)
    else:
        tag_names.append(build.metadata.profession.id_)

    tag_names.extend(build.metadata.labels)

    used_names = set()
    for name in tag_names:
        if name not in used_names and name in gw2site.tags:
            yield gw2site.tags[name]
        used_names.add(name)


def get_text_build_tags (gw2site, build):
    return ', '.join(name for name in build.metadata.labels
                     if name not in gw2site.tags)
