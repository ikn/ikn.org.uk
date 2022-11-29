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


def get_build_id (build):
    m = build.metadata
    parts = []
    if m.game_mode is not None:
        parts.append(m.game_mode.value.id_)
    spec = m.profession if m.elite_spec is None else m.elite_spec
    parts.append(spec.id_)
    parts.extend(m.labels)
    return '-'.join(parts).replace(' ', '-')


def get_build_page (site, build):
    return site.page.child('gw2/builds').child(get_build_id(build))
