# My Story

## And so it begins ...
Start the story with an initial dialogue
The Text can contain "###" Headings and other markdown
### Heading within the initial dialogue
Some other text. All empty lines are ignored

- Heading of second dialogue: One option to continue the story with
the second dialogue.
Can contain markdown as well.

- The saga continues: Description of other option

## Heading of second dialogue
LOGIC self.properties["some_property"] = "some_value"

Some description of the second dialogue. Can also contain markdown

- And so it begins ...: Desciption of option that leads back to
the initial dialogue

- The saga continues: Desciption of option that leads to the next
dialogue.

## The saga continues
LOGIC if self.properties.get("some_property","") == "some_value":
LOGIC    self.next_dialog("The saga continues (if some_property is some_value)")

Some description of this dialogue.
The property "some_property" is not "some_value"

- And so it begins ...: Desciption of option that leads back

## The saga continues (if some_property is some_value)
This is the next dialogue if the property "some_property" is "some_value"

- And so it begins ...: Desciption of option that leads back
