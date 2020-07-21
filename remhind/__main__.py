import asyncio
import argparse
import logging
import pathlib

import gi
import toml
from xdg import XDG_CONFIG_HOME, XDG_CACHE_HOME

from .monitor import monitor_calendars
from .events import check_events, CalendarStore

gi.require_version('Notify', '0.7')
from gi.repository import Notify  # noqa


async def monitor_file_events(args):
    with args.config.open() as fd:
        config = toml.load(fd)

    log_level = max(logging.CRITICAL - args.verbose * 10, logging.NOTSET)
    logging.basicConfig(
        format='%(asctime)s:%(levelname)s:%(message)s', level=log_level)
    Notify.init('remhind')

    calendars = CalendarStore(config['calendars'].values(), args.database)

    try:
        notifications_config = config['notifications']
    except KeyError:
        notifications_config = {}

    events_checker = check_events(notifications_config, calendars)
    calendars_monitor = monitor_calendars(config['calendars'], calendars)
    await asyncio.gather(events_checker, calendars_monitor)


def main():
    parser = argparse.ArgumentParser(description="remind event from vdirs")
    parser.add_argument('-c', '--config', type=pathlib.Path,
        default=XDG_CONFIG_HOME / 'remhind' / 'config')
    parser.add_argument('-d', '--database', type=pathlib.Path,
        default=XDG_CACHE_HOME / 'remhind.db')
    parser.add_argument('-v', '--verbose', action='count', default=0)

    asyncio.run(monitor_file_events(parser.parse_args()))


if __name__ == '__main__':
    main()
