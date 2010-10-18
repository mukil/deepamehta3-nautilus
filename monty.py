import os
import sys
import syslog
import urllib
import subprocess as proc
from restclient import GET, POST, PUT, DELETE

# -----------------------------------------------------------------------------
## a nearly unbearable attempt towards a deepamehta3 python client named: Monty
# -----------------------------------------------------------------------------
#
# @author http://github.com/mukil (malte@deepamehta.org)
# @last modified: 15.September 2010

# Requirements: running jiri's deepamehta3-server
#
# FIXME: getFolderTopicIdByPath() - leads to double creation when folder contains an empty space; 
#        there is no folder delivered as a search result by_property with this kind of argument
# FIXME: createFolderTopic() - empty spaces in filePath are not encoded correctly
# TODO: JSON Object Decoding
# TODO: Exception Handling

# usage example in python interpreter
# > import monty as dmc
# > dmc.isDeepaMehtaRunning()
# False
# > dmc.startDeepaMehtaServer()

SERVICE_URL = 'http://localhost:8080/core'
DM_INSTALLATION_DIR = '/home/malted/Desktop/diePaarDemos'

def isDeepaMehtaRunning():
    # returns either True or False
    syslog.syslog('INFO: checking if your local DeepaMehta-Server was already started..')
    # check if some topic is available
    try:
        response = GET(SERVICE_URL + '/topic/63',
          headers={'Content-Type' : 'application/json'}, 
          accept=['application/json', 'text/plain']
        )
        # syslog.syslog('monty.dmc.checkForDM: ' + repr(response))
        return True
    except BaseException:
        syslog.syslog('WARNING: Your local DeepaMehta-Server is not started yet')
        return False

def startDeepaMehtaServer():
    syslog.syslog("INFO: your local DeepaMehta server is going to be started. NOTE: you need to switch folder now once")
    proc.Popen(['gnome-terminal', '-t', 'DeepaMehta Server', '-x', '' + DM_INSTALLATION_DIR + '/deepamehta-linux.sh'])

def getFolderTopicIdByPath(folderPath):
    # queries if there is a folderTopic known to dm with a Path property
    key = 'de/deepamehta/core/property/Path'.replace("/", "%2F")
    value = folderPath.replace("/", "%2F")
    url = SERVICE_URL + '/topic/by_property/' + key + '/' + value
    syslog.syslog("monty.getFolderTopicIdByPath: " + folderPath)
    response = GET(url,
        headers={'Content-Type' : 'application/json', 'TE' : 'UTF-8'}, 
        accept=['application/json', 'text/plain']
    )
    resultId = getFieldFromResponse(response, 'id')
    if resultId == '':
        syslog.syslog(' ---: That folder is yet unknown to your DeepaMehta installation :--- ')
    return resultId

def createRelation(relation_type_uri, topicOne, topicTwo):
    # create a relation of type_uri between two topicIds
    # returns id
    message = '{"type_id":"' + relation_type_uri + '","src_topic_id":'\
      + topicOne + ',"dst_topic_id":' + topicTwo + ',"properties":{}}'
    syslog.syslog("mondy.creatingFolderCanvasRelation from folderId => "\
      + topicOne + " to canvasId =>  " + topicTwo + "")
    try:
        response = POST(SERVICE_URL + '/relation/',
          headers={'Content-Type' : 'application/json'}, 
          accept=['application/json', 'text/plain'],
          body = message
        )
        # response: {"id":541,"type_id":"RELATION","src_topic_id":98,"dst_topic_id":100,"properties":{}}
        resultId = getFieldFromResponse(response, 'id')
        syslog.syslog('monty.createdRelation.resultId => ' + resultId)
        return resultId
    except BaseException, e:
        syslog.syslog('EXCEPTION: ' + str(e))
    return ''

def createNewTopicmap(title):
    # creates a new topicmap
    # returns id
    syslog.syslog("monty.createNewTopicmap.title => \"" + title + "\"")
    postBody = '{"type_uri":"de/deepamehta/core/topictype/Topicmap",'\
      + '"properties":{"de/deepamehta/core/property/Title":"' + title + '"}}'
    try:
        response = POST(SERVICE_URL + '/topic',
            headers={'Content-Type' : 'application/json'},
            accept=['application/json', 'text/plain', 'text/html'],
            body = postBody
        )
        # syslog.syslog("monty.createNewTopicmap.response => " + repr(response))
        resultId = getFieldFromResponse(response, 'id')
        syslog.syslog('monty.createNewTopicmap.resultId => ' + repr(resultId))
        return resultId
    except BaseException, e:
        syslog.syslog('EXCEPTION: ' + str(e))
        return ''

