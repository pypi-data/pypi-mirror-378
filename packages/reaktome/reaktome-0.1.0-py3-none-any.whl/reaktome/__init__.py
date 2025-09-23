import logging

from typing import Any, Callable, Union
from collections import defaultdict
from weakref import WeakMethod
from functools import wraps


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

NOWRAP = (int, float, str, bool, bytes, tuple, frozenset, type(None))
KLASSES = {}
ON_CHANGE = Callable[[Any, Any, Any], None]
SENTINAL = object()


def maybe_make_klass(value, attrs):
    "Create base classes to override __setitem__ and cache them"
    base = value.__class__
    name = f'_Reactome_{base.__name__.title()}'
    attrs.update({
        '_is_reaktome': True,
    })
    if base not in KLASSES:
        KLASSES[base] = type(name, (base,), attrs)
    return KLASSES[base]


def reaktiv8(value: Any,
             on_change: ON_CHANGE,
             path: str = '',
             ) -> Any:
    """Wrap dicts/lists with reactive containers recursively"""
    if hasattr(value, '_is_reaktome'):
        return value

    if isinstance(value, NOWRAP):
        return value

    def _on_change(subpath, old, val):
        full_key = f"{path}{subpath}" if path and subpath else subpath or path
        on_change(full_key, old, val)

    if isinstance(value, dict):
        for k, v in value.items():
            subpath = f'{path}[{k}]'
            value[k] = reaktiv8(v, on_change=_on_change, path=subpath)
        value = ReaktomeDict(value, _on_change)

    elif isinstance(value, list):
        for i, item in enumerate(value):
            subpath = f'{path}[{i}]'
            value[i] = reaktiv8(item, on_change=_on_change, path=subpath)
        value = ReaktomeList(value, _on_change)

    elif hasattr(value, '__dict__'):
        for k, v in value.__dict__.items():
            if not k.startswith('_'):
                v = reaktiv8(v, on_change=_on_change, path=f'[{k}]')
            value.__dict__[k] = v

        value.__class__ = maybe_make_klass(value, {
            '__setitem__': __setitem__,
        })

    return value


def __setattr__(self, name, value):
    old = getattr(self, name, None)
    if name.startswith('_') or callable(value):
        object.__setattr__(self, name, value)
        return
    value = reaktiv8(value, on_change=self.on_change, path=name)
    object.__setattr__(self, name, value)
    self.on_change(name, old, value)


def __setitem__(self, key, value):
    if (isinstance(key, str) and key.startswith('_')) or callable(value):
        super().__setitem__(key, value)
        return

    try:
        old = self[key]

    except KeyError:
        old = None

    super(type(self), self).__setitem__(key, value)
    self.on_change(f'[{key}]', old, value)


def __delitem__(self, key):
    old = self[key]
    super(type(self), self).__delitem__(key)
    self.on_change(f'[{key}]', old, None)


def pop(self, i=-1, default=SENTINAL):
    try:
        old = value = super(type(self), self).pop(i)

    except KeyError:
        old = None
        if default is SENTINAL:
            raise
        value = default

    if old is not None:
        self.on_change(f'[{i}]', old, None)
    return value


def remove(self, value):
    i = self.index(value)
    old = self[i]
    super(type(self), self).remove(value)
    self.on_change(f'[{i}]', old, None)


def append(self, value):
    i = len(self)
    value = reaktiv8(value, on_change=self.on_change, path=f'[{i}]')
    super(type(self), self).append(value)
    self.on_change(f'[{i}]', None, value)


def insert(self, i, value):
    value = reaktiv8(value, on_change=self.on_change, path=f'[{i}]')
    super(type(self), self).insert(i, value)
    self.on_change(f'[{i}]', None, value)


def extend(self, iterable):
    i = len(self)
    iterable = [
        reaktiv8(value, on_change=self.on_change, path=f'[{i + ii}]')
        for ii, value in enumerate(iterable)
    ]
    super(type(self), self).extend(iterable)
    self.on_change(f'[{i:i+len(iterable)}]', None, iterable)


