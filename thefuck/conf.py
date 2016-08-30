from copy import copy
from imp import load_source
import os
import sys
from six import text_type
from . import logs


class RulesNamesList(list):
    """Wrapper a top of list for string rules names."""

    def __contains__(self, item):
        return super(RulesNamesList, self).__contains__(item.name)


class _DefaultRulesNames(RulesNamesList):
    def __add__(self, items):
        return _DefaultRulesNames(list(self) + items)

    def __contains__(self, item):
        return item.enabled_by_default or \
               super(_DefaultRulesNames, self).__contains__(item)

    def __eq__(self, other):
        if isinstance(other, _DefaultRulesNames):
            return super(_DefaultRulesNames, self).__eq__(other)
        else:
            return False


DEFAULT = _DefaultRulesNames([])


class Settings(object):
    def __init__(self, conf):
        self._conf = conf

    def __getattr__(self, item):
        return self._conf.get(item)

    def update(self, **kwargs):
        """Returns new settings with new values from `kwargs`."""
        conf = copy(self._conf)
        conf.update(kwargs)
        return Settings(conf)


DEFAULT_SETTINGS = {'rules': DEFAULT,
                    'wait_command': 3,
                    'require_confirmation': False,
                    'no_colors': False}

ENV_TO_ATTR = {'THEFUCK_RULES': 'rules',
               'THEFUCK_WAIT_COMMAND': 'wait_command',
               'THEFUCK_REQUIRE_CONFIRMATION': 'require_confirmation',
               'THEFUCK_NO_COLORS': 'no_colors'}


def _settings_from_file(user_dir):
    """Loads settings from file."""
    settings = load_source('settings',
                           text_type(user_dir.joinpath('settings.py')))
    return {key: getattr(settings, key)
            for key in DEFAULT_SETTINGS.keys()
            if hasattr(settings, key)}


def _rules_from_env(val):
    """Transforms rules list from env-string to python."""
    val = val.split(':')
    if 'DEFAULT' in val:
        val = DEFAULT + [rule for rule in val if rule != 'DEFAULT']
    return val


def _val_from_env(env, attr):
    """Transforms env-strings to python."""
    val = os.environ[env]
    if attr == 'rules':
        val = _rules_from_env(val)
    elif attr == 'wait_command':
        val = int(val)
    elif attr in ('require_confirmation', 'no_colors'):
        val = val.lower() == 'true'
    return val


def _settings_from_env():
    """Loads settings from env."""
    return {attr: _val_from_env(env, attr)
            for env, attr in ENV_TO_ATTR.items()
            if env in os.environ}


def get_settings(user_dir):
    """Returns settings filled with values from `settings.py` and env."""
    conf = copy(DEFAULT_SETTINGS)
    try:
        conf.update(_settings_from_file(user_dir))
    except Exception:
        logs.exception("Can't load settings from file",
                       sys.exc_info(),
                       Settings(conf))

    try:
        conf.update(_settings_from_env())
    except Exception:
        logs.exception("Can't load settings from env",
                       sys.exc_info(),
                       Settings(conf))

    if not isinstance(conf['rules'], RulesNamesList):
        conf['rules'] = RulesNamesList(conf['rules'])

    return Settings(conf)
