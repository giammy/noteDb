#!/usr/bin/env python3
import os
import sys
import requests
import json
import random
import time
import argparse
import datetime

# GUI
import PySimpleGUI as sg
import random
import string

import client_input

debugLevel = 0

#
# a command line interface to REST API of notes
# to get help use: ./client.py --help
#
# some usage examples:
# ./client.py --createEntity '{"__ENT__":"PC", "OWNER":"name1", "LOCATION":"office1"}'
# ./client.py --listEntities STAFFMEMBER   
# ./client.py --searchEntity '{"__ENT__":"PC", "OWNER":"name1"}'     
# ./client.py --searchEntity '{"__ENT__":"STAFFMEMBER", "GROUPNAME":"Group2"}'
# ./client.py --getEntity 6 

# theUrl = "http://127.0.0.1:8000/note"
# theUrl = "http://192.168.1.80/note"
theUrlBase = "http://127.0.0.1:8000"
theUrlToken = theUrlBase + "/token/" # the url to get the JWT token
theUrl = theUrlBase + "/note"


theUsername = ""
thePassword = ""
theAuthorizationToken = None


#
# the following 2 functions create an example entity called STAFFMEMBER, 
# they are invoked by the option --createManyStaffMembers NUM
# to fill the database for testing purposes
#
def createStaffMember(username, email, secondaryEmail, name, surname, groupName, leaderOfGroup, created, validFrom, validTo, note, officePhone, officeLocation, lastChangeAuthor, lastChangeDate):
    rid = createNote(rid=0, type="STAFFAGENDA", data="null") # if data="", the note is created with return code 400
    createNote(rid=rid, type="USERNAME", data=username)
    createNote(rid=rid, type="EMAIL", data=email)
    createNote(rid=rid, type="SECONDARYEMAIL", data=secondaryEmail)
    createNote(rid=rid, type="NAME", data=name)
    createNote(rid=rid, type="SURNAME", data=surname)
    createNote(rid=rid, type="GROUPNAME", data=groupName)
    createNote(rid=rid, type="LEADEROFGROUP", data=leaderOfGroup)
    createNote(rid=rid, type="CREATED", data=created)
    createNote(rid=rid, type="VALIDFROM", data=validFrom)
    createNote(rid=rid, type="VALIDTO", data=validTo)
    createNote(rid=rid, type="NOTE", data=note)
    createNote(rid=rid, type="OFFICEPHONE", data=officePhone)
    createNote(rid=rid, type="OFFICEPHONE2", data=officePhone)
    createNote(rid=rid, type="OFFICELOCATION", data=officeLocation)
    createNote(rid=rid, type="LASTCHANGEAUTHOR", data=lastChangeAuthor)
    createNote(rid=rid, type="LASTCHANGEDATE", data=lastChangeDate)
    createNote(rid=rid, type="AUTHREAD", data="AUTHENTICATED")
    createNote(rid=rid, type="AUTHWRITE", data="AUTHENTICATED")
    return rid

def createDemoEntries(num, par2):
    startTime = time.time()
    for i in range(0, num):
        createStaffMember(username="username%d" % (i), email="email%d@email.it" % (i), secondaryEmail="email%d@email.it" % (i), name="name%d" % (i), surname="surname%d" % (i), groupName="Group%d"%(random.randint(1, par2)), leaderOfGroup="leaderOfGroup%d" % (i), created="created%d" % (i), validFrom="validFrom%d" % (i), validTo="validTo%d" % (i), note="note%d" % (i), officePhone="officePhone%d" % (i), officeLocation="officeLocation%d" % (i), lastChangeAuthor="lastChangeAuthor%d" % (i), lastChangeDate="lastChangeDate%d" % (i))
    print("Created %d entries in %s seconds" % (num, time.time() - startTime))

#
# general functions
#

def getCurrentDate():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+0000")

def printNote(note):
    print(note)
    # print("%i,%i,%i,%s,%s\n" % (note['id'],note['rid'],note['lid'],note['type'],note['data']))

