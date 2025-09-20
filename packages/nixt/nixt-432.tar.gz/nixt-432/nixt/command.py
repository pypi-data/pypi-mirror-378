# This file is placed in the Public Domain.


"loading on demand"


import inspect
import logging
import os


from .brokers import Fleet
from .methods import parse
from .package import Mods, getmod, modules
from .utility import md5sum


DEBUG = False


class Commands:

    cmds = {}
    names = {}

    @staticmethod
    def add(func) -> None:
        name = func.__name__
        modname = func.__module__.split(".")[-1]
        Commands.cmds[name] = func
        Commands.names[name] = modname

    @staticmethod
    def get(cmd):
        func = Commands.cmds.get(cmd, None)
        if func:
            return func
        name = Commands.names.get(cmd, None)
        if not name:
            return
        module = getmod(name)
        if not module:
            return
        scan(module)
        if DEBUG:
            module.DEBUG = True
        return Commands.cmds.get(cmd, None)


def command(evt):
    parse(evt)
    func = Commands.get(evt.cmd)
    if func:
        func(evt)
        Fleet.display(evt)
    evt.ready()


def scan(module):
    for key, cmdz in inspect.getmembers(module, inspect.isfunction):
        if key.startswith("cb"):
            continue
        if 'event' in inspect.signature(cmdz).parameters:
            Commands.add(cmdz)


def scanner(names=None):
    res = []
    if not os.path.exists(Mods.mod):
        logging.info("modules directory is not set.")
        return
    logging.info("scanning %s", Mods.mod)
    for nme in sorted(modules()):
        if names and nme not in spl(names):
            continue
        module = getmod(nme)
        if not module:
            continue
        scan(module)
        res.append(module)
    return res


def table(checksum=""):
    pth = os.path.join(Mods.mod, "tbl.py")
    if os.path.exists(pth):
        if checksum and md5sum(pth) != checksum:
            logging.warning("table checksum error.")
    tbl = getmod("tbl")
    if tbl and "NAMES" in dir(tbl):
        Commands.names.update(tbl.NAMES)
    else:
        scanner()


def __dir__():
    return (
        'Commands',
        'command',
        'scan',
        'scanner',
        'table'
    )
