import datetime as dt

import gi
import logging
from jinja2 import Template

gi.require_version('Notify', '0.7')
from gi.repository import Notify  # noqa

class Notifier:
    def __init__(self, config=None, title_template_path=None, message_template_path=None):
        self._config = config
        self._title_template_path = title_template_path
        self._message_template_path = message_template_path

        self._load_title_template(title_template_path)
        self._load_message_template(message_template_path)

    def _load_title_template(self, template_path):
        template_content = self._load_template(template_path, "{{ alarm.due_date.hour }}:{{ alarm.due_date.minute }} {{alarm.message}}")
        self._title_template = Template(template_content)

    def _load_message_template(self, template_path):
        template_content = self._load_template(template_path, 'Alarm')
        self._message_template = Template(template_content)

    def _load_template(self, template_path, default):
        try:
            with open(template_path, 'r') as myfile:
                template_content = myfile.read()
        except OSError:
            logging.debug(
                f'Template not found at '+str(template_path)+f' - using default template')
            return default
        return template_content

    def show(self, alarm):
        logging.debug(
            f'Notifying of alarm {alarm.id} "{alarm.message}"'+str(alarm))
        title, message = self._format_alarm(alarm)
        n = Notify.Notification.new(title, message)
        self._add_notification_timeout(n)
        n.show()

    def _format_alarm(self, alarm):
        difference = alarm.due_date - alarm.date
        context = {
            "alarm": alarm,
            "in_time": self._format_time_difference(difference),
            "difference": difference,
            "now": dt.datetime.now()
        }

        title = self._format_title(context)
        message = self._format_message(context)

        return [ title, message ]

    def _format_title(self, context):
        return self._title_template.render(context)

    def _format_message(self, context):
        return self._message_template.render(context)

    def _format_time_difference(self, difference):
        if difference < dt.timedelta(minutes=1):
            return ""

        days, remainder = divmod(difference.seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        if seconds > 30:
            minutes += 1

        in_time = [ 'in' ]
        self._pluralize_if_not_zero(in_time, days, 'day')
        self._pluralize_if_not_zero(in_time, hours, 'hour')
        self._pluralize_if_not_zero(in_time, minutes, 'minute')
        return " ".join(in_time)

    def _pluralize_if_not_zero(self, in_time, number, unit):
        if number == 0:
            return
        result = self._pluralize(in_time, number, unit)
        in_time.append(result)

    def _pluralize(self, in_time, number, unit):
        result = str(number)+" "+unit
        if abs(number) > 1:
            result += 's'
        return result

    def _add_notification_timeout(self, notification):
        try:
            config_timeout = self._config['timeout']
        except KeyError:
            logging.debug(f'Using default timeout')
            return

        if config_timeout == "DEFAULT":
            logging.debug(f'Using default timeout')
            return

        if config_timeout == "NEVER":
            logging.debug(f'Timeout: never')
            notification.set_timeout(Notify.EXPIRES_NEVER)
            return

        timeout = int(config_timeout)
        logging.debug(f'Timeout in milliseconds: '+str(timeout) )
        notification.set_timeout(timeout)
