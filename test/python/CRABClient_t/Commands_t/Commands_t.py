import CRABRESTModelMock
from FakeRESTServer import FakeRESTServer
from Commands.server_info import server_info
from Commands.getoutput import getoutput
from Commands.status import status
from Commands import CommandResult
import client_default

import unittest
import logging
import os
import shutil
from socket import error as SocketError

class CommandTest(FakeRESTServer):

    def __init__(self, config):
        FakeRESTServer.__init__(self, config)
        self.setLog()

        client_default.defaulturi = {
            'submit' : '/unittests/rest/task/',
            'getlog' : '/unittests/rest/log/',
            'getoutput' : '/unittests/rest/data/',
            'reg_user' : '/unittests/rest/user/',
            'server_info' : '/unittests/rest/info/',
            'status' : '/unittests/rest/task/'
        }


    def setLog(self):
        self.logger = logging.getLogger("CommandTest")
        self.logger.setLevel(logging.DEBUG)


    def testServerInto(self):
        si = server_info(self.logger)

        #1) check that the right API is called
        res = si(["-s","localhost:8588"])
        expRes = CommandResult(0, CRABRESTModelMock.SI_RESULT)
        self.assertEquals(expRes, res)

        #2) wrong -s option: the user give us an address that does not exists
        self.assertRaises(SocketError, si, ["-s","localhos:8588"])


    def testGetStatus(self):
        s = status(self.logger)

        #1) missing required -t option
        expRes = CommandResult(1, 'Error: Task option is required')
        res = s([])
        self.assertEquals(expRes, res)

        #2) correct execution
        analysisDir = os.path.join(os.path.dirname(__file__), 'crab_AnalysisName')
        res = s(["-t", analysisDir])
        expRes = CommandResult(0, None)
        self.assertEquals(expRes, res)

        #3) wrong -t option
        analysisDir = os.path.join(os.path.dirname(__file__), 'crab_XXX')
        self.assertRaises( IOError, s, ["-t", analysisDir])

    def testGetOutput(self):
        """
        Crete a fake source output file and verify it is copied to the correct
        dest directory
        """
        #f = open("src_output.root", 'w')
        #f.close()

        #1) missing required -t option (the other required option, -r, is ignored)
        go = getoutput(self.logger)
        res = go([])
        expRes = CommandResult(1, 'Error: Task option is required')

        #2) -t option is present but -r is missing
        analysisDir = os.path.join(os.path.dirname(__file__), 'crab_AnalysisName')
        res = go(["-t", analysisDir])
        expRes = CommandResult(1, 'Error: Range option is required')

        #3) request passed with the -t option does not exist
        #res = go(["-t", analysisDir + "asdf"])
        #TODO we expect an appropriate answer from the server

        #4) check correct behaviour without specifying output directory
        #N.B.: -p options is required for tests to skip proxy creation and delegation
        res = go(["-t", analysisDir, "-r", "20", "-p"])
        expRes = CommandResult(0, None)
        #check if the result directory has been created
        destDir = os.path.join(analysisDir, 'results')
        self.assertTrue(os.path.isdir(destDir))
        #Remove the directory
        shutil.rmtree(destDir)
        self.assertFalse(os.path.isdir(destDir))

        #5) correct behavior and output directory specified which exists
        res = go(["-t", analysisDir, "-r", "20", "-o", "/tmp", "-p"])
        expRes = CommandResult(0, None)
        #check if the result directory has been created
        self.assertTrue(os.path.isdir('/tmp'))
        #TODO check tath the file has been copied

        #6) correct behavior and output directory specified which does not exists
        res = go(["-t", analysisDir, "-r", "20", "-o", "/tmp/asdf/qwerty", "-p"])
        expRes = CommandResult(0, None)
        #check if the result directory has been created
        self.assertTrue(os.path.isdir('/tmp/asdf/qwerty'))
        #Remove the directory
        shutil.rmtree('/tmp/asdf/qwerty')



if __name__ == "__main__":
    unittest.main()

