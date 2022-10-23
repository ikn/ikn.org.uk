from . import releases


class Projects:
    def __init__ (self, site):
        self.releases = releases.get_releases(site)
