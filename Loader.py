#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
This architecture implements a very simple plugin system which includes
a plugin loader and a directory for storing plugins.
"""

__author__ = 'Nb'

import os

# this flag assists the singleton implementation of PluginLoader
# see PluginLoader.__new__ for more detail
__MANAGER__ = None


class PluginLoader:
    """
    This is the loader class for scanning and loading plugins.\n
    All plugins are required to implement a PluginAgent class which
    includes Start, Stop and Receive methods and name, version and author fields.\n
    Predefined directory is ./Plugins.
    """

    # information of loader itself
    # also available to all plugins
    LOADER_NAME = 'PluginLoader'
    LOADER_VERSION = 1.2
    LOADER_PLUGIN_DIRECTORY = 'Plugins'

    def __init__(self):
        # a dict storing all plugins in name - module set
        self._pluginList = {}
        self._validNameList = set()  # using set for better performance
        self._observerList = {}

    def __new__(cls, *args, **kwargs):
        """
        Ensures that only one PluginLoader instance will be created.\n
        When a class is being constructed, its __new__ method is the first
        to be called and this function overrides the default __new__ method
        of Object and uses a global variable __MANAGER__ to store the only
        instance. If __MANAGER__ is None, in other words no instance has been
        created yet, then create an instance and return it. Otherwise it would
        return __MANAGER__ directly.\n
        The purpose of making this class a singleton is to improve its robustness
        and prevent situations like two PluginLoaders trying to call the same
        plugin agent at the same time.
        """
        global __MANAGER__
        if __MANAGER__ is None:
            __MANAGER__ = object.__new__(cls, *args, **kwargs)
        return __MANAGER__

    def LoadPlugin(self):
        # concat plugin path
        pluginPath = os.path.join(os.path.dirname(__file__), self.LOADER_PLUGIN_DIRECTORY)

        # scan all plugins and import them if valid
        for rootName, dirName, fileNames in os.walk(pluginPath):
            if fileNames:
                for fileName in fileNames:
                    if fileName.endswith('.py') and not fileName.startswith('__init__'):
                        moduleName = fileName[:-3]
                        # see __import__ documentation for more details
                        self._pluginList[moduleName] = __import__(
                            name='Plugins.%s' % moduleName,
                            globals=globals(), locals=locals(),  # namespaces
                            fromlist=[moduleName]  # names of submodules to be imported
                        )

        # call start method defined in the PluginAgent
        removalList = []
        for name, plugin in self._pluginList.items():
            try:
                plugin.PluginAgent.Start()
            # if contract class or method is not found
            except AttributeError as e:
                print('ERROR: Error initialising plugin %s -> %s\n'
                      'ERROR: Please make sure it has properly implemented PluginAgent.'
                      % (name, e))
                removalList.append(name)
            # if error occurs during execution of Start
            except Exception as e:
                print('ERROR: Error initialising plugin %s -> %s\n'
                      'ERROR: Please check if there is any bug in PluginAgent.Start.'
                      % (name, e))
                removalList.append(name)
            # if no error happens then initialise its observer list
            else:
                self._observerList[name] = [] + plugin.PluginAgent.observingList

        # remove invalid plugin
        for removalPlugin in removalList:
            self._pluginList.pop(removalPlugin)

    def Callback(self, functionName: str, result):
        """
        Transfer the result of function being observing to the observer plugin.\n
        Send result of original function to the plugin who is observing given function name
        so that they can perform further process.
        """
        # check function name validity
        assert functionName in self._validNameList
        # check observer list and send result to observing plugin
        for pluginName, observingList in self._observerList.items():
            if functionName in observingList:
                print('INFO: Plugin %s is intercepting function %s' % (pluginName, functionName))
                return self._pluginList[pluginName].PluginAgent.Receive(functionName, result)
        # if no plugin is observing this name then return the original result
        return result


# initialise the plugin manager
PluginManager = PluginLoader()
PluginManager.LoadPlugin()


def OpenToPlugin(functionName):
    """
    Decorator for marking a function as open to plugin.\n
    While decorating, it register the given function name into the valid name list.
    Notice that the function name has to be unique.\n
    When decorated function is called, the original function runs first and the result
    is then transferred to PluginManager.Callback which would send the result to observing
    plugins for further process and then return that result back to normal procedure.
    """
    PluginManager._validNameList.add(functionName)

    def _PluginMixin(function):
        def __PluginMix(*args, **kwargs):
            result = function(*args, **kwargs)
            return PluginManager.Callback(functionName, result)

        return __PluginMix

    return _PluginMixin


# A sample function for showing how this decorator works
# It registers itself as 'Astra' and should return 6 if not interfered.
# However, the sample plugin has 'Astra' in its observing list and in that case
# the call of this function will be intercepted and the result would be changed
# to 7.
@OpenToPlugin('Astra')
def Astra():
    return 6


# try if it works
# then change the function name provided for decorator and try again
print('INFO: Result of sample function is %s' % Astra())
