# Harry in the woods

## The beginning
LOGIC PROPERTY "Health Points" = 100 

Harry is in the woods. He is lost. He is looking for a way out.

- Turn to the castle: Go to the castle

- Go left: Turn left on the path

## Go left
LOGIC PROPERTY "Health Points" = "Health Points" - 10

Harry is attacked. He loses 10 health.

- Turn to the castle: Go to the castle

## Turn to the castle
LOGIC NEXTDIALOG "Injured" IF "Health Points" < 100

This dialogue is only shown if the condition after IF is false, i.e. if Harry is not injured.
Otherwise, the dialogue "Injured" is shown.

## Injured
LOGIC "Health Points" = 100

Harry is injured. The wizard heals him.

