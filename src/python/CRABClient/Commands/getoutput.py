from CRABClient.Commands.getcommand import getcommand
from CRABClient.ClientUtilities import initLoggers
        

from CRABClient.ClientExceptions import ConfigurationException


class getoutput(getcommand):
    """ Retrieve the output files of a number of jobs specified by the -q/--quantity option. The task
        is identified by the -d/--dir option
    """
    name = 'getoutput'
    shortnames = ['output', 'out']
    visible = True #overwrite getcommand

    def __call__(self, **argv):
        
        mod = __import__('CRABClient.Commands.status2', fromlist='status2')

        _, logger, _ = initLoggers()
        cmdobj = getattr(mod, 'status2')(logger)
        _, jobList = cmdobj.__call__()
        jobList = jobList['jobList']

        transferringIds = [x[1] for x in jobList if x[0] in ['transferring', 'cooloff', 'held']]
        finishedIds = [x[1] for x in jobList if x[0] in ['finished', 'failed', 'transferred']]

        possibleJobIds = transferringIds + finishedIds
        
        if not self.options.jobids:
            self.options.jobids = []
        
        ## Check that the jobids passed by the user are in a valid state to retrieve files.
        import pdb
        pdb.set_trace()
        if self.options.jobids:
            for jobid in self.options.jobids:
                if not str(jobid[1]) in possibleJobIds:
                    raise ConfigurationException("The job with id %s is not in a valid state to retrieve output files" % jobid[1])
        else:
            ## If the user does not give us jobids, set them to all possible ids.
            self.options.jobids = []
            for jobid in possibleJobIds:
                self.options.jobids.extend([('jobids', jobid)])
            
        # TODO: process the quantity parameter
#         else:
#             howmany = -1 #if the user specify the jobids return all possible files with those ids

#         taskname = self.cachedinfo['RequestName']
#         uri = self.getUrl(self.instance, resource = 'workflow')
#         serverFactory = CRABClient.Emulator.getEmulator('rest')
#         server = serverFactory(self.serverurl, self.proxyfilename, self.proxyfilename, version=__version__)
#         test, a, b =  server.get(uri, data = {'subresource': 'data2', 'workflow': taskname, 'limit': howmany,
#                                                     'jobids': jobids})
        import pdb
        pdb.set_trace()

#         self.options.jobids = jobids

        returndict = getcommand.__call__(self, subresource = 'data2')
        return returndict

    #TODO: move to client utils
    def getColumn(self, dictresult, columnName):
        columnIndex = dictresult['desc']['columns'].index(columnName)
        value = dictresult['result'][columnIndex]
        return value


    def setOptions(self):
        """
        __setOptions__

        This allows to set specific command options
        """
        self.parser.add_option( '--quantity',
                                dest = 'quantity',
                                help = 'The number of output files you want to retrieve (or "all"). Ignored if --jobids is used.' )
        self.parser.add_option( '--parallel',
                                dest = 'nparallel',
                                help = 'Number of parallel download, default is 10 parallel download.',)
        self.parser.add_option( '--wait',
                                dest = 'waittime',
                                help = 'Increase the sendreceive-timeout in second',)
        getcommand.setOptions(self)
