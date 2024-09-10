# -*- coding: utf-8 -*-

__all__ = ['COMPONENT_TYPE', 'COMPONENT_ALIGN', 'COMPONENT_EVENT', 'GUIFlash']

import codecs
import json

# noinspection PyUnresolvedReferences
import BigWorld
# noinspection PyUnresolvedReferences
import GUI

import BattleReplay
import Event
from frameworks.wulf import WindowLayer
from gui import g_guiResetters
from gui.Scaleform.framework import g_entitiesFactories, ScopeTemplates, ViewSettings
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.personality import ServicesLocator
from helpers import dependency
from skeletons.gui.app_loader import GuiGlobalSpaceID as SPACE_ID
from skeletons.gui.battle_session import IBattleSessionProvider
from utils import LOG_DEBUG, LOG_ERROR, LOG_NOTE, getParentWindow


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
    NONE = 'none'


class COMPONENT_STATE(object):
    INIT = 1
    LOAD = 2
    UNLOAD = 3
    DESTROY = 4


class COMPONENT_EVENT(object):
    LOADED = Event.Event()
    UPDATED = Event.Event()
    UNLOADED = Event.Event()


# noinspection PyMethodMayBeStatic
class Cache(object):

    def __init__(self):
        self.components = {}

    def create(self, alias, _type, props, battle=True, lobby=False):
        LOG_DEBUG("Create cache: '%s' [%s] -> Properties: %s, battle: %s, lobby: %s" % (alias, _type, props, battle, lobby))
        self.components[alias] = {'type': _type, 'props': props, 'battle': battle, 'lobby': lobby}

    def update(self, alias, props):
        LOG_DEBUG("Change cache: '%s' -> Properties: %s" % (alias, props))
        self.components[alias].get('props').update(props)

    def delete(self, alias):
        LOG_DEBUG("Destroy cache: '%s'" % alias)
        del self.components[alias]

    def isComponent(self, alias):
        return alias in self.components

    def isActiveComponent(self, alias):
        if alias not in self.components:
            return False
        return self.components[alias]['battle'] if hasattr(BigWorld.player(), 'arena') else self.components[alias]['lobby']

    def getComponent(self, alias=None):
        return self.components if alias is None else self.components.get(alias)

    def getKeys(self):
        return sorted(filter(self.isActiveComponent, self.components.keys()))

    def getCustomizedType(self, compType):
        return ''.join(compType.split()).capitalize()

    def isTypeValid(self, compType):
        return compType in ALL_COMPONENT_TYPES

    def readConfig(self, path):
        LOG_DEBUG("Read config from file '%s'." % path)
        with open(path, "r") as f:
            data = json.load(f)
        return data

    def saveConfig(self, path, data):
        LOG_DEBUG("Save config in file '%s'." % path)
        with codecs.open(path, 'w', 'utf-8') as f:
            json.dump(data, f, indent=4, sort_keys=True, ensure_ascii=False)


class Views(object):

    def __init__(self):
        self.ui = None

    def createAll(self):
        for alias in g_guiCache.getKeys():
            component = g_guiCache.getComponent(alias)
            self.create(alias, component.get('type'), component.get('props'))
        if not hasattr(BigWorld.player(), 'arena'):
            self.cursor(True)

    def create(self, alias, compType, props):
        if self.ui is not None:
            LOG_DEBUG("Create component: '%s' [%s] -> Properties: %s" % (alias, compType, props))
            self.ui.as_createS(alias, compType, props)

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

    def fullStatsPersonalReserves(self, isShow):
        if self.ui is not None:
            self.ui.as_fullStatsPersonalReservesS(isShow)

    def epicMapOverlayVisibility(self, isShow):
        if self.ui is not None:
            self.ui.as_epicMapOverlayVisibilityS(isShow)

    def epicRespawnOverlayVisibility(self, isShow):
        if self.ui is not None:
            self.ui.as_epicRespawnOverlayVisibilityS(isShow)

    def battleRoyaleSpawnVisibility(self, isVisible):
        if self.ui is not None:
            self.ui.as_battleRoyaleRespawnVisibilityS(isVisible)

    def killCamVisibility(self, isVisible):
        if self.ui is not None:
            self.ui.as_killCamVisibilityS(isVisible)


