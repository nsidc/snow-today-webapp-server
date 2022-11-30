"""Invoke tasks."""

from invoke import Collection

from . import env
from . import format
from . import test

ns = Collection()
ns.add_collection(env)
ns.add_collection(format)
ns.add_collection(test)
