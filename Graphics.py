import pygame


def getDisplay():
    return pygame.display.Info()


class Window:
    defX, defY = 0, 0
    display = None
    window = None

    currMode = None

    def __init__(self, dx, dy, vx, vy, mode, vsync):
        width, height = vx, vy
        self.defX, self.defY = dx, dy
        self.window = pygame.display
        self.currMode = mode
        self.display = self.window.set_mode((width, height), mode, vsync=vsync)

    def changeResolutionMode(self, dx, dy):
        self.window.set_mode((dx, dy))

    def getDisplay(self):
        return self.window.Info()


class Graphics:
    getTicksLastFrame = 0
    currWin = None

    def __init__(self, newWindow: Window):
        self.currWin = newWindow
        self.getTicksLastFrame = 0

    # DELTA SYSTEM
    def delta(self):
        t = pygame.time.get_ticks()
        # deltaTime in seconds.
        deltaTime = (t - self.getTicksLastFrame) / 1000.0
        self.getTicksLastFrame = t
        return deltaTime

    def getFPS(self):
        delta = self.delta()
        return 1 / delta

    def loopX(self, tileX, IDX, camX, tileSize):
        newX = tileX
        newIDX = IDX
        if (tileX < -(tileSize * 3)):
            newX = (self.currWin.defX * (self.currWin.getDisplay().current_w / self.currWin.defX) - (
                    tileX + tileSize)) + camX
            newIDX += 40
        return newX, newIDX

    def displayTable(self, map, dx, dy, screen, camX, camY):
        screen.fill((0, 0, 0))
        tileSize = 16 * (self.currWin.getDisplay().current_w / self.currWin.defX)
        IDY = 0
        for y in range(dy + 1):
            for x in range(dx + 1):


                # tileRect = tileSprite.get_rect()
                IDX = x
                IDY = y
                tileX = (x * tileSize) + camX
                tileY = (y * tileSize) + camY
                screen_width = self.currWin.defX * (self.currWin.getDisplay().current_w / self.currWin.defX)
                screen_height = self.currWin.defY * (self.currWin.getDisplay().current_h / self.currWin.defY)

                # **Wrap Tiles Horizontally**
                if tileX + tileSize < 0:
                    tileX += screen_width + tileSize  # Bring tile back in from the right
                    IDX += dx
                #elif tileX > screen_width:
                #    tileX -= screen_width + tileSize  # Wrap to the left

                # **Wrap Tiles Vertically**
                if tileY + tileSize < 0:
                    tileY += screen_height + (tileSize + (tileSize // 2))  # Bring tile back in from the bottom
                    IDY += dy
                #elif tileY > screen_height:
                #    tileY -= screen_height + tileSize  # Wrap to the top

                tileSprite = map[IDY][IDX]
                tileSprite = pygame.transform.scale(tileSprite, (tileSize, tileSize))
                screen.blit(tileSprite, (tileX, tileY))

        # Update the display
        pygame.display.flip()