def createFolderTopic(filePath):
    # creates a topic of type de/deepamehta/core/topictype/Folder for the given pathName 
    # NOTE: before executing this, check if one is already one there !
    nameIdx = str.rfind(filePath, "/")
    folderName = filePath[nameIdx + 1:]
    postBody = '{"type_uri":"de/deepamehta/core/topictype/Folder", '\
      + '"properties":{"de/deepamehta/core/property/Path":"' + filePath + '", '\
      + '"de/deepamehta/core/property/FolderName": "' + folderName + '"}}'
    response = POST(SERVICE_URL + '/topic', 
        headers={'Content-Type' : 'application/json'},
        accept=['application/json', 'text/plain', 'text/html'],
        body = postBody)
    try:
        resultId = getFieldFromResponse(response, 'id')
        syslog.syslog('monty.createFolderTopic.resultId => ' + resultId)
        return resultId
    except Exception, e:
        syslog.syslog("Exception while accessing the new folderTopicId: " + str(e))
    return ''
    
    def getTopicById(topicId):
        # currently unused and untested and we can not other values than numbers from json
        syslog.syslog('monty.getTopicById: ' + topicId)
        response = GET(SERVICE_URL + '/topic/' + topicId, 
            headers={'Content-Type' : 'application/json'}, 
            accept=['application/json', 'text/plain']
        )
        syslog.syslog(' ---: ' + response + ' :--- ')

def putTxtFileTopic(filePath):
    # unused dummy method which creates a new file topic in one deeapemehta instance 
    # with media type text/plain and lorem ipsum content
    syslog.syslog('monty.putTxtFileTopic: ' + filePath)
    response = POST(SERVICE_URL + '/topic',
        headers={'Content-Type' : 'application/json' },
        accept=['application/json', 'text/plain', 'text/html'],
        body = '{ "type_uri":"de/deepamehta/core/topictype/File", '\
          + '"properties": { "de/deepamehta/core/property/FileName": "Hello World", '\
          + '"de/deepamehta/core/property/Path":"' + filePath + '", '\
          + '"de/deepamehta/core/property/MediaType":"text/plain", '\
          + '"de/deepamehta/core/property/Size":0, '\
          + '"de/deepamehta/core/property/Content":"Hello World!"}}'
    )

# ----------------------
## Parser Utility
# ----------------------

def getFieldFromResponse(responseString, string):
    # this method was introduced cause of prblems wiht json decoding -- 
    # => see line 162 and forthcoming for detailed problem description
    # just works for extracting numbers(integers) from JSON and is 
    # ### TODO untested for the extractions of strings and other datatypes
    field = '';
    firstIndex = responseString.find('"' + string + '"')
    scndIndex = responseString.find('"', int(firstIndex) + 1)
    thirdIndex = responseString.find('"', int(scndIndex) + 1)
    field = responseString[int(scndIndex+2):int(thirdIndex-1)] # start, steps
    # syslog.syslog('monty.getFieldFromResponse => ' + field)
    return field

# ----------------------------
## Folder Canvas Functionality
# ----------------------------

def getFolderCanvasId(folderId):
    # dmc.getFolderCanvasId("354")
    # returns either '' or 'id'
    typeString = 'de/deepamehta/core/topictype/Topicmap'.replace("/", "%2F")
    url = SERVICE_URL + '/topic/' + folderId + '/'\
      + 'related_topics?include_topic_types='+ typeString + ''\
      + '&include_rel_types=FOLDER_CANVAS;INCOMING'
    syslog.syslog("monty.getRelatedCanvasId: " + url)
    response = GET(url,
        headers={'Content-Type' : 'application/json', 'TE' : 'UTF-8'},
        accept=['application/json', 'text/plain']
    )
    resultId = getFieldFromResponse(response, 'id')
    if resultId == '':
        syslog.syslog(' ---: That folder was not yet turned into a Folder Canvas :--- ')
    else:
        syslog.syslog("monty.getRelatedCanvasId.canvasId => " + resultId + " :--- ")
    return resultId

def createCanvasTopic(filePath, folderTopicId):
    # returns the ID of the topicmapTopic
    canvasIndex = str.rfind(filePath, "/")
    canvasName = filePath[canvasIndex + 1:]
    syslog.syslog('monty.createFolderCanvas: ' + canvasName + ' and folderId: ' + folderTopicId)
    try:
        #syslog.syslog(' ---: ' + json.dumps(prettyRe) + ' :---')
        canvasId = createNewTopicmap(canvasName)
        return canvasId
        # 
        # return relationId
    except Exception, e:
        syslog.syslog('createAndRelateCanvasTopics.Exception: ' + str(e))
    return ''

def updateFolderCanvasTopic(topicmapId):
    syslog.syslog('monty.updateFolderCanvas.canvasId => ' + topicmapId + '')
    # "deepamehta3-foldercanvas.synchronize"
    location = SERVICE_URL + '/command/deepamehta3-foldercanvas.synchronize'
    message = '{topicmap_id: ' + topicmapId + '}'
    response = POST(location,
        headers={'Content-Type' : 'application/json'},
        accept=['application/json', 'text/plain', 'text/html'],
        body = message)
    try:
        # syslog.syslog(' ---: ' + simplejson.loads(response)['id'] + ' :---')
        # resultId = self.getFieldFromResponse(response, 'id')
        syslog.syslog('monty.updateFolderCanvas.result => ' + repr(response))
        return ''
    except SyntaxException:
        syslog.syslog("SyntaxException while accessing the new result")
        syslog.syslog('updateFolderCanvasTopic is returning \'\' ')
    return ''