#
# get JWT token
# MITICO! tutta la funzione
#
def getJWTToken(username, password):
    global theUrlToken
    resp = requests.post(url=theUrlToken,
                         # headers={"Content-Type": "application/json"}, 
                         data={'username': username, 'password': password})
    # print(theUrlToken)
    # if resp.status_code != 200:
    #     # print("Error: %s" % (resp.text))
    #     return resp.text
    # return resp.text
    return json.loads(resp.text)

def auxGetHeaders():
    global theUrl
    global theUsername
    global thePassword
    global theAuthorizationToken
    if theAuthorizationToken is None:
        theAuthorizationToken = getJWTToken(theUsername, thePassword)
        # print("token-refresh: %s" % (theAuthorizationToken['refresh']))
        # print("token-access: %s" % (theAuthorizationToken['access']))

    if 'access' in theAuthorizationToken.keys():
        return {'Authorization': 'Bearer ' + theAuthorizationToken['access']}

    print("Error: %s" % (theAuthorizationToken))
    sys.exit()

def auxGetAndReturnList(url):
    resp = requests.get(url=url, headers=auxGetHeaders())
    if (resp.status_code == 200):
        #print(resp.content)
        #print(resp.json())
        return resp.json()
    else:
        return []

def getAllNotes():
    return auxGetAndReturnList(theUrl)

def getNote(id):
    return auxGetAndReturnList(theUrl + "/?id=%s" % (id))

def getNotesWithType(tagName):
    return auxGetAndReturnList(theUrl + "/?type=%s" % (tagName))

def getAttributesOfNote(id):
    return auxGetAndReturnList(theUrl + "/?rid=%d" % (id))

def getEntities(whichType):
    return auxGetAndReturnList(theUrl + "/?type=%s&rid=0" % (whichType))

# create a new note with a POST request
def createNote(rid, type, data):
    resp = requests.post(url=theUrl,
                         headers=auxGetHeaders(), 
                         json={"rid": rid, "lid": 0, "type": type, "data": data})
    # print(resp.status_code)
    if (resp.status_code == 200 or resp.status_code == 201 or resp.status_code == 202 or resp.status_code == 203):
        return resp.json()['id']
    else:
        return -1

# TODO
def isEntityAttributeDuplicate(rid, type, data):
    pass

def addAttributeToEntity(entityId, type, data):
    return createNote(rid=entityId, type=type, data=data)

def createEntity(jsonInfo):
    entityType = jsonInfo['__ENT__']
    rid = createNote(rid=0, type=entityType, data="__ENT__")
    for key in jsonInfo:
        if (key != '__ENT__'):
            createNote(rid=rid, type=key, data=jsonInfo[key])

def checkType(thisType, noteList):
    if len(noteList)<1:
        return False
    return noteList[0]['type'] == thisType

def searchEntity(jsonInfo):
    entityType = jsonInfo['__ENT__']
    del jsonInfo['__ENT__']
    firstKey = list(jsonInfo.keys())[0]
    firstValue = jsonInfo[firstKey]
    noteList = auxGetAndReturnList(theUrl + "/?type=%s&data=%s" % (firstKey, firstValue))
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

#
# Available operations
#         

def infoDb():
    note = getNotesWithType("__SYSTEM__")
    if len(note) == 0:
        return []
    else:  
        note = getAttributesOfNote(note[0]['id']) 
        return note

def initDb():
    if len(infoDb()) > 0:
        return False
    rid = createNote(rid=0, type="__SYSTEM__", data="__ENT__")
    if rid>0:
        createNote(rid=rid, type="CREATED", data=getCurrentDate())
        return True
    else:
        return False

def deleteNote(id):
    resp = requests.delete(url=theUrl + "/" + str(id), headers=auxGetHeaders())
    return(resp)

def resetDb():
    noteList = getAllNotes()
    for note in noteList:
        deleteNote(note['id'])

def countNotes():
    noteList = getAllNotes()
    return len(noteList)

