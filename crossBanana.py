from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.showbase.MessengerGlobal import messenger

pygame_found = True
try:
    import pygame
except ImportError:
    pygameFound = False
    print 'Pygame not found, necessary for joystick use'


class JoystickHandler(DirectObject):
    def __init__(self):
        if not pygame_found:
            return
        pygame.init()
        pygame.joystick.init()
        count = pygame.joystick.get_count()
        # do I want to load more than one?
        for i in range(count):
            self.joystick_found = True
            js = pygame.joystick.Joystick(i)
            js.init()
            self.js.append(js)
        taskMgr.add(self.joystick_polling, 'Joystick Polling')

    def destroy(self):
        pygame.quit()

    def get_joysticks(self):
        return self.js

    def get_count(self):
        return len(self.js)

    def joystick_polling(self, task):
        for ev in pygame.event.get():
            if ev.type is pygame.JOYAXISMOTION:
                name = 'joystick%d-axis%d' % (ev.joy, ev.axis)
                messenger.send(name, [ev.value])


class CrossBanana(JoystickHandler):
    def __init__(self):
        self.base = ShowBase()
        JoystickHandler.__init__(self)
        config = {}
        execfile('config_test.py', config)
        self.cross_pos = config['xStartPos']
        self.cross_move = config['xHairDist']

        self.accept('joystick0-axis2', self.steer)
        print 'ok then'

if __name__ == "__main__":
    CB = CrossBanana()
    run()