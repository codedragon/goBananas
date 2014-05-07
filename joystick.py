from direct.showbase.DirectObject import DirectObject
from direct.showbase.MessengerGlobal import messenger
PYGAME_LOADED = True
try:
    import pygame
except ImportError:
    PYGAME_LOADED = False
    print 'Pygame not found, necessary for joystick use'


class JoystickHandler(DirectObject):
    def __init__(self):
        if not PYGAME_LOADED:
            return
        pygame.init()
        pygame.joystick.init()
        #print pygame.joystick.get_count()
        # do I want to load more than one?
        self.joystick_found = True
        self.count = 0
        try:
            self.js = pygame.joystick.Joystick(0)
            self.js.init()
            taskMgr.add(self.joystick_polling, 'Joystick Polling')
        except pygame.error, message:
            print "Need to plug in a joystick"
            raise SystemExit(message)

    def destroy(self):
        pygame.quit()

    def get_joysticks(self):
        return self.js

    def get_count(self):
        return len(self.js)

    def joystick_polling(self, task):
        # if joystick is not moving, does not send an event, but may be holding steady...
        #print 'task poll'
        # before you move the joystick, center is registered as zero, but as soon as you
        # move the joystick, center seems to no longer be zero.
        # second sample from y is always maxed out instead of zero, why?
        # don't send first 5 samples for now. (Gives y a chance to come back to center,
        # seems to work

        for ev in pygame.event.get():
            if ev.type is pygame.JOYAXISMOTION:
                if self.count < 5:
                    #print 'pass'
                    self.count += 1
                else:
                    if ev.axis == 0:
                        axis = 'x_axis'
                        messenger.send(axis, [ev.value])
                    elif ev.axis == 1:
                        axis = 'y_axis'
                        messenger.send(axis, [ev.value])
        return task.cont