def countEntities():
    noteList = getAttributesOfNote(0) 
    typeList = list(map(lambda x: x['type'], noteList))
    counted = {i:typeList.count(i) for i in typeList}
    return counted 

def printNotes():
    noteList = getAllNotes()
    for note in noteList:
        printNote(note)

def listEntities(whichType):
    noteList = getEntities(whichType)
    idList = list(map(lambda x: x['id'], noteList))
    return idList

def getEntity(id):
    noteList = getAttributesOfNote(id)
    return noteList

# MITICO!
def deleteEntity(id):
    noteList = getAttributesOfNote(id)
    for note in noteList:
        deleteNote(note['id'])
    deleteNote(id)

#
# users management
#

def userAddToGroup(username, groupName):
    print("Adding user %s to group %s" % (username, groupName))
    jsonText = '{"__ENT__":"__AUTHSETUSERGROUP__", "USERNAME":"%s", "GROUP":"%s"}' % (username, groupName)
    # print(jsonText)
    jsonInfo = json.loads(jsonText)
    createEntity(jsonInfo)

def auxUserAndGroupsList():
    idList = listEntities("__AUTHSETUSERGROUP__")
    userGroupNodeList = list(map(lambda x: getEntity(x), idList))
    userGroupList = list(map(lambda x: list(map(lambda y: y['data'], x)), userGroupNodeList))
    return(userGroupList)

def userList():
    print("Listing users")
    userList = list(map(lambda x: x[0], auxUserAndGroupsList()))
    print(userList)
    return None

def userGroupList():
    print("Listing active user groups")
    groupList = list(map(lambda x: x[1], auxUserAndGroupsList()))
    print(groupList)
    return None

def userRemoveFromGroup(username, groupName):
    print("Removing user %s from group %s" % (username, groupName))
    idList = listEntities("__AUTHSETUSERGROUP__")
    userGroupNodeList = list(map(lambda x: getEntity(x), idList))
    userGroupList = list(map(lambda x: list(map(lambda y: y['data'], x)), userGroupNodeList))
    for i in range(len(userGroupList)):
        if userGroupList[i][0] == username and userGroupList[i][1] == groupName:
            deleteEntity(idList[i])
            return True
    return False

#
# default authorization groups management
#

def getIdOfAuthGroupList():
    return(listEntities("AUTHGROUPLIST"))

def groupList():
    print("Listing default authorization groups (AUTHGROUPLIST):")
    ids = getIdOfAuthGroupList()
    if len(ids) == 1:
        entity = getEntity(ids[0])
        #print(entity)
        for attr in entity:
            print(attr['data'])
    else:
        print("Error: no AUTHGROUPLIST found")
    return None

def groupAdd(groupName):
    print("Adding one default group: %s" % (groupName))
    ids = getIdOfAuthGroupList()

    if len(ids) > 1:
        print("More than 1 AUTHGROUPLIST: remove the extra ones")
        return None

    if len(ids) < 1:
        print("No AUTHGROUPLIST: creating one")
        id = createNote(rid=0, type="AUTHGROUPLIST", data="__ENT__")
    else:
        id = ids[0]

    # add attribute to entity
    addAttributeToEntity(id, "GROUPNAME", groupName)
    return None
    
# MITICO! tutta la funzione
def groupRemove(groupName):
    print("Removing one default group: %s" % (groupName))
    ids = getIdOfAuthGroupList()

    if len(ids) > 1:
        print("More than 1 AUTHGROUPLIST: remove the extra ones")
        return None

    if len(ids) < 1:
        print("No AUTHGROUPLIST: nothing to remove")
        return None

    id = ids[0]
    entity = getEntity(id)
    #print(entity)
    for attr in entity:
        if attr['type'] == "GROUPNAME" and attr['data'] == groupName:
            deleteNote(attr['id'])
            return None
    print("Group %s not found" % (groupName))
    return None
#
# main
#

