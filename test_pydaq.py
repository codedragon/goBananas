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
        eye_data_x = []
        eye_data_y = []
        future = time.time() + 0.1
        task.StartTask()
        while time.time() < future:
            #print task.EOGData
            eye_data_x.append(task.EOGData[0])
            eye_data_y.append(task.EOGData[1])
        #    print task.EOGData
        task.StopTask()
        print len(eye_data_x)
        x = eye_data_x[-20:]
        y = eye_data_y[-20:]
        for row in zip(x, y):
            print row
        print task.EOGData
        task.ClearTask()
        self.assertTrue(len(task.EOGData) == 2)
        # should not be exactly zero if really getting data
        self.assertNotIn(0, task.EOGData)

if __name__ == "__main__":
    unittest.main()
