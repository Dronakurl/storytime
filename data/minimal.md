# Harry in the woods

## The beginning
LOGIC PROPERTY "Health Points" = 100 

Harry is in the woods. He is lost. He is looking for a way out.

- Turn to the castle: Go to the big castle

- Go left: Turn left on the path

## Go left
LOGIC PROPERTY "Health Points" = "Health Points" - 10

Harry is attacked by a bear. He loses 10 health.

- Turn to the castle: Go to the big castle

## Turn to the castle
LOGIC NEXTDIALOG "Injured" if self.properties.get("Health Points",100) < 100:
LOGIC     self.next_dialog("Injured")

Harry is not injured and arrives at the castle. He is greeted by a wizard.

## Injured
LOGIC self.properties["Health Points"] = 100

Harry is injured. The wizard heals him.

