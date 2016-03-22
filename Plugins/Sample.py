#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
This is a sample plugin.
"""

__author__ = 'Nb'


class PluginAgent:
    """
    This class, as required by the plugin 'interface', provides methods for
    plugin manager to initialise, control and dispose the plugin.\n
    It includes following methods:\n
    Start - static method to initialise the plugin\n
    Stop - static method to stop the plugin
    """

    # Observing list stores the names of functions this plugin
    # wishes to observe. Notice that this name should be the same
    # as the one provided by the function itself.
    # In this sample it observes a function 'Astra' from Loader.Astra.
    observingList = ['Astra']

    @staticmethod
    def Start():
        """Start method will be called while being loaded."""
        print('INFO: Plugin %s started.' % __file__.split('/')[-1][:-3])

    @staticmethod
    def Stop():
        """Stop method will be called while being disposed."""
        print('INFO: Plugin %s stopped.' % __file__.split('/')[-1][:-3])

    @staticmethod
    def Receive(functionName: str, *args, **kwargs):
        """
        Receive method performs the addition procedure of observed functions.\n
        It takes a function name and a preliminary result of that function.
        Then it performs certain secondary procedure according to the given
        function name.\n
        In this sample it only perform a self increment for 'Astra' function.
        """
        # make sure that given function name is valid
        assert functionName in PluginAgent.observingList
        if functionName == 'Astra':
            return 'Nb'
        else:
            return args[0]
