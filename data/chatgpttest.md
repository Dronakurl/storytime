
# Dragon on the Mountain Wurst

## The beginning
LOGIC self.properties["health"] = 100
LOGIC self.properties["has_sword"] = False

You are a brave adventurer standing at the base of the mighty Mountain Wurst. Legends speak of a fearsome dragon that guards its peak. Your quest is to defeat the dragon and claim its treasure.

- Approach the mountain: Begin your ascent

- Search for a sword: Look for a weapon before climbing

## Search for a sword
LOGIC self.properties["has_sword"] = True

You explore the nearby village and find a blacksmith who offers to sell you a powerful sword. With the sword in hand, you feel more confident in your ability to face the dragon.

- Approach the mountain: Begin your ascent

## Approach the mountain
LOGIC self.properties["health"] -= 20

You start your treacherous climb up the steep slopes of Mountain Wurst. The air becomes thinner, and the temperature drops significantly. As you ascend, you start feeling weaker, losing 20 health due to the challenging conditions.

- Rest and recover: Take a short break to regain strength

- Continue climbing: Push through the difficulties

## Rest and recover
LOGIC self.properties["health"] += 10

You find a sheltered spot and rest for a while, allowing your body to recover. The break revitalizes you, and you regain 10 health points.

- Continue climbing: Resume your ascent

## Continue climbing
LOGIC self.properties["health"] -= 30

You press on, determined to reach the dragon's lair. The path becomes even more treacherous, and you suffer from exhaustion and minor injuries, losing 30 health points.

- Confront the dragon: Face the beast head-on

- Retreat: Descend the mountain and rethink your strategy

## Retreat
LOGIC self.next_dialogue = "Rethink strategy"

You decide to retreat for now, understanding that you need to prepare better before confronting the dragon. You descend the mountain and return to the village to rethink your strategy.

## Rethink strategy

You take your time to regroup and gather valuable information about the dragon's weaknesses. After thorough preparation, you once again stand at the base of Mountain Wurst, ready to face the dragon.

- Approach the mountain: Begin your ascent

## Confront the dragon
LOGIC if self.properties["has_sword"]:
LOGIC     self.next_dialog("Victory")
LOGIC else:
LOGIC     self.next_dialog("Defeat")

With sword in hand, you boldly enter the dragon's lair. The dragon awakens, roaring with fury. The battle begins!

## Victory
CONCLUSION Congratulations! With a well-placed strike, you defeat the dragon, claiming its treasure as your own. You emerge from the mountain victorious, a legendary hero!

## Defeat
CONCLUSION Alas, without a proper weapon, you stand no chance against the mighty dragon. It overwhelms you with its fiery breath, leaving you defeated. Your quest ends here, but the legend of the dragon on the Mountain Wurst lives on.
