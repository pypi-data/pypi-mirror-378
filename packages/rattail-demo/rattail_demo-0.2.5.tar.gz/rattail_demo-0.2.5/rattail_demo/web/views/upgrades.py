# -*- coding: utf-8; -*-
"""
Upgrade views
"""

import re

from tailbone.views import upgrades as base


class UpgradeView(base.UpgradeView):

    def get_changelog_projects(self):
        projects = super(UpgradeView, self).get_changelog_projects()

        projects.update({
            'rattail_demo': {
                'commit_url': 'https://forgejo.wuttaproject.org/rattail/rattail-demo/compare/{{old_version}}...{{new_version}}',
                'release_url': 'https://forgejo.wuttaproject.org/rattail/rattail-demo/src/tag/v{{new_version}}/CHANGELOG.md',
            },
        })

        return projects


def includeme(config):
    base.defaults(config, **{'UpgradeView': UpgradeView})
