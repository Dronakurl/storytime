# Story title

## First dialogue
LOGIC PROPERTY "A property" = 100 

Description of the first dialogue. Contains a description of the situation.
Syntax remark (not shown in the story). The following choices are marked with a dash. 
The text before the colon is the heading of the dialogue to be shown when 
the choice is selected. The text after the colon is the description of the choice.

- Next dialogue: Description of the choice. 

- Other Next dialogue: Another description

## Next dialogue
LOGIC PROPERTY "A property" = "A property" - 10

Description of the situation after the first choice. 

- Other Next dialogue: Description to the dialogue with heading "Other Next dialogue"

## Other Next dialogue
LOGIC NEXTDIALOG "A fourth dialogue" IF "A property" < 100

This dialogue is only shown if the condition after IF is false.
Otherwise, the dialogue "Injured" is shown.

- First dialogue: Description of the choice leading to the first dialogue, as "First dialogue" is the heading
 
## A fourth dialogue
LOGIC "A property" = 100

Another description of the situation. No choices are available, end of the story.