def main():
    global theUrl
    global theUsername
    global thePassword
    global theAuthorizationToken
    global debugLevel

    parser = argparse.ArgumentParser()

    # general db operations
    parser.add_argument('--infoDb', help='Show some info on the database', action='store_true')
    parser.add_argument('--initDb', help='Initialize the database', action='store_true')
    parser.add_argument('--resetDb', help='Reset the database. WARNING: ALL DATA WILL BE DELETED', action='store_true')

    # notes operations
    parser.add_argument('--countNotes', help='Count all the notes present in the database', action='store_true')  
    parser.add_argument('--printNotes', help='Print all the notes present in the database', action='store_true')

    # entities operations
    parser.add_argument('--countEntities', help='Count all the entities present in the database', action='store_true')
    parser.add_argument('--listEntities', help='List all the entities of given type', metavar='TYPE') 
    parser.add_argument('--createEntity', help='Create a new entity from the given JSON', 
                        metavar='{"__ENT__":"PC", "OWNER":"name1", "LOCATION":"office1"}')
    parser.add_argument('--searchEntity', help='Search an entity from the given JSON (search on 1 property only)', 
                        metavar='{"__ENT__":"PC", "OWNER":"name1"}')
    parser.add_argument('--getEntity', help='Get an entity', type=int, metavar='ID')
    parser.add_argument('--deleteEntity', help='Delete an entity', type=int, metavar='ID')

    # testing flag
    parser.add_argument('--createDemoEntries', help='Create DEMO entries', type=int, metavar='NUM')

    # user management
    parser.add_argument('--userAddToGroup', help='Add a user to a group', metavar='username groupname', nargs='*', type=str)
    parser.add_argument('--userRemoveFromGroup', help='Remove a user from a group', metavar='username groupname', nargs='*', type=str)
    parser.add_argument('--userList', help='List users', action='store_true')
    parser.add_argument('--userGroupList', help='List active groups', action='store_true')

    # groups management
    parser.add_argument('--groupAdd', help='Add a new default authorization group', metavar='GROUPNAME')
    parser.add_argument('--groupRemove', help='Remove a new default authorization group', metavar='GROUPNAME')
    parser.add_argument('--groupList', help='List default authorization groups', action='store_true') 

    # configuration for accessing the database
    parser.add_argument('--host', help='Set the host', metavar='URL of the host') 
    parser.add_argument('--username', help='username for connection', type=str, metavar='username')
    parser.add_argument('--password', help='password for connection', type=str, metavar='password') 
    parser.add_argument('--gui', help='Start GUI', action='store_true')

    # debug
    parser.add_argument('--debug', help='Set debug level', type=int, metavar='debug level (0-9)')

    args = parser.parse_args()

    # check if a username and password are provided by environment variables
    theUrl = os.environ.get("NOTEDB_URL", theUrl)
    theUsername = os.getenv("NOTEDB_USERNAME", theUsername)
    thePassword = os.getenv("NOTEDB_PASSWORD", thePassword)

    # if the flag is present, we need to set hostname, username, password
    if args.__dict__['host'] != None:        
        theUrl = args.__dict__['host']
    if args.__dict__['username'] != None:        
        theUsername = args.__dict__['username']
    if args.__dict__['password'] != None:        
        thePassword = args.__dict__['password']
    if args.__dict__['debug'] != None:
        debugLevel = args.__dict__['debug']

    # 
    # get the authorization token and store it for the following calls
    auxGetHeaders() 
    print("User %s connected on remote API host: %s" % (theUsername, theUrl))

    if args.__dict__['gui'] != None:
        guiManagement()

    for k, arg in args.__dict__.items():
        match k:

            # general db operations
            case 'infoDb':
                if arg:
                    print("Show info about the database:")
                    res = infoDb()
                    if len(res) > 0:
                        print(res)
                    else:
                        print("Database not initialized.")  
                continue
            case 'initDb':
                if arg:
                    print("Initializing the database")
                    if initDb():
                        print("Database initialized")
                    else:
                        print("Database not initialized")
                continue
            case 'resetDb':
                if arg:
                    print("Resetting the database")
                    resetDb()
                continue

            # notes operations
            case 'countNotes':
                if arg:
                    print("Counting the notes in the database: %d" % (countNotes()))
                continue
            case 'printNotes':
                if arg:
                    print("Printing the notes in the database:")
                    printNotes()
                continue

            # entities operations
            case 'countEntities':
                if arg:
                    print("Counting the entities in the database: %s" % (countEntities()))
                continue
            case 'listEntities':
                if arg != None:
                    print("List the entities in the database: %s" % (listEntities(arg)))
                continue
            case 'createEntity':
                if arg != None:
                    print("Creating entity: %s" % (arg))
                    convertedArg = json.loads(arg)
                    createEntity(convertedArg)
                continue
            case 'searchEntity':
                if arg != None:
                    print("Searching entity: %s" % (arg))
                    convertedArg = json.loads(arg)
                    res = searchEntity(convertedArg)
                    print(res)
                continue
            case 'getEntity':
                if arg != None:
                    print("Getting entity: %s" % (arg))
                    res = getEntity(arg)
                    print(res)
                continue
            case 'deleteEntity':
                if arg != None:
                    print("Deleting entity: %s" % (arg))
                    res = deleteEntity(arg)
                    print(res)
                continue

            # testing flag
            case 'createDemoEntries':
                if arg != None:
                    print("Creating %d entries" % (arg))
                    createDemoEntries(arg, 10)
                continue

            # user management
            case 'userAddToGroup':
                if arg != None:
                    userAddToGroup(arg[0], arg[1])
                continue
            case 'userRemoveFromGroup':
                if arg != None:
                    userRemoveFromGroup(arg[0], arg[1])
                continue
            case 'userList':
                if arg:
                    userList()
                continue
            case 'userGroupList':
                if arg:
                    userGroupList()
                continue

            # groups management
            case 'groupAdd':
                if arg:
                    groupAdd(arg)
                continue
            case 'groupRemove':
                if arg:
                    groupRemove(arg)
                continue
            case 'groupList':
                if arg:
                    groupList()
                continue

            # configuration for accessing the database
            case 'debug':
                # just to avoid the "Unmanaged flag" warning
                pass
            case 'host':
                # just to avoid the "Unmanaged flag" warning
                pass
            case 'username':
                # just to avoid the "Unmanaged flag" warning
                pass            
            case 'password':
                # just to avoid the "Unmanaged flag" warning
                pass
            case 'gui':
                # just to avoid the "Unmanaged flag" warning
                pass
            case _:
                print("Unmanaged flag: %s" % (k))


