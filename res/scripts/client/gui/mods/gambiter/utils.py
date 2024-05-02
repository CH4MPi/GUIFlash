# -*- coding: utf-8 -*-

IS_DEBUG = False

def LOG(arg, *args):
    print str(arg), ' '.join([str(arg) for arg in args])


def LOG_NOTE(*args):
    LOG('GUIFlash: [NOTE]', *args)


def LOG_ERROR(*args):
    LOG('GUIFlash: [ERROR]', *args)


def LOG_DEBUG(*args):
    if IS_DEBUG:
        LOG('GUIFlash: [DEBUG]', *args)


def LOG_TRACE(exc=None):
    import traceback
    print '=' * 25
    if exc is not None:
        LOG_ERROR(exc)
        traceback.print_exc()
    else:
        traceback.print_stack()
    print '=' * 25


def LOG_DIR(object, include=None, exclude=None):
    print '=' * 25
    for attr in dir(object):
        if (include is None or attr.find(include) >= 0) and (exclude is None or attr.find(exclude) == -1):
            try:
                LOG('GUIFlash: [DIR]', 'object.%s = %s' % (attr, getattr(object, attr)))
            except:
                LOG('GUIFlash: [DIR]', 'object.%s = %s' % (attr, '<error>'))
    print '=' * 25


def debugLog(func):

    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
            LOG_DEBUG("Function '%s' completed!" % func.func_name)
        except Exception as Error:
            LOG_ERROR("Error in function '%s': %s!" % (func.func_name, Error))

    return wrapper


def debugTime(func):

    def wrapper(*args, **kwargs):
        import time
        startTime = time.time()
        func(*args, **kwargs)
        LOG_DEBUG("Method '%s' measuring time: %.10f" % (func.func_name, time.time() - startTime))

    return wrapper


def getParentWindow():
    from skeletons.gui.impl import IGuiLoader
    from helpers import dependency
    uiLoader = dependency.instance(IGuiLoader)
    if uiLoader and uiLoader.windowsManager:
        return uiLoader.windowsManager.getMainWindow()


class EventHook(object):

    def __init__(self):
        self.__handlers = []

    def __iadd__(self, handler):
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler):
        if handler in self.__handlers:
            self.__handlers.remove(handler)
        return self

    def fire(self, *args, **keywargs):
        for handler in self.__handlers:
            handler(*args, **keywargs)

    def clearObjectHandlers(self, inObject):
        for theHandler in self.__handlers:
            if theHandler.im_self == inObject:
                self -= theHandler


def _RegisterEvent(handler, cls, method, prepend=False):
    evt = '__event_%i_%s' % ((1 if prepend else 0), method)
    if hasattr(cls, evt):
        e = getattr(cls, evt)
    else:
        newm = '__orig_%i_%s' % ((1 if prepend else 0), method)
        setattr(cls, evt, EventHook())
        setattr(cls, newm, getattr(cls, method))
        e = getattr(cls, evt)
        m = getattr(cls, newm)
        setattr(cls, method, lambda *a, **k: __event_handler(prepend, e, m, *a, **k))
    e += handler


def __event_handler(prepend, e, m, *a, **k):
    try:
        if prepend:
            e.fire(*a, **k)
            r = m(*a, **k)
        else:
            r = m(*a, **k)
            e.fire(*a, **k)
        return r
    except:
        LOG_TRACE(__file__)


def _override(cls, method, newm):
    orig = getattr(cls, method)
    if type(orig) is not property:
        setattr(cls, method, newm)
    else:
        setattr(cls, method, property(newm))


def _OverrideMethod(handler, cls, method):
    orig = getattr(cls, method)
    newm = lambda *a, **k: handler(orig, *a, **k)
    _override(cls, method, newm)


def _OverrideStaticMethod(handler, cls, method):
    orig = getattr(cls, method)
    newm = staticmethod(lambda *a, **k: handler(orig, *a, **k))
    _override(cls, method, newm)


def _OverrideClassMethod(handler, cls, method):
    orig = getattr(cls, method)
    newm = classmethod(lambda *a, **k: handler(orig, *a, **k))
    _override(cls, method, newm)


def _hook_decorator(func):

    def decorator1(*a, **k):

        def decorator2(handler):
            func(handler, *a, **k)

        return decorator2

    return decorator1


registerEvent = _hook_decorator(_RegisterEvent)
overrideMethod = _hook_decorator(_OverrideMethod)
overrideStaticMethod = _hook_decorator(_OverrideStaticMethod)
overrideClassMethod = _hook_decorator(_OverrideClassMethod)
