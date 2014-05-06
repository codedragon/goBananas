from direct.showbase.DirectObject import DirectObject
from direct.showbase.MessengerGlobal import messenger
PYGAME_LOADED = True
try:
    import pygame
except ImportError:
    PYGAME_LOADED = False
    print 'Pygame not found, necessary for joystick use'


class JoystickHandler(DirectObject):
    def __init__(self, tolerance=None):
        if not PYGAME_LOADED:
            return
        print tolerance
        if tolerance is None:
            self.threshold = 0.2
        else:
            self.threshold = tolerance
        print self.threshold
        pygame.init()
        pygame.joystick.init()
        #print pygame.joystick.get_count()
        # do I want to load more than one?
        self.joystick_found = True
        try:
            self.js = pygame.joystick.Joystick(0)
            self.js.init()
            taskMgr.add(self.joystick_polling, 'Joystick Polling')
        except pygame.error, message:
            "Need to plug in a joystick"
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
        js_input = None
        for ev in pygame.event.get():
            if ev.type is pygame.JOYAXISMOTION:
                if ev.axis == 0:
                    axis = 'x_axis'
                else:
                    axis = 'y_axis'
                messenger.send(axis, [ev.value])
                #print ev.value
                #print self.threshold
                #print 'move'
                #name = 'joystick%d-axis%d' % (ev.joy, ev.axis)
                # if abs(ev.value) > self.threshold:
                #     #print 'made threshold'
                #     if ev.axis == 0:
                #         if ev.value < 0:
                #             js_input = 'js_left'
                #         elif ev.value > 0:
                #             js_input = 'js_right'
                #     elif ev.axis == 1:
                #         if ev.value > 0:
                #             js_input = 'js_down'
                #         elif js_input < 0:
                #             js_input = 'js_up'
                #     messenger.send(js_input, [ev.value])
                #     #print '%s: %s' % (pygame.event.event_name(ev.type), ev.dict)
                # else:
                #     messenger.send('let_go', [0])
        return task.cont