##
## GUI management
##

def infoWindow(title, message):
    layout = [[sg.Text(message, font='Any 20')],
              [sg.OK()]]
    window = sg.Window(title, layout, keep_on_top=True)
    event, values = window.read()
    window.close()

def aboutWindow():
    infoWindow("About", "NoteDb GUI")

def confirmWindow(str):
    layout = [[sg.Text('CONFIRM ' + str, font='Any 20')],
              [sg.Cancel(), sg.OK()]]
    window = sg.Window('Confirm?', layout, keep_on_top=True)
    event, values = window.read()
    window.close()
    if event == 'OK':   
        return True
    return False
    
def addEntityAttributesWindow(title, listOfAttributes):
    layoutBody = list(map(lambda s: [sg.Text(s), sg.InputText()], listOfAttributes))
    layout = [[sg.Text('Compile attributes', font='Any 20')]] + layoutBody + [[sg.Cancel(), sg.Stretch(), sg.Submit(),]]
    window = sg.Window('Add attributes for entity ' + title, layout, keep_on_top=True)
    # display and interact with the Window
    event, values = window.read()
    window.close()
    
def addEntityWindow():
    list = countEntities()
    entityList = []
    for e,n in list.items():
        entityList.append(e) 
    entityName = client_input.inputWindow("Entity name", "Input Entity Name", "", entityList)
    if (len(entityName)) == 0:
        return
    listOfAttributes = getListOfAttributes(entityName)
    # print(listOfAttributes)
    # listOfValues = addEntityAttributesWindow(entityName, listOfAttributes)
    # print(listOfValues)

    l1 = map(lambda s: '"' + s + '": "val"', listOfAttributes)
    str = '{"__ENT__": "' + entityName + '", ' + ', '.join([*l1]) + '}'
    issueStr = client_input.inputWindow("Build String", "", str, [])
    if debugLevel > 0:
        print(issueStr)
    if len(issueStr) > 0:
        createEntity(json.loads(issueStr))
        infoWindow("Info", "Entity created")

