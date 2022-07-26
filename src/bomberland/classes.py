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

    ## an abstract method for all the implementations to override
    ## will return the appropriate value for the map, whether that be
    ## a health, or just constant 1
    def call(self) -> torch.Tensor:
        pass

@dataclass
class Indestructible(Entity):
    def call(self) -> torhc.Tensor:
        return torch.tensor

@dataclass
class Destructible(Entity):
    hp: int
    def call(self):
        return self.hp

@dataclass
class Pickup(Entity):
    gives: int
    ## 0 for bomb, 1 for ammo
    ## no idea how to implement this better

@dataclass
class Radius(Pickup):
    def call(self):
        return 1

@dataclass
class Ammo(Pickup):
    def call(self):
        return 1

@dataclass
class Bomb(Entity):
    owner: str
    expires: int
    hp: int
    blastDiameter: int

@dataclass
class Fire(Entity):
    ## just collating explosion fire and end game fire into the same thing
    ## because they're functionally idenditcal if you just set the end game fire
    ## expire time to be functionally infinite
    owner: str
    expires: int




## Every turn, we will get a response from the api. With this class:
## 1. We parse the API response into a board state that contains python objects
## 2. We pass this object to an agent
## 3. The agent determines the next move based on the board state

## Immutable
@dataclass(frozen=True)
class BoardState:

    width: int
    height: int
    entities: List[Entity]

    ## Determine all possible board permutations from this state for a tree-search agent
    ## Essentially generates all possible results of the "tick" function
    def permute_all(self) -> list['BoardState']:
        return None
        ## return <all possible moved states>


    ## Convert to tensors to use in an RL model
    def to_learnable(self) -> None:
    # def to_learnable(self) -> dict[str, torch.Tensor]:
        unit_map = torch.zeros([self.width, self.height], dtype=torch.int32)
        indestructible_map = torch.zeros([self.width, self.height], dtype=torch.int32)
        destructible_map =  torch.zeros([self.width, self.height], dtype=torch.int32)
        # pickup_map = torch.zeros([self.width, self.height], dtype=torch.int32)
        radius_map = torch.zeros([self.width, self.height], dtype=torch.int32)
        ammo_map = torch.zeros([self.width, self.height], dtype=torch.int32)
        ## bomb has 3 dimensions for expiration, hp, and blast diameter
        bomb_map = torch.zeros([self.width, self.height], dtype=torch.int32)
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

        for entitiy in self.entities:
            class_map = table[type(entitiy)]

            class_map[entitiy.coord.x, entity.coord.y] = entity.call()
            

        return None

        # return {
        #     "occupancy": occupancy_map,
        #     "explosions": ...,
        # }

    ## Move units, etc
    def tick(actions: Dict[Entity, Action]) -> BoardState:
        pass

