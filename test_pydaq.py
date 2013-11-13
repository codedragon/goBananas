import unittest
import pydaq
import time

class PyDAQTests(unittest.TestCase):

    def testGiveReward(self):
        task = pydaq.GiveReward()
        task.pumpOut()
        choice = raw_input('Did you hear a beep? y/n\n')
        self.assertTrue(choice == 'y')

    def testEOGTask(self):
        task = pydaq.EOGTask()
        future = time.time() + 0.1
        task.StartTask()
        while time.time() < future:
            pass
        #    print task.EOGData
        task.StopTask()
        print task.EOGData
        task.ClearTask()
        self.assertTrue(len(task.EOGData) == 2)
        # should not be exactly zero if really getting data
        self.assertNotIn(0, task.EOGData)

if __name__ == "__main__":
    unittest.main()