def updateEntityTypesList(window):
    global tableEntityListValues
    global tableEntityDetailsValues
    ent = countEntities()
    list = []
    for e,n in ent.items():
        list.append([e,n]) 
    window['-TABLE-ENTITY-TYPES-LIST-'].update(values=list)
    tableEntityListValues = []
    window['-TABLE-ENTITY-LIST-'].update(values=tableEntityListValues)
    tableEntityDetailsValues = []
    window['-TABLE-ENTITY-CONTENTS-'].update(values=tableEntityDetailsValues)
    return list

def guiManagement():
    global theUrl
    global theUsername
    global thePassword
    global theAuthorizationToken
    global debugLevel

    sg.theme('Light Blue 2')

    print(sg.get_versions())

    tableEntityTypesListValues = []
    tableEntityListValues = []
    tableEntityDetailsValues = []

    fileMenu =   [  'Unused', 
                    ['Quit']]
    adminMenu = [  'Unused', 
                    ['Reset/Initialize', 
                    'Create DEMO entries']]
    actionMenu = [  'Unused', 
                    ['Add entity']] 
    helpMenu =   [  'Unused', 
                    ['About']]

    body = [sg.Table(values=tableEntityTypesListValues, headings=["_ _ Type of Entity _ _", "Num."], max_col_width=40,
                    auto_size_columns=True,
                    # cols_justification=('left','center','right','c', 'l', 'bad'),       # Added on GitHub only as of June 2022
                    display_row_numbers=False,
                    justification='center',
                    num_rows=20,
                    alternating_row_color='light blue3',
                    key='-TABLE-ENTITY-TYPES-LIST-',
                    selected_row_colors='white on blue',
                    enable_events=True,
                    expand_x=True,
                    expand_y=True,
                    # tooltip='This is the list of the Entities',
                    vertical_scroll_only=False,
                    enable_click_events=True           # Comment out to not enable header and other clicks
                    ),
            sg.Table(values=tableEntityListValues, headings=["Entity ID"], max_col_width=40,
                    auto_size_columns=True,
                    # cols_justification=('left','center','right','c', 'l', 'bad'),       # Added on GitHub only as of June 2022
                    display_row_numbers=False,
                    justification='center',
                    num_rows=20,
                    alternating_row_color='light blue3',
                    key='-TABLE-ENTITY-LIST-',
                    selected_row_colors='white on blue',
                    enable_events=True,
                    expand_x=True,
                    expand_y=True,
                    # tooltip='This is the selected Entity'
                    vertical_scroll_only=False,
                    enable_click_events=True,           # Comment out to not enable header and other clicks
                    ),
                sg.Table(values=tableEntityDetailsValues, headings=["_ _ _ _ _ Entity Details _ _ _ _ _"], max_col_width=40,
                    auto_size_columns=True,
                    # cols_justification=('left','center','right','c', 'l', 'bad'),       # Added on GitHub only as of June 2022
                    display_row_numbers=False,
                    justification='center',
                    num_rows=20,
                    alternating_row_color='light blue3',
                    key='-TABLE-ENTITY-CONTENTS-',
                    selected_row_colors='white on blue',
                    enable_events=True,
                    expand_x=True,
                    expand_y=True,
                    # tooltip='This is the selected Entity'
                    vertical_scroll_only=False,
                    enable_click_events=True,           # Comment out to not enable header and other clicks
                    )
                ]

    layout = [  
                #[sg.Menu(menuDefinition, tearoff=False, pad=(200, 1))],
                [sg.ButtonMenu('File',  fileMenu, key='-FILEMENU-'), sg.ButtonMenu('Action',  actionMenu, key='-ACTIONMENU-'), sg.ButtonMenu('Admin',  adminMenu, key='-ADMINMENU-'), sg.ButtonMenu('Help',  helpMenu, key='-HELPMENU-')],
                [sg.HorizontalSeparator()],
                body,
                [sg.VStretch()],   # Stretch verticaly                                                               
                [sg.Button("Connect"), sg.Text(theUsername), sg.Text(theUrl), sg.Text("Database not connected", key="-STATUS-"), sg.Stretch(), sg.B('Quit')] 
            ]

    # Create the window                                                                                              
    window = sg.Window("NoteDbGUI", layout, resizable=True, finalize=True, font=("Helvetica", 16))

    # init
    window[f'-STATUS-'].update("CONNECTED")
    tableEntityTypesListValues = updateEntityTypesList(window)

    # Create an event loop                                                                                           
    while True:
        event, values = window.read()     
        if debugLevel > 0:
            print(event, "\n", values)                                                                                     
        if event == "Quit" or event == sg.WIN_CLOSED:
            break
        if event == "Connect":
            tableEntityTypesListValues = updateEntityTypesList(window)
            window[f'-STATUS-'].update("CONNECTED")
        elif event == "-TABLE-ENTITY-TYPES-LIST-":
            if len(values['-TABLE-ENTITY-TYPES-LIST-']) > 0:
                clickedRaw = values['-TABLE-ENTITY-TYPES-LIST-'][0]
                clickedEntity = tableEntityTypesListValues[clickedRaw][0] 
                tableEntityListValues = listEntities(clickedEntity)
                window['-TABLE-ENTITY-LIST-'].update(values=tableEntityListValues)
                tableEntityDetailsValues = []
                window['-TABLE-ENTITY-CONTENTS-'].update(values=tableEntityDetailsValues)
        elif event == '-TABLE-ENTITY-LIST-':
            if len(values['-TABLE-ENTITY-LIST-']) > 0:
                clickedRaw = values['-TABLE-ENTITY-LIST-'][0]
                clickedEntityId = tableEntityListValues[clickedRaw] 
                res = getEntity(clickedEntityId)
                tableEntityDetailsValues = list(map(lambda x: '"' + x['type'] + ": " + x['data'] + '"', res))
                window['-TABLE-ENTITY-CONTENTS-'].update(values=tableEntityDetailsValues)
        elif event == '-HELPMENU-':
            if values['-HELPMENU-'] == 'About':
                # sg.popup('About this program', 'Version 1.0', 'PySimpleGUI rocks...')
                aboutWindow()
        elif event == '-FILEMENU-':
            if values['-FILEMENU-'] == 'Quit':
                break
        elif event == '-ADMINMENU-':
            if values['-ADMINMENU-'] == 'Reset/Initialize':
                if confirmWindow("Reset/Initialize?"):
                    if debugLevel > 0:
                        print("Reset/Initialize")
                    resetDb()
                    initDb()
                    tableEntityTypesListValues = updateEntityTypesList(window)
                else:
                    if debugLevel > 0:
                        print("SKIP Reset/Initialize")
            elif values['-ADMINMENU-'] == 'Create DEMO entries':
                if confirmWindow("Create DEMO entries?"):
                    createDemoEntries(10,10)
                    tableEntityTypesListValues = updateEntityTypesList(window)
        elif event == '-ACTIONMENU-':
            if values['-ACTIONMENU-'] == 'Add entity':
                if debugLevel > 0:
                    print("Add entity")
                addEntityWindow()
                updateEntityTypesList(window)
    window.close()
    exit

main()
