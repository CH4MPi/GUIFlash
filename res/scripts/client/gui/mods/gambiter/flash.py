# -*- coding: utf-8 -*-

__all__ = ['COMPONENT_TYPE', 'COMPONENT_ALIGN', 'COMPONENT_EVENT']

import codecs
import json

import GUI

import BattleReplay
import Event
# 'TODO' WOT V.1.10.1.0'
from frameworks.wulf import WindowLayer
from gui import g_guiResetters
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates
# from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.personality import ServicesLocator
from helpers import dependency
from skeletons.gui.app_loader import GuiGlobalSpaceID as SPACE_ID
from skeletons.gui.battle_session import IBattleSessionProvider
from utils import LOG_NOTE, LOG_DEBUG, LOG_ERROR


class CONSTANTS(object):
    FILE_NAME = 'GUIFlash.swf'
    VIEW_ALIAS = 'GUIFlash'


class COMPONENT_TYPE(object):
    PANEL = 'Panel'
    LABEL = 'Label'
    IMAGE = 'Image'
    SHAPE = 'Shape'


ALL_COMPONENT_TYPES = (COMPONENT_TYPE.PANEL, COMPONENT_TYPE.LABEL, COMPONENT_TYPE.IMAGE, COMPONENT_TYPE.SHAPE)


class COMPONENT_ALIGN(object):
    LEFT = 'left'
    RIGHT = 'right'
    CENTER = 'center'
    TOP = "top"
    BOTTOM = 'bottom'


class COMPONENT_STATE(object):
    INIT = 1
    LOAD = 2
    UNLOAD = 3
    DESTROY = 4


class COMPONENT_EVENT(object):
    LOADED = Event.Event()
    UPDATED = Event.Event()
    UNLOADED = Event.Event()


class Cache(object):

    def __init__(self):
        self.components = {}

    def create(self, alias, type, props):
        LOG_DEBUG("Create cache: '%s' [%s] -> Properties: %s" % (alias, type, props))
        self.components[alias] = {'type': type, 'props': props}

    def update(self, alias, props):
        LOG_DEBUG("Change cache: '%s' -> Properties: %s" % (alias, props))
        self.components[alias].get('props').update(props)

    def delete(self, alias):
        LOG_DEBUG("Destroy cache: '%s'" % alias)
        del self.components[alias]

    def isComponent(self, alias):
        return alias in self.components

    def getComponent(self, alias=None):
        if alias is None:
            return self.components
        return self.components.get(alias)

    def getKeys(self):
        return sorted(self.components.keys())

    def getCustomizedType(self, type):
        return ''.join(type.split()).capitalize()

    def isTypeValid(self, type):
        return type in ALL_COMPONENT_TYPES

    # ..
    def readConfig(self, file):
        LOG_DEBUG("Read config from file '%s'." % file)
        with open(file, "r") as file:
            data = json.load(file)
        return data

    # ..
    def saveConfig(self, file, data):
        LOG_DEBUG("Save config in file '%s'." % file)
        with open(file, 'wb') as file:
            json.dump(data, codecs.getwriter('utf-8')(file), indent=4, sort_keys=True, ensure_ascii=False)


class Views(object):

    def __init__(self):
        self.ui = None

    def createAll(self):
        for alias in g_guiCache.getKeys():
            component = g_guiCache.getComponent(alias)
            self.create(alias, component.get('type'), component.get('props'))

    def create(self, alias, type, props):
        if self.ui is not None:
            LOG_DEBUG("Create component: '%s' [%s] -> Properties: %s" % (alias, type, props))
            self.ui.as_createS(alias, type, props)

    def update(self, alias, props, params):
        if self.ui is not None:
            LOG_DEBUG("Change component: '%s' -> Properties: %s | Parameters: %s" % (alias, props, params))
            self.ui.as_updateS(alias, props, params)

    def delete(self, alias):
        if self.ui is not None:
            LOG_DEBUG("Destroy component: '%s'" % alias)
            self.ui.as_deleteS(alias)

    def resize(self):
        if self.ui is not None:
            width, height = GUI.screenResolution()
            self.ui.as_resizeS(width, height)

    def cursor(self, isShow):
        if self.ui is not None:
            self.ui.as_cursorS(isShow)

    def radialMenu(self, isShow):
        if self.ui is not None:
            self.ui.as_radialMenuS(isShow)

    def fullStats(self, isShow):
        if self.ui is not None:
            self.ui.as_fullStatsS(isShow)

    def fullStatsQuestProgress(self, isShow):
        if self.ui is not None:
            self.ui.as_fullStatsQuestProgressS(isShow)

    def epicMapOverlayVisibility(self, isShow):
        if self.ui is not None:
            self.ui.as_epicMapOverlayVisibilityS(isShow)

    def epicRespawnOverlayVisibility(self, isShow):
        if self.ui is not None:
            self.ui.as_epicRespawnOverlayVisibilityS(isShow)


