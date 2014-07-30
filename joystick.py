from direct.showbase.DirectObject import DirectObject
from direct.showbase.MessengerGlobal import messenger
from direct.task.TaskManagerGlobal import taskMgr
PYGAME_LOADED = True
try:
    import pygame
except ImportError:
    PYGAME_LOADED = False
    pygame = None
    print 'Pygame not found, necessary for joystick use'


class JoystickHandler(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        if not PYGAME_LOADED:
            return
        pygame.init()
        pygame.joystick.init()
        js_count = pygame.joystick.get_count()
        if js_count > 1:
            code = "More than one joystick connected"
            raise JoystickError(code)
        self.joystick_found = True
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

        for ev in pygame.event.get():
            if ev.type is pygame.JOYAXISMOTION:
                if ev.axis == 0:
                    axis = 'x_axis'
                    messenger.send(axis, [ev.value])
                elif ev.axis == 1:
                    axis = 'y_axis'
                    messenger.send(axis, [ev.value])
        return task.cont


class JoystickError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)