# pylint: disable=blacklisted-name

import logging
import pytest
from os.path import abspath, dirname

from mock import MagicMock

import gluetool

from . import create_module, testing_asset


class DummyModule(gluetool.Module):
    """
    Dummy module for testing _parse_config
    """

    name = 'Dummy module'

    options = {
        'foo': {},
        'bar': {}
    }


@pytest.fixture(name='module')
def fixture_module():
    return create_module(DummyModule)[1]


def test_parse(module):
    """
    This test will check that ${config_root} is correctly replaced.
    gluetool passes an absolute path to _parse_config.
    The configuration dir has this structure:
    config_root/config/module_config_file
    """

    path = abspath(testing_asset('parse_config', 'configroot', 'config', 'data_config_root_a'))

    module._parse_config([path])

    foo_data = "\n".join([
        "pre-artifact-installation:${config_root}/pre-artifact-installation-playbooks-map.yaml,",
        "pre-artifact-installation-workarounds:~/.citool.d/pre-artifact-installation-workarounds-playbooks-map.yaml,",
        "post-artifact-installation:${config_root}/post-artifact-installation-playbooks-map.yaml"
    ])

    foo_data = foo_data.replace("${config_root}", dirname(dirname(path)))

    assert module.option('foo') == foo_data
    # bar is not in the config files
    assert module.option('bar') is None
    assert module.glue.module_config_roots == {
        'dummy-module': dirname(dirname(path))
    }


def test_not_unicode(module):
    """
    This test will check that string options are not unicode in python-2.7.
    In python-3.x, unicode have str type, so this test will always pass.
    """

    path = abspath(testing_asset('parse_config', 'configroot', 'config', 'data_not_unicode'))

    module._parse_config([path])

    assert isinstance(module.option('foo'), str)
    assert isinstance(module.option('bar'), str)
    assert module.glue.module_config_roots == {
        'dummy-module': dirname(dirname(path))
    }


def test_overwrite(module, log):
    """
    Multiple configuration files may be specified. This test is to check that
    the latter files overwrite values of the former files.
    """

    config_path_first = abspath(testing_asset('parse_config', 'configroot', 'config', 'data_config_root_a'))
    config_path_second = abspath(testing_asset('parse_config', 'configroot', 'config', 'data_config_root_b'))

    paths = [
        config_path_first,
        config_path_second
    ]

    module._parse_config(paths)

    foo_data = "\n".join([
        "pre-artifact-installation:${config_root}/pre-artifact-installation-playbooks-map.yaml,",
        "pre-artifact-installation-workarounds:~/.citool.d/pre-artifact-installation-workarounds-playbooks-map.yaml,",
        "post-artifact-installation:${config_root}/post-artifact-installation-playbooks-map.yaml_overwrite"
    ])

    foo_data = foo_data.replace("${config_root}", dirname(dirname(paths[1])))

    assert module.option('foo') == foo_data
    # bar is not in the config files
    assert module.option('bar') is None
    assert module.glue.module_config_roots == {
        'dummy-module': dirname(dirname(config_path_second))
    }
    assert log.match(
        levelno=logging.WARNING,
        message="module '{}' config root reset to '{}'".format(
            module.unique_name,
            dirname(dirname(config_path_second))
        )
    )


def test_separate_dir(module, log):
    """
    data_config_root_a has a key 'bar' with value containing '${config_root}'
    data_config_root_b does not have 'bar' item. So most certainly, the
    '${config_root}' for this value should be replaced by the root dir of
    data_config_root_a.
    """

    paths = [
        abspath(testing_asset('parse_config', 'configroota', 'config', 'data_config_root_a')),
        abspath(testing_asset('parse_config', 'configrootb', 'config', 'data_config_root_b'))
    ]

    module._parse_config(paths)

    foo_data = "\n".join([
        "pre-artifact-installation:${config_root}/pre-artifact-installation-playbooks-map.yaml,",
        "pre-artifact-installation-workarounds:~/.citool.d/pre-artifact-installation-workarounds-playbooks-map.yaml,",
        "post-artifact-installation:${config_root}/post-artifact-installation-playbooks-map.yaml_overwrite"
    ])

    bar_data = "${config_root}/another_value"

    foo_data = foo_data.replace("${config_root}", dirname(dirname(paths[1])))
    bar_data = bar_data.replace("${config_root}", dirname(dirname(paths[0])))

    assert module.option('foo') == foo_data
    # bar is in the data_config_root_a
    assert module.option('bar') == bar_data

    assert log.match(
        levelno=logging.WARNING,
        message="module '{}' config root reset to '{}'".format(
            module.unique_name,
            dirname(dirname(paths[0]))
        )
    )
    assert log.match(
        levelno=logging.WARNING,
        message="module '{}' config root reset to '{}'".format(
            module.unique_name,
            dirname(dirname(paths[1]))
        )
    )
