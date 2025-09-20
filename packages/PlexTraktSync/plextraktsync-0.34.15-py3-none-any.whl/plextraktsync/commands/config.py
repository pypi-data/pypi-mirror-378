from __future__ import annotations

from plextraktsync.factory import factory


def dump(data, print=None):
    """
    Print config serialized as yaml.
    If print is None, return the produced string instead.
    """
    from plextraktsync.config.ConfigLoader import ConfigLoader

    dump = ConfigLoader.dump_yaml(None, data)
    if print is None:
        return dump
    print(dump)


def config(urls_expire_after: bool, edit: bool, locate: bool):
    config = factory.config
    print = factory.print

    if edit or locate:
        import click

        click.launch(config.config_yml, locate=locate)
        return

    if urls_expire_after:
        print("# HTTP Cache")
        dump(config.http_cache.serialize(), print=print)
        return

    print(f"# Config File: {config.config_yml}")
    dump(config.serialize(), print=print)
