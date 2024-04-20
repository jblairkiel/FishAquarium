import pygame as pg


class Inspector:
    def __init__(self):
        self.currentItem = None
        self.hidden = True

    def toggleShow(self):
        if self.hidden == True:
            self.hidden = False
        else:
            self.hidden = True

    def drawPane(self, screen, gameWidth, gameHeight, mosX, mosY):
        if self.currentItem != None:
            # Draw Pane
            pg.draw.rect(
                screen, (40, 40, 40), pg.Rect(gameWidth - 300, 0, 300, gameHeight)
            )

            # Type Mouse Cursor Pos Bottom
            fontSize = 20
            font = pg.font.SysFont("comicsansms", fontSize)
            mouseText = font.render(
                "X: " + str(mosX) + " Y: " + str(mosY), True, (120, 50, 20)
            )
            screen.blit(mouseText, (gameWidth - 250, gameHeight - 50))

            drawingYIter = 60
            if self.currentItem != None:
                # Draw Fish at top
                pg.draw.rect(
                    screen,
                    self.currentItem.color,
                    pg.Rect(
                        gameWidth - 150,
                        drawingYIter,
                        self.currentItem.lenX,
                        self.currentItem.lenY,
                    ),
                )
                drawingYIter += self.currentItem.lenY + 10

                # Label Descriptions
                fishAttributes = [
                    a
                    for a in dir(self.currentItem)
                    if not a.startswith("__")
                    and not callable(getattr(self.currentItem, a))
                ]
                for attr in fishAttributes:
                    drawingYIter += 10 + fontSize
                    val = getattr(self.currentItem, attr)
                    attrText = font.render(attr + ": " + str(val), True, (120, 50, 20))
                    screen.blit(attrText, (gameWidth - 225, drawingYIter))
