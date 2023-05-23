# Title of my Story

## Starting dialogue
Start the story with an initial dialogue

- Heading of second dialogue: Description of option that leads to the next

- Title of another option: Description of other option

## Heading of second dialogue
LOGIC self.properties["some_property"] = "some_value"

Some description of the second dialogue. 

- And so it begins ...: Description of option that leads back to the first

- Title of another option: Description of option that leads to the next

## Title of another option
LOGIC if self.properties.get("some_property","") == "some_value":
LOGIC    self.next_dialog("Conditional dialogue")

Some description of this dialogue.

- Starting dialogue: Description of option that leads back

## Conditional dialogue
This is the next dialogue if the property "some_property" is "some_value"

- Starting dialogue: Description of option that leads back
