# DO NOT USE THIS ON THE WINDOWS MACHINE!!!!!
# (see note below)
#
# This file is part of GoBananas
#
# GoBananas is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 2.1 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Maria Mckinley

# Converting on the Windows machine is just not working! Bam files created
# cannot be loaded (no error message, but window stays blank). Create on
# Mac and move to Windows, that works fine
#
# To convert all models in my model directory from gobananas directory on my mac:
# arch -i386 ppython myEggToBam.py
#
# To convert one file:
# start python in gobananas directory:
# arch -i386 ppython
# from myEggToBam import convertEggToBam
# convertEggToBam('../../play/play_models/play_field.egg')


import direct.directbase.DirectStart
import os


def convertEggToBam(eggFile):
    """
    Load the given .egg file and convert it to .bam.
    """

    #print eggFile
    bamFile = eggFile[:-4] + ".bam"
    model = loader.loadModel(eggFile)
    model.writeBamFile(bamFile)
    #print 'ok'


def convert_all():
    # Load config file values.
    config = {}

    execfile("config.py", globals(), config)

    # Terrain, sky.
    #convertEggToBam(config['terrainModel'][:-4]+".egg")
    #convertEggToBam(config['skyModel'][:-4]+".egg")

    # all bam files (this converts a lot we don't need...):
    for directory in mylistdir('./models'):
        #print 'directory', directory
        temp = os.path.join('./models', directory)
        #print temp
        for filename in os.listdir(temp):
            #print 'filename', filename
            #print filename[:-4]
            if filename[-4:] == '.egg':
                print 'convert'
                print os.path.join(temp, filename)
                convertEggToBam(os.path.join(temp, filename))

def mylistdir(directory):
    """A specialized version of os.listdir() that ignores files that
    start with a leading period."""
    filelist = os.listdir(directory)
    return [x for x in filelist
            if not (x.startswith('.'))]

    # Stores.
    #for filename in os.listdir(config['storeDir']):
    #    if filename[-4:] == ".egg":
    #        convertEggToBam(os.path.join(config['storeDir'], filename))

    # Buildings.
    #for filename in os.listdir(config['buildingDir']):
    #    if filename[-4:] == ".egg":
    #        convertEggToBam(os.path.join(config['buildingDir'], filename))

if __name__ == '__main__':
    convert_all()