def popitem(self):
    k, v = super(type(self), self).popitem()
    self.on_change(f'[{k}]', v, None)
    return k, v


def setdefault(self, key, default=None):
    old = self.get(key)
    super(type(self), self).setdefault(key, default)
    self.on_change(f'[{key}]', old, default)
    return default


def update(self, *args, **kwargs):
    keys, old, new = [], [], []
    for arg in args:
        if callable(getattr(arg, 'items', None)):
            arg = arg.items()
        for k, v in arg:
            keys.append(k)
            old.append(self.get(k))
            new.append(reaktiv8(v, on_change=self.on_change, path=f'[{k}]'))
    for k, v in kwargs.items():
        keys.append(k)
        old.append(self.get(k))
        new.append(reaktiv8(v, on_change=self.on_change, path=f'[{k}]'))
    super(type(self), self).update(zip(keys, new))
    self.on_change(f'[{",".join(keys)}]', old, new)


class ReaktomeList(list):
    _is_reaktome = True
    __setattr__ = __setattr__
    __setitem__ = __setitem__
    __delitem__ = __delitem__
    pop = pop
    append = append
    remove = remove
    insert = insert
    extend = extend

    def __init__(self, value, on_change):
        self.on_change = on_change


class ReaktomeDict(dict):
    _is_reaktome = True
    __setattr__ = __setattr__
    __setitem__ = __setitem__
    __delitem__ = __delitem__
    pop = pop
    popitem = popitem
    setdefault = setdefault
    update = update

    def __init__(self, value, on_change):
        self.on_change = on_change


class ReaktomeMeta(type):
    def __new__(mcs, name, bases, namespace):
        if '__setattr__' not in namespace:
            namespace['__setattr__'] = __setattr__
        cls = super().__new__(mcs, name, bases, namespace)
        return cls


class DeadWatcher(Exception):
    "Raised when a watcher's weakref has been collected."
    pass


class ReaktomeWatcher:
    def __init__(self, cb: ON_CHANGE) -> None:
        self.cb: Union[WeakMethod[ON_CHANGE], ON_CHANGE]
        if getattr(cb, '__self__', None) is not None:
            # NOTE: cb is a method, use a Weakref
            self.cb = WeakMethod(cb)
        else:
            self.cb = cb

    def __call__(self, name: str, old: Any, new: Any) -> Any:
        if isinstance(self.cb, WeakMethod):
            cb = self.cb()
            if cb is None:
                raise DeadWatcher()

        else:
            cb = self.cb

        return cb(name, old, new)


def ensure_watchers(f):
    @wraps(f)
    def inner(self, *args, **kwargs):
        if not hasattr(self, '_watchers'):
            self.__dict__['_watchers'] = defaultdict(set)
        return f(self, *args, **kwargs)
    return inner


class Reaktome(metaclass=ReaktomeMeta):
    @ensure_watchers
    def on(self,
           path: str,
           cb: ON_CHANGE,
           ) -> tuple[str, ReaktomeWatcher]:
        watcher = ReaktomeWatcher(cb)
        self._watchers[path].add(watcher)  # type: ignore
        return (path, watcher)

    @ensure_watchers
    def off(self, path_cb: tuple[str, ReaktomeWatcher]) -> None:
        try:
            path, watcher = path_cb

        except TypeError:
            raise ValueError('Invalid handle: %s', path_cb)

        try:
            self._watchers[path].discard(watcher)  # type: ignore

        except ValueError:
            pass

    @ensure_watchers
    def on_change(self, path, old=None, new=None):
        """Hook to respond to all attribute/item changes"""
        LOGGER.debug(f"⚡ Change → {path}: {old} -> {new}")
        dead = []

        watchers = [
            *self._watchers.get('*', []),
            *self._watchers.get(path, []),
        ]

        for watcher in watchers:
            try:
                watcher(path, old, new)

            except DeadWatcher:
                dead.append((path, watcher))

        for (path, watcher) in dead:
            self._watchers[path].discard(watcher)


def on(obj: Any, path: str) -> Callable[[Callable], Callable]:
    def wrapped(f):
        obj.on(path, f)
        return f

    return wrapped
