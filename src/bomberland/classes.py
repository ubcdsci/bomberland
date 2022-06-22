from dataclasses import dataclass

@dataclass
class Coordinate:
    x: int
    y: int


@dataclass
class UnitState:
    unitId: str
    agentId: str
    coord: Coordinate
    hp: int
    bomb: int
    ammunition: int
    invulnerability: int


state = UnitState(
            unitId="c",
            agentId="a",
            coord=Coordinate(3,5),
            hp=1,
            bomb=3,
            ammunition=0,
            invulnerability=30,
        )

print(state)

indestructible, destructible, pickup, bomb, fire = range(5)

@dataclass
class Entity:
    created: int
    coord: Coordinate
    # type: int
    # types:
    #   m: metalBlock (indestructible)
    #   w: woodenBlock (destructible)
    #   o: oreBlock (destructible)
    #   a: ammo
    #   bp:blast radius powerup
    #   b: bomb
    #   x: explosion
    #   x: end game fire

@dataclass
class Indestructible(Entity):
    pass

@dataclass
class Destructible(Entity):
    hp: int

@dataclass
class Pickup(Entity):
    gives: int
    # 0 for bomb, 1 for ammo
    # no idea how to implement this better

@dataclass
class Bomb(Entity):
    owner: str
    expires: int
    hp: int
    blastDiameter: int

@dataclass
class Fire(Entity):
    # just collating explosion fire and end game fire into the same thing
    # because they're functionally idenditcal if you just set the end game fire
    # expire time to be functionally infinite
    owner: str
    expires: int


