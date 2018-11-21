# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 17:59:16 2018

@author: jelha
"""

commandList = {
               "help" : "lists out all commands",
               "excuse (MEETING NAME) (MEETING EXCUSE)": "Submits an excuse an upcoming mandatory meeting",
               "more" : "more commands incoming!"
               }

def helpCommand():
    #Still need to look into how to format messages so that they return pretty.
    response = ""
    for comm in commandList.keys():
        response = response + comm + " : " + commandList[comm] + "\n"
    return response