class Hooks(object):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _start(self):
        ServicesLocator.appLoader.onGUISpaceEntered += self.__onGUISpaceEntered
        ServicesLocator.appLoader.onGUISpaceLeft += self.__onGUISpaceLeft

    def _destroy(self):
        ServicesLocator.appLoader.onGUISpaceEntered -= self.__onGUISpaceEntered
        ServicesLocator.appLoader.onGUISpaceLeft -= self.__onGUISpaceLeft

    def _populate(self):
        g_eventBus.addListener(events.GameEvent.SHOW_CURSOR, self.__handleShowCursor, EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.addListener(events.GameEvent.HIDE_CURSOR, self.__handleHideCursor, EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.addListener(events.GameEvent.RADIAL_MENU_CMD, self.__toggleRadialMenu, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(events.GameEvent.FULL_STATS, self.__toggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(events.GameEvent.FULL_STATS_QUEST_PROGRESS, self.__toggleFullStatsQuestProgress, scope=EVENT_BUS_SCOPE.BATTLE)
        g_guiResetters.add(self.__onResizeStage)
        ctrl = self.sessionProvider.dynamic.maps
        # TODO: check for bonusType?!
        if ctrl and hasattr(ctrl, 'onVisibilityChanged'):
            ctrl.onVisibilityChanged += self.__onMapVisibilityChanged
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnVisibilityChanged += self.__onRespawnVisibilityChanged

    def _dispose(self):
        g_eventBus.removeListener(events.GameEvent.SHOW_CURSOR, self.__handleShowCursor, EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.removeListener(events.GameEvent.HIDE_CURSOR, self.__handleHideCursor, EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.removeListener(events.GameEvent.RADIAL_MENU_CMD, self.__toggleRadialMenu, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(events.GameEvent.FULL_STATS, self.__toggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(events.GameEvent.FULL_STATS_QUEST_PROGRESS, self.__toggleFullStatsQuestProgress, scope=EVENT_BUS_SCOPE.BATTLE)
        g_guiResetters.discard(self.__onResizeStage)

        ctrl = self.sessionProvider.dynamic.maps
        # TODO: check for bonusType?!
        if ctrl and hasattr(ctrl, 'onVisibilityChanged'):
            ctrl.onVisibilityChanged -= self.__onMapVisibilityChanged
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnVisibilityChanged -= self.__onRespawnVisibilityChanged

    def __onGUISpaceEntered(self, spaceID):
        if spaceID == SPACE_ID.LOGIN:
            g_guiEvents.goToLogin()
        elif spaceID == SPACE_ID.LOBBY:
            g_guiEvents.goToLobby()
        elif spaceID == SPACE_ID.BATTLE_LOADING:
            g_guiEvents.goToBattleLoading()
        elif spaceID == SPACE_ID.BATTLE:
            g_guiEvents.goToBattle()

    def __onGUISpaceLeft(self, spaceID):
        if spaceID == SPACE_ID.LOBBY:
            g_guiEvents.leaveLobby()
        elif spaceID == SPACE_ID.BATTLE:
            g_guiEvents.leaveBattle()

    def __onResizeStage(self):
        g_guiEvents.resizeStage()

    def __handleShowCursor(self, _):
        isShow = True
        g_guiEvents.toggleCursor(isShow)

    def __handleHideCursor(self, _):
        isShow = False
        g_guiEvents.toggleCursor(isShow)

    def __toggleRadialMenu(self, event):
        if BattleReplay.isPlaying():
            return
        isDown = event.ctx['isDown']
        g_guiEvents.toggleRadialMenu(isDown)

    def __toggleFullStats(self, event):
        isDown = event.ctx['isDown']
        g_guiEvents.toggleFullStats(isDown)

    def __toggleFullStatsQuestProgress(self, event):
        isDown = event.ctx['isDown']
        g_guiEvents.toggleFullStatsQuestProgress(isDown)

    def __onMapVisibilityChanged(self, isVisible):
        g_guiEvents.epicMapOverlayVisibility(isVisible)

    def __onRespawnVisibilityChanged(self, isRespawnScreenVisible):
        g_guiEvents.epicRespawnOverlayVisibility(isRespawnScreenVisible)


class Events(object):

    def goToLogin(self):
        pass

    def goToLobby(self):
        pass

    def goToBattleLoading(self):
        pass

    def goToBattle(self):
        ServicesLocator.appLoader.getApp().loadView(SFViewLoadParams(CONSTANTS.VIEW_ALIAS))

    def leaveLobby(self):
        pass

    def leaveBattle(self):
        pass

    def resizeStage(self):
        g_guiViews.resize()

    def toggleCursor(self, isShow):
        g_guiViews.cursor(isShow)

    def toggleRadialMenu(self, isShow):
        g_guiViews.radialMenu(isShow)

    def toggleFullStats(self, isShow):
        g_guiViews.fullStats(isShow)

    def toggleFullStatsQuestProgress(self, isShow):
        g_guiViews.fullStatsQuestProgress(isShow)

    def epicMapOverlayVisibility(self, isShow):
        g_guiViews.epicMapOverlayVisibility(isShow)

    def epicRespawnOverlayVisibility(self, isShow):
        g_guiViews.epicRespawnOverlayVisibility(isShow)


class Settings(object):

    def _start(self):
        g_entitiesFactories.addSettings(ViewSettings(CONSTANTS.VIEW_ALIAS, Flash_UI, CONSTANTS.FILE_NAME, WindowLayer.WINDOW, None, ScopeTemplates.GLOBAL_SCOPE))
        # g_entitiesFactories.addSettings(ViewSettings(CONSTANTS.VIEW_ALIAS, Flash_UI, CONSTANTS.FILE_NAME, ViewTypes.WINDOW, None, ScopeTemplates.GLOBAL_SCOPE))

    def _destroy(self):
        g_entitiesFactories.removeSettings(CONSTANTS.VIEW_ALIAS)


class Flash_Meta(View):

    def py_log(self, *args):
        self._printOverrideError('py_log')

    def py_update(self, alias, props):
        self._printOverrideError('py_update')

    def as_createS(self, alias, type, props):
        if self._isDAAPIInited():
            return self.flashObject.as_create(alias, type, props)

    def as_updateS(self, alias, props, params):
        if self._isDAAPIInited():
            return self.flashObject.as_update(alias, props, params)

    def as_deleteS(self, alias):
        if self._isDAAPIInited():
            return self.flashObject.as_delete(alias)

    def as_resizeS(self, width, height):
        if self._isDAAPIInited():
            return self.flashObject.as_resize(width, height)

    def as_cursorS(self, isShow):
        if self._isDAAPIInited():
            return self.flashObject.as_cursor(isShow)

    def as_radialMenuS(self, isShow):
        if self._isDAAPIInited():
            return self.flashObject.as_radialMenu(isShow)

    def as_fullStatsS(self, isShow):
        if self._isDAAPIInited():
            return self.flashObject.as_fullStats(isShow)

    def as_fullStatsQuestProgressS(self, isShow):
        if self._isDAAPIInited():
            return self.flashObject.as_fullStatsQuestProgress(isShow)

    def as_epicMapOverlayVisibilityS(self, isShow):
        return self.flashObject.as_epicMapOverlayVisibility(isShow) if self._isDAAPIInited() else None

    def as_epicRespawnOverlayVisibilityS(self, isShow):
        return self.flashObject.as_epicRespawnOverlayVisibility(isShow) if self._isDAAPIInited() else None


class Flash_UI(Flash_Meta):

    def _populate(self):
        super(Flash_UI, self)._populate()
        g_guiHooks._populate()
        g_guiViews.ui = self
        g_guiViews.resize()
        g_guiViews.createAll()

    def _dispose(self):
        g_guiViews.ui = None
        g_guiHooks._dispose()
        super(Flash_UI, self)._dispose()

    def py_log(self, *args):
        LOG_NOTE(*args)

    def py_update(self, alias, props):
        if g_guiCache.isComponent(alias):
            g_guiCache.update(alias, props.toDict())
            COMPONENT_EVENT.UPDATED(alias, props.toDict())


class GUIFlash(object):

    def __init__(self):
        g_guiSettings._start()
        g_guiHooks._start()

    def __del__(self):
        g_guiHooks._destroy()
        g_guiSettings._destroy()

    def createComponent(self, alias, type, props=None):
        if not g_guiCache.isComponent(alias):
            type = g_guiCache.getCustomizedType(type)
            if g_guiCache.isTypeValid(type):
                g_guiCache.create(alias, type, props)
                g_guiViews.create(alias, type, props)
            else:
                LOG_ERROR("Invalid type of component '%s'!" % alias)
        else:
            LOG_ERROR("Component '%s' already exists!" % alias)

    def updateComponent(self, alias, props, params=None):
        if g_guiCache.isComponent(alias):
            g_guiCache.update(alias, props)
            g_guiViews.update(alias, props, params)
        else:
            LOG_ERROR("Component '%s' not found!" % alias)

    def deleteComponent(self, alias):
        if g_guiCache.isComponent(alias):
            g_guiCache.delete(alias)
            g_guiViews.delete(alias)
        else:
            LOG_ERROR("Component '%s' not found" % alias)


g_guiCache = Cache()
g_guiViews = Views()
g_guiHooks = Hooks()
g_guiEvents = Events()
g_guiSettings = Settings()
