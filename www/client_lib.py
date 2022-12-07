
import os
import sys
import requests
import json
import random
import time
import argparse
import datetime

debugLevel = 0

theConfiguration = {
    "theUrlBase":  "",
    "theUrlToken": "",
    "theUrl":      "",
    "theUsername": "",
    "thePassword": "",
    "theAuthorizationToken": None
}

def setUrlBase(base):
    global theConfiguration
    theConfiguration["theUrlBase"] = base
    theConfiguration["theUrlToken"] = theConfiguration["theUrlBase"] + "/token/"
    theConfiguration["theUrl"] = theConfiguration["theUrlBase"] + "/note"

def setUsername(username):
    global theConfiguration
    theConfiguration["theUsername"] = username

def setPassword(password):
    global theConfiguration
    theConfiguration["thePassword"] = password

#
# get JWT token
# MITICO! tutta la funzione
#
def getJWTToken():
    global debugLevel
    global theConfiguration
    resp = requests.post(url=theConfiguration["theUrlToken"],
                         # headers={"Content-Type": "application/json"}, 
                         data={'username': theConfiguration["theUsername"], 
                            'password': theConfiguration["thePassword"]})
    # print(theUrlToken)
    # if resp.status_code != 200:
    #     # print("Error: %s" % (resp.text))
    #     return resp.text
    # return resp.text
    return json.loads(resp.text)

def auxGetHeaders():
    global theConfiguration
    if theConfiguration["theAuthorizationToken"] is None:
        aus = getJWTToken()
        # print("token-refresh: %s" % (theAuthorizationToken['refresh']))
        # print("token-access: %s" % (theAuthorizationToken['access']))
        if 'access' in aus.keys():
            theConfiguration["theAuthorizationToken"] = {'Authorization': 'Bearer ' + aus['access']}
        else:
            print("Error: %s" % (aus))
            theConfiguration["theAuthorizationToken"] = None;
            sys.exit()
    if debugLevel > 0:
        print(theConfiguration["theAuthorizationToken"])
    return theConfiguration["theAuthorizationToken"]

# create a new note with a POST request
def createNote(rid, type, data):
    global theConfiguration
    resp = requests.post(url=theConfiguration["theUrl"],
                         headers = auxGetHeaders(), 
                         json={"rid": rid, "lid": 0, "type": type, "data": data})
    # print(resp.status_code)
    if (resp.status_code == 200 or resp.status_code == 201 or resp.status_code == 202 or resp.status_code == 203):
        return resp.json()['id']
    else:
        return -1

def createEntity(jsonInfo):
    entityType = jsonInfo['__ENT__']
    rid = createNote(rid=0, type=entityType, data="__ENT__")
    for key in jsonInfo:
        if (key != '__ENT__'):
            createNote(rid=rid, type=key, data=jsonInfo[key])

def getCurrentDate():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+0000")

def printNote(note):
    print(note)
    # print("%i,%i,%i,%s,%s\n" % (note['id'],note['rid'],note['lid'],note['type'],note['data']))
       
def auxGetAndReturnList(url):
    resp = requests.get(url=url, headers=auxGetHeaders())
    if (resp.status_code == 200):
        #print(resp.content)
        #print(resp.json())
        return resp.json()
    else:
        return []

def getAllNotes():
    return auxGetAndReturnList(theConfiguration["theUrl"])

def getNote(id):
    return auxGetAndReturnList(theConfiguration["theUrl"] + "/?id=%s" % (id))

def getNotesWithType(tagName):
    return auxGetAndReturnList(theConfiguration["theUrl"] + "/?type=%s" % (tagName))

def getAttributesOfNote(id):
    return auxGetAndReturnList(theConfiguration["theUrl"] + "/?rid=%d" % (id))

def getEntities(whichType):
    return auxGetAndReturnList(theConfiguration["theUrl"] + "/?type=%s&rid=0" % (whichType))

# TODO
def isEntityAttributeDuplicate(rid, type, data):
    pass

def addAttributeToEntity(entityId, type, data):
    return createNote(rid=entityId, type=type, data=data)

def checkType(thisType, noteList):
    if len(noteList)<1:
        return False
    return noteList[0]['type'] == thisType

def searchEntity(jsonInfo):
    entityType = jsonInfo['__ENT__']
    del jsonInfo['__ENT__']
    firstKey = list(jsonInfo.keys())[0]
    firstValue = jsonInfo[firstKey]
    noteList = auxGetAndReturnList(theConfiguration["theUrl"] + "/?type=%s&data=%s" % (firstKey, firstValue))
    idList = list(map(lambda x: x['rid'], noteList))
    resList = list(filter(lambda x: checkType(entityType, getNote(x)), idList))
    return resList

def getListOfAttributes(entityName):
    entities = getEntities(entityName)
    list = []
    if len(entities) <= 0:
        return list
    # TODO get a merge of attributes of all entities
    attr = getAttributesOfNote(entities[0]['id'])
    for n in attr:
        list.append(n['type']) 
    return list

def deleteNote(id):
    resp = requests.delete(url=theConfiguration["theUrl"] + "/" + str(id), headers=auxGetHeaders())
    return(resp)
