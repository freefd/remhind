import asyncio
import argparse
import logging
import pathlib

import gi
import toml
from xdg import BaseDirectory

from .monitor import monitor_calendars
from .events import check_events, CalendarStore, display_test_event
from .notification import Notifier

gi.require_version('Notify', '0.7')
from gi.repository import Notify  # noqa


async def monitor_file_events(args):
    with args.config.open() as fd:
        config = toml.load(fd)

    log_level = max(logging.CRITICAL - args.verbose * 10, logging.NOTSET)
    logging.basicConfig(
        format='%(asctime)s:%(levelname)s:%(message)s', level=log_level)
    Notify.init('remhind')

    try:
        notifications_config = config['notifications']
    except KeyError:
        notifications_config = {}
    notifier = Notifier(notifications_config, args.title_template, args.message_template)

    if args.action == "test":
        display_test_event(notifier, args.in_minutes)
        return

    calendars = CalendarStore(config['calendars'].values(), args.database,
                              notifications_config)

    events_checker = check_events(notifier, calendars)
    calendars_monitor = monitor_calendars(config['calendars'], calendars)
    await asyncio.gather(events_checker, calendars_monitor)


def main():
    parser = argparse.ArgumentParser(description="remind event from vdirs")
    parser.add_argument('action', default="run", nargs='?', choices=[
        "run",
        "test",
    ])
    parser.add_argument('-c', '--config', type=pathlib.Path,
        default=BaseDirectory.xdg_config_home +  '/remhind/config')
    parser.add_argument('-t', '--title-template', type=pathlib.Path,
        default=BaseDirectory.xdg_config_home + '/remhind/title.j2')
    parser.add_argument('-m', '--message-template', type=pathlib.Path,
        default=BaseDirectory.xdg_config_home + 'remhind/message.j2')
    parser.add_argument('-d', '--database', type=pathlib.Path,
        default=BaseDirectory.xdg_cache_home + 'remhind.db')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('--in-minutes', default=5)

    asyncio.run(monitor_file_events(parser.parse_args()))


if __name__ == '__main__':
    main()
