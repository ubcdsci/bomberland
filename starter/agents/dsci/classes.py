from dataclasses import dataclass
from typing import List
import torch


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
    invBomb: int ## how many bombs in inventory
    actBomb: int ## how many bombs we have out right now
    radius: int ## explosion radius of bomb
    invulnerability: int ## number of ticks until invul wears off


# state = UnitState(
#             unitId="c",
#             agentId="a",
#             coord=Coordinate(3,5),
#             hp=1,
#             bomb=3,
#             ammunition=0,
#             invulnerability=30,
#         )
# 
# print(state)

# indestructible, destructible, pickup, bomb, fire = range(5)

@dataclass
class Entity:
    created: int
    coord: Coordinate
    # types:
    #   m: metalBlock (indestructible)
    #   w: woodenBlock (destructible)
    #   o: oreBlock (destructible)
    #   a: ammo
    #   bp: blast radius powerup
    #   b: bomb
    #   x: explosion
    #   x: end game fire

    ## an abstract method for all the implementations to override
    ## will return the appropriate value for the map, whether that be
    ## a health, or just constant 1
    def call(self) -> torch.Tensor:
        return torch.tensor(1)

    ## will just take the map and add the output of its call() to 
    ## its corresponding coordinates on the map
    ## but some classes like the bomb needs to do extra stuff
    def update_map(self, target: torch.Tensor):
        target[self.coord.x, self.coord.y] = self.call()

@dataclass
class Indestructible(Entity):
    pass

@dataclass
class Destructible(Entity):
    hp: int
    def call(self):
        return torch.tensor(self.hp)

@dataclass
class Pickup(Entity):
    ## though seemingly an unnecessary level of abstraction for the two
    ## pickups considering no code is in this class, instances of the
    ## radius and ammo pickups also both being instances of pickups
    ## makes some things very convenient
    hp: int

@dataclass
class Radius(Pickup):
    expires: int
    pass

@dataclass
class Ammo(Pickup):
    expires: int
    pass

@dataclass
class Bomb(Entity):
    owner: str
    expires: int
    hp: int
    blastDiameter: int
    
    ## we need to consider the bomb's collision
    ## so we can't just use the initial plan of
    ## the bomb map being the fire map
    def call(self):
        return torch.tensor([self.expires, self.hp, self.blastDiamter])

    def update_map(self, target: torch.Tensor):
        target[..., self.coord.x, self.coord.y] = self.call()
    

@dataclass
class Fire(Entity):
    ## just collating explosion fire and end game fire into the same thing
    ## because they're functionally idenditcal if you just set the end game fire
    ## expire time to be functionally infinite

    # TODO: endgame fire expires
    expires: int
    owner: str = None # default is none because end game fire has no owner

    def call(self):
        return torch.tensor(self.expires)

## Every turn, we will get a response from the api. With this class:
## 1. We parse the API response into a board state that contains python objects
## 2. We pass this object to an agent
## 3. The agent determines the next move based on the board state

## Immutable
@dataclass(frozen=True)
class BoardState:
    entities: List[Entity]
    units: List[Unit]
    width: int
    height: int
    tick: int
    # entities: list
    # entities: "list of entities"
    # entities: ...
    # entities: list[Entity]
    # entities

    ## Determine all possible board permutations from this state for a tree-search agent
    ## Essentially generates all possible results of the "tick" function
    # def permute_all(self) -> list['BoardState']:
    def permute_all(self):
        return None
        ## return <all possible moved states>


    ## Convert to tensors to use in an RL model
    # def to_learnable(self) -> None:
    # def to_learnable(self) -> dict[type, torch.Tensor]:
    def to_learnable(self):
        unit_map = torch.zeros([self.width, self.height], dtype=torch.int32)
        ## TODO: how will we distinguish the units of different sides on the map?
        ## negative and positive values? does that makes sense?
        ## or should we do a new map
        indestructible_map = torch.zeros([self.width, self.height], dtype=torch.int32)
        destructible_map =  torch.zeros([self.width, self.height], dtype=torch.int32)
        # pickup_map = torch.zeros([self.width, self.height], dtype=torch.int32)
        radius_map = torch.zeros([self.width, self.height], dtype=torch.int32)
        ammo_map = torch.zeros([self.width, self.height], dtype=torch.int32)
        bomb_map = torch.zeros([2, self.width, self.height], dtype=torch.int32)
        fire_map = torch.zeros([self.width, self.height], dtype=torch.int32)
        
        table = {
            UnitState: unit_map,
            Indestructible: indestructible_map,
            Destructible: destructible_map,
            # Pickup: pickup_map,
            Ammo: ammo_map,
            Radius: radius_map,
            Bomb: bomb_map,
            Fire: fire_map
        }

        for entity in self.entities:
            class_map = table[type(entity)]
            entity.update_map(class_map)

            ## just have a method in entity class that takes a map and updates it with the result of its call
            ## then overload this method as necessary for the weirded entities like bombs and units
            

        return table

    ## Move units, etc
    # def tick(actions: Dict[Entity, Action]) -> BoardState:
    def tick(actions):
        pass

