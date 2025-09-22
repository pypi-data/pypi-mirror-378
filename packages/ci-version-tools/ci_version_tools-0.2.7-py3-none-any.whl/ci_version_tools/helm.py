import pathlib

import semver
import yaml


def get_helm_chart_version(chart_yaml_path: pathlib.Path) -> semver.Version:
    with open(chart_yaml_path) as f:
        chart = yaml.safe_load(f)

    return semver.Version.parse(chart["version"])
