# ===================== Possible World Configurations ========================
from dataclasses import dataclass, field

from typing_extensions import List, Callable

from .base_config import WorldConf, BodyConf, Connection, FixedConnectionConf, PrismaticConnectionConf, \
    ContainerConf, HandleConf

from ...factories.world import create_world


@dataclass
class Handle1(HandleConf):
    name: str = "Handle1"


@dataclass
class Handle2(HandleConf):
    name: str = "Handle2"


@dataclass
class Handle3(HandleConf):
    name: str = "Handle3"


@dataclass
class Container1(ContainerConf):
    name: str = "Container1"


@dataclass
class Container2(ContainerConf):
    name: str = "Container2"


@dataclass
class Container3(ContainerConf):
    name: str = "Container3"


def bodies():
    return [
        Handle1(),
        Handle2(),
        Handle3(),
        Container3(),
        Container1(),
        Container2()
    ]


@dataclass
class World(WorldConf):
    bodies: List[BodyConf] = field(default_factory=bodies, init=False)
    connections: List[Connection] = field(default_factory=lambda: [
        FixedConnectionConf(parent=Container1(), child=Container2()),
        FixedConnectionConf(parent=Container3(), child=Handle3()),
        PrismaticConnectionConf(parent=Container2(), child=Container1()),
        PrismaticConnectionConf(parent=Container2(), child=Container3()),
        FixedConnectionConf(parent=Container1(), child=Handle1()),
    ], init=False)
    factory_method: Callable = field(default=create_world, init=False)


