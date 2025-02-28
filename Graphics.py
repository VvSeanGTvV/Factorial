import pygame


class Graphics:
    getTicksLastFrame = 0

    def __init__(self):
        self.getTicksLastFrame = 0

    def delta(self):
        t = pygame.time.get_ticks()
        # deltaTime in seconds.
        deltaTime = (t - self.getTicksLastFrame) / 1000.0
        self.getTicksLastFrame = t
        return deltaTime

    def displayTable(self, map, screen, camX, camY):
        print(len(map))
        size = (len(map))
        screen.fill((0, 0, 0))
        for y in range(size // 2):
            for x in range(size // 2):
                try:
                    tileSprite = map[x + y]
                    tileRect = tileSprite.get_rect()
                    screen.blit(tileSprite, ((tileRect.width * x) + camX, (tileRect.height * y) + camY))
                except:
                    print("[GR] OUT OF ALIGN")

        # Update the display
        pygame.display.flip()