# noinspection PyMethodMayBeStatic
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
        g_eventBus.addListener(events.GameEvent.FULL_STATS_PERSONAL_RESERVES, self.__toggleFullStatsPersonalReserves, scope=EVENT_BUS_SCOPE.BATTLE)
        g_guiResetters.add(self.__onResizeStage)

        ctrl = self.sessionProvider.dynamic.maps
        if ctrl is not None and hasattr(ctrl, 'onVisibilityChanged'):
            ctrl.onVisibilityChanged += self.__onMapVisibilityChanged

        # NOTE: frontline respawn screen
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None and hasattr(ctrl, 'onRespawnVisibilityChanged'):
            ctrl.onRespawnVisibilityChanged += self.__onRespawnVisibilityChanged

        # WoT 1.24.1 - KILL CAM - throws an error on other clients like Lesta, so we catch and ignore it
        try:
            if hasattr(self.sessionProvider.shared, 'killCamCtrl') and self.sessionProvider.shared.killCamCtrl:
                self.sessionProvider.shared.killCamCtrl.onKillCamModeStateChanged += self.__onKillCamModeStateChanged
        except AttributeError:
            LOG_DEBUG('killCamCtrl not found!')

        # NOTE: steel hunter select spawn screen
        try:
            from battle_royale.gui.Scaleform.daapi.view.battle import BattleRoyalePage
            spawnCtrl = self.sessionProvider.dynamic.spawn
            if spawnCtrl is not None:
                if hasattr(BattleRoyalePage, 'showSpawnPoints'):
                    global hooked_showSpawnPoints
                    if hooked_showSpawnPoints is None:
                        hooked_showSpawnPoints = BattleRoyalePage.showSpawnPoints
                        BattleRoyalePage.showSpawnPoints = newBattleRoyalePageShowSpawnPoints
                        LOG_DEBUG('BattleRoyalePage:showSpawnPoints hooked!')

                if hasattr(BattleRoyalePage, 'closeSpawnPoints'):
                    global hooked_closeSpawnPoints
                    if hooked_closeSpawnPoints is None:
                        hooked_closeSpawnPoints = BattleRoyalePage.closeSpawnPoints
                        BattleRoyalePage.closeSpawnPoints = newBattleRoyalePageCloseSpawnPoints
                        LOG_DEBUG('BattleRoyalePage:closeSpawnPoints hooked!')

                # TEST: check if this works more accurate
                # ctrl = self.sessionProvider.dynamic.maps
                # if ctrl is not None:
                #     ctrl.onOverlayTriggered += self.onBattleRoyaleSpawnVisibilityChanged
                #     self.onBattleRoyaleSpawnVisibilityChanged(ctrl.overlayActive)
                # TEST: !check if this works more accurate
        except ImportError:
            pass

    def _dispose(self):
        g_eventBus.removeListener(events.GameEvent.SHOW_CURSOR, self.__handleShowCursor, EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.removeListener(events.GameEvent.HIDE_CURSOR, self.__handleHideCursor, EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.removeListener(events.GameEvent.RADIAL_MENU_CMD, self.__toggleRadialMenu, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(events.GameEvent.FULL_STATS, self.__toggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(events.GameEvent.FULL_STATS_QUEST_PROGRESS, self.__toggleFullStatsQuestProgress, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(events.GameEvent.FULL_STATS_PERSONAL_RESERVES, self.__toggleFullStatsPersonalReserves, scope=EVENT_BUS_SCOPE.BATTLE)
        g_guiResetters.discard(self.__onResizeStage)

        ctrl = self.sessionProvider.dynamic.maps
        if ctrl and hasattr(ctrl, 'onVisibilityChanged'):
            ctrl.onVisibilityChanged -= self.__onMapVisibilityChanged

        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnVisibilityChanged -= self.__onRespawnVisibilityChanged

        # WoT 1.24.1 - KILL CAM
        try:
            if hasattr(self.sessionProvider.shared, 'killCamCtrl') and self.sessionProvider.shared.killCamCtrl:
                self.sessionProvider.shared.killCamCtrl.onKillCamModeStateChanged -= self.__onKillCamModeStateChanged
        except AttributeError:
            LOG_DEBUG('killCamCtrl not found!')

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
        g_guiEvents.toggleCursor(True)

    def __handleHideCursor(self, _):
        g_guiEvents.toggleCursor(False)

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

    def __toggleFullStatsPersonalReserves(self, event):
        isDown = event.ctx['isDown']
        g_guiEvents.toggleFullStatsPersonalReserves(isDown)

    def __onKillCamModeStateChanged(self, state, *args, **kwargs):
        try:
            from gui.shared.events import DeathCamEvent
            if state is DeathCamEvent.State.NONE:
                return
            g_guiEvents.killCamVisible(state not in (DeathCamEvent.State.INACTIVE, DeathCamEvent.State.PREPARING, DeathCamEvent.State.FINISHED))
        except ImportError:
            pass

    def __onMapVisibilityChanged(self, isVisible):
        g_guiEvents.epicMapOverlayVisibility(isVisible)

    def __onRespawnVisibilityChanged(self, isVisible):
        g_guiEvents.epicRespawnOverlayVisibility(isVisible)

    def onBattleRoyaleSpawnVisibilityChanged(self, isVisible):
        g_guiEvents.battleRoyaleSpawnVisibility(isVisible)


# noinspection PyMethodMayBeStatic
class Events(object):

    def goToLogin(self):
        pass

    def goToLobby(self):
        ServicesLocator.appLoader.getApp().loadView(SFViewLoadParams(CONSTANTS.VIEW_ALIAS, parent=getParentWindow()))

    def goToBattleLoading(self):
        pass

    def goToBattle(self):
        ServicesLocator.appLoader.getApp().loadView(SFViewLoadParams(CONSTANTS.VIEW_ALIAS, parent=getParentWindow()))

    def leaveLobby(self):
        if g_guiViews.ui is not None:
            g_guiViews.ui.destroy()
        return

    def leaveBattle(self):
        if g_guiViews.ui is not None:
            g_guiViews.ui.destroy()
        return

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

    def toggleFullStatsPersonalReserves(self, isShow):
        g_guiViews.fullStatsPersonalReserves(isShow)

    def epicMapOverlayVisibility(self, isShow):
        g_guiViews.epicMapOverlayVisibility(isShow)

    def epicRespawnOverlayVisibility(self, isShow):
        g_guiViews.epicRespawnOverlayVisibility(isShow)

    def battleRoyaleSpawnVisibility(self, isShow):
        g_guiViews.battleRoyaleSpawnVisibility(isShow)

    def killCamVisible(self, isVisible):
        g_guiViews.killCamVisibility(isVisible)


# noinspection PyMethodMayBeStatic
class Settings(object):

    def _start(self):
        g_entitiesFactories.addSettings(ViewSettings(CONSTANTS.VIEW_ALIAS, Flash_UI, CONSTANTS.FILE_NAME, WindowLayer.WINDOW, None, ScopeTemplates.GLOBAL_SCOPE))
        return

    def _destroy(self):
        g_entitiesFactories.removeSettings(CONSTANTS.VIEW_ALIAS)


class Flash_Meta(View):

    def py_log(self, *args):
        self._printOverrideError('py_log')

    def py_update(self, alias, props):
        self._printOverrideError('py_update')

    def as_createS(self, alias, compType, props):
        return self.flashObject.as_create(alias, compType, props) if self._isDAAPIInited() else None

    def as_updateS(self, alias, props, params):
        return self.flashObject.as_update(alias, props, params) if self._isDAAPIInited() else None

    def as_deleteS(self, alias):
        return self.flashObject.as_delete(alias) if self._isDAAPIInited() else None

    def as_resizeS(self, width, height):
        return self.flashObject.as_resize(width, height) if self._isDAAPIInited() else None

    def as_cursorS(self, isVisible):
        return self.flashObject.as_cursor(isVisible) if self._isDAAPIInited() else None

    def as_radialMenuS(self, isVisible):
        return self.flashObject.as_radialMenu(isVisible) if self._isDAAPIInited() else None

    def as_fullStatsS(self, isVisible):
        return self.flashObject.as_fullStats(isVisible) if self._isDAAPIInited() else None

    def as_fullStatsQuestProgressS(self, isVisible):
        return self.flashObject.as_fullStatsQuestProgress(isVisible) if self._isDAAPIInited() else None

    def as_fullStatsPersonalReservesS(self, isVisible):
        return self.flashObject.as_fullStatsPersonalReserves(isVisible) if self._isDAAPIInited() else None

    def as_epicMapOverlayVisibilityS(self, isVisible):
        return self.flashObject.as_epicMapOverlayVisibility(isVisible) if self._isDAAPIInited() else None

    def as_epicRespawnOverlayVisibilityS(self, isVisible):
        return self.flashObject.as_epicRespawnOverlayVisibility(isVisible) if self._isDAAPIInited() else None

    def as_battleRoyaleRespawnVisibilityS(self, isVisible):
        return self.flashObject.as_battleRoyaleRespawnVisibility(isVisible) if self._isDAAPIInited() else None

    def as_killCamVisibilityS(self, isVisible):
        return self.flashObject.as_killCamVisibility(isVisible) if self._isDAAPIInited() else None


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
        return

    def py_log(self, *args):
        LOG_NOTE(*args)

    def py_update(self, alias, props):
        if g_guiCache.isComponent(alias):
            g_guiCache.update(alias, props.toDict())
            COMPONENT_EVENT.UPDATED(alias, props.toDict())


# noinspection PyMethodMayBeStatic
class GUIFlash(object):

    def __init__(self):
        g_guiSettings._start()
        g_guiHooks._start()

    def __del__(self):
        g_guiHooks._destroy()
        g_guiSettings._destroy()

    def createComponent(self, alias, compType, props=None, battle=True, lobby=False):
        if not g_guiCache.isComponent(alias):
            compType = g_guiCache.getCustomizedType(compType)
            if g_guiCache.isTypeValid(compType):
                g_guiCache.create(alias, compType, props, battle, lobby)
                if g_guiCache.isActiveComponent(alias):
                    g_guiViews.create(alias, compType, props)
            else:
                LOG_ERROR("Invalid component type '%s'!" % alias)
        else:
            LOG_ERROR("Component '%s' already exists!" % alias)

    def updateComponent(self, alias, props, params=None):
        if g_guiCache.isComponent(alias):
            g_guiCache.update(alias, props)
            if g_guiCache.isActiveComponent(alias):
                g_guiViews.update(alias, props, params)
        else:
            LOG_ERROR("Component '%s' not found!" % alias)

    def deleteComponent(self, alias):
        if g_guiCache.isComponent(alias):
            if g_guiCache.isActiveComponent(alias):
                g_guiViews.delete(alias)
            g_guiCache.delete(alias)
        else:
            LOG_ERROR("Component '%s' not found" % alias)


g_guiCache = Cache()
g_guiViews = Views()
g_guiHooks = Hooks()
g_guiEvents = Events()
g_guiSettings = Settings()

hooked_showSpawnPoints = None  # Type: Callable
hooked_closeSpawnPoints = None


# noinspection PyCallingNonCallable
def newBattleRoyalePageShowSpawnPoints(self):
    try:
        LOG_DEBUG('newBattleRoyalePageShowSpawnPoints called!')
        g_guiHooks.onBattleRoyaleSpawnVisibilityChanged(True)
    except StandardError:
        pass
    finally:
        hooked_showSpawnPoints(self)


# noinspection PyCallingNonCallable
def newBattleRoyalePageCloseSpawnPoints(self):
    try:
        LOG_DEBUG('newBattleRoyalePageCloseSpawnPoints called!')
        g_guiHooks.onBattleRoyaleSpawnVisibilityChanged(False)
    except StandardError:
        pass
    finally:
        hooked_closeSpawnPoints(self)
