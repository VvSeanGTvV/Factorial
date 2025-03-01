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

    def displayTable(self, map, size, screen, camX, camY):
        screen.fill((0, 0, 0))
        for y in range(size):
            dataM = map[y]
            for x in range(size):
                tileSprite = dataM[x]
                tileSprite = pygame.transform.scale(tileSprite, (
                                                        16 * (self.currWin.getDisplay().current_w / self.currWin.defX),
                                                        16 * (self.currWin.getDisplay().current_h / self.currWin.defY))
                                                    )
                tileRect = tileSprite.get_rect()
                tileWidth, tileHeight = tileRect.width, tileRect.height
                screen.blit(tileSprite, ((tileWidth * x) + camX, (tileHeight * y) + camY))

        # Update the display
        pygame.display.flip()
