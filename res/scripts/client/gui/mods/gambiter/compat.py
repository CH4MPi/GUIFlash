# -*- coding: utf-8 -*-
"""Cross-realm access to the client's Scaleform view settings registry.

Lesta clients (WoT 1.45 and older) expose the registry as a module level
singleton ``gui.Scaleform.framework.g_entitiesFactories``.

WG clients (WoT 2.4.1) dropped that name from ``gui.Scaleform.framework`` and
keep the very same registry behind the gui loader service: the
``IGuiLoader.entitiesFactory`` property returns a
``gui.impl.gui_factories.GuiEntitiesFactories`` instance which implements the
same ``addSettings``/``removeSettings``/``getSettings`` API.

Both GUIFlash and mods_gui register their views through that registry, so the
lookup lives here - in the lowest layer both of them import.
"""

__all__ = ['getEntitiesFactories', 'addSettings', 'removeSettings']

try:
    # Lesta (RU): module level singleton, present up to 1.45.0.0
    from gui.Scaleform.framework import g_entitiesFactories as _moduleFactories
except ImportError:
    _moduleFactories = None


def getEntitiesFactories():
    """Return the view settings registry of the running client."""
    if _moduleFactories is not None:
        return _moduleFactories
    # WG (EU) 2.4.1: the registry lives in the gui loader service. The service
    # exists before gui mods are imported (game.py configures the dependencies
    # in front of gui_personality.init()), see gui/impl/__init__.py:14.
    from helpers import dependency
    from skeletons.gui.impl import IGuiLoader
    return dependency.instance(IGuiLoader).entitiesFactory


def addSettings(settings):
    return getEntitiesFactories().addSettings(settings)


def removeSettings(alias):
    return getEntitiesFactories().removeSettings(alias)
