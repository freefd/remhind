# remhind

A notification daemon of events stored in directories

Those directories will be monitored for change in order to allow you to use
solution like [vdirsyncer](https://github.com/pimutils/vdirsyncer) to sync your
CalDAV server with your local filesystem.

## Installing

`remhind` can be installed through PyPI using pip.

```sh
pip install remhind
```

## Getting Started

`remhind` use a [toml](https://github.com/toml-lang/toml) configuration file
indicating which directories holds your event files. Here's a simple example:

```toml
[calendars]
    [calendars.test]
    name = "Test"
    path = "~/projets/perso/remhind/test_calendar"
```

### Default alerts

`remhind` displays notification for calendar events even if they don't have an
alert set. By deafult his happens at the time the event starts but can
be configured in the configuration file as in the following example.  
Note that the default is `[ 0 ]` and you have to include `0` in your
configuration if you want an alert at the time of the event.

```toml
[notifications]
    alert_before_event_minutes = [ 15, 5, 0 ]
[calendars]
    [calendars.test]
    name = "Test"
    path = "~/projets/perso/remhind/test_calendar"
```

### Notification timeout

You can can specify a timeout for your notifications in the config file. Allowed
values are

- `DEFAULT` - Use your notification tools' default timeout. This is the same as
    not setting any option
- `NEVER` - Notification will be displayed until clicked away
- 5000 - A number will be interpreted as timeout in milliseconds. The
    notification will automatically disappear after this time.

```toml
[notifications]
    timeout = "NEVER"
[calendars]
    [calendars.test]
    name = "Test"
    path = "~/projets/perso/remhind/test_calendar"
```

### Notification templates

If you are not satisfied with the look of the default notifications you can
style them yourself. The template engine is [jinja2](https://jinja.palletsprojects.com/)
and the template files used can be specied with the `--title-template` and
`--message-template` argument.  
They default to `~/.config/remhind/title.j2` and `~/config/remhind/message.j2`

- `alarm`: alarm,
- `in_time`: "in X days Y hours Z minutes" - a human readable version of difference,
- `difference`: shorthand for alarm.due_date - alarm.date
- `now`: datetime.now()

If no template file is given the following templates will be used

title

```jinja2
{{ alarm.due_date.hour }}:{{ alarm.due_date.minute }} {{alarm.message}}
```

message

```jinja2
Alarm
```

## Acknowledgments

This work has been inspired by the work of the [pimutils group](https://github.com/pimutils)
