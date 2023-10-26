"""
Generic configuration manager.
Uses PYTHON_ENV to define which configuration file to use. Configuration
files are generic python files with constant definitions. The value defined in
the selected configuration file overrides default configuration.
"""
import imp
import os


def get_by_name(env="default"):
    """
    Returns a module object for a given environment.
    """
    path = os.path.abspath(os.path.dirname(__file__)) + "/" + env + ".py"
    return imp.load_source("*", path)


def update_config(current, env):
    """
    Overloads default configurations.
    """
    diff = get_by_name(env=env)
    new_conf = current

    for attr in dir(diff):
        setattr(new_conf, attr, getattr(diff, attr))

    return new_conf


def get_config():
    """
    Obtain configurations.
    Sets default configurations, and if PYTHON_ENV is defined overloads
    with $PYTHON_ENV.py configurations.
    """
    conf = get_by_name()
    python_env = os.getenv("PYTHON_ENV")

    if python_env:
        conf = update_config(conf, python_env)

    return conf


CONFIG = get_config()
