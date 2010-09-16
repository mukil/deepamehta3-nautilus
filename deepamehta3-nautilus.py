import os
import syslog
import nautilus
import webbrowser
import urllib
import simplejson
import sys
import subprocess as proc
from restclient import GET, POST, PUT, DELETE

# -----------------------------------------------------------------
### a simple context menu extension for the nautilus filebrowser
### which allows you to turn your folder window into a canvas
# ---------------------------------------------------------------
# Requirements: running jiri's deepamehta3-foldercanvas plugin
# 
# @author mr.mukil (malte@deepamehta.org) 
# @date of the art: 15.September 2010
#

SERVICE_URL = 'http://localhost:7557/core'
DM_CLIENT_URL = 'http://localhost:7557/de.deepamehta.3-client/index.html'

# 
# FIXME: fix double creation issue when folder contains an empty space
#

class DeepMenuProvider(nautilus.MenuProvider):

    def __init__(self):
        pass

    # context menu provided directly on file and folder items
    def get_file_items(self, window, files):
        # topicType = urllib.urlencode('de/deepamehta/core/topictype/Note') ### fixme:
        # topics = self.getTopicsByType(topicType)
        # anway allow assocating
        # assoc_menuitem = nautilus.MenuItem('DeepMenuProvider::Associate', 'Associate with ..', '')
        # assoc submenu
        # submenu = nautilus.Menu()
        # sub_menuitem = nautilus.MenuItem('DeepMenuProvider::Tag', 'MuC2010', '')
        # sub_menuitem.connect('activate', self.menu_activate_file_muc, files)
        # submenu.append_item(sub_menuitem)
        # assoc_menuitem.set_submenu(submenu)
        #
        if files[0].is_directory(): # if a folder item is selected, provide a command for a folder canvas
            view_menuitem = nautilus.MenuItem('DeepMenuProvider::FolderView', 'Open with DeepaMehta', '')
            ### FIXME doesnt work when clicking on folder items yet
            view_menuitem.connect('activate', self.menu_activate_view_folder, files[0])
            return view_menuitem,
            # assoc_menuitem, 
        # else:
            #return assoc_menuitem,

    # context menu provided directly on all "Folder Windows Backgrounds"
    def get_background_items(self, window, file):
        serviceAvailable = self.isDeepaMehtaRunning()
        #
        if serviceAvailable:          
            menuitem = nautilus.MenuItem('DeepMenuProvider::View', 'Open with DeepaMehta', '')
            menuitem.connect('activate', self.menu_activate_view, file)
            return menuitem,
        else: 
            # menuitem = nautilus.MenuItem('DeepMenuProvider::Start', 'Start DeepaMehta Server', '')
            # menuitem.connect('activate', self.menu_activate_start, file)   
            syslog.syslog("WARNING: DeepaMehta Server is not running ! Please start your DeepaMehta Server.");

    # ------------------------
    ### Menu Item Handlers
    # ------------------------
    
    # unused method to associate files or folders
    def menu_activate_file_muc(self, menu, files):
        # self.getTopicsByType(urllib.urlencode('de/deepamehta/core/topictype/ToDo', 'UTF-8'));
        syslog.syslog('Command came from: ' + repr(menu))
        for crtFile in files:
            filename = urllib.unquote(crtFile.get_uri()[7:])
            syslog.syslog('Associate Item/s: ' + filename + ' of Type: ' + crtFile.get_mime_type())

    # performs the main action of this plugin, invoked through a background right click
    def menu_activate_view(self, menu, file):
        #
        filePath = urllib.unquote(file.get_location().get_path())
        fileName = filePath[filePath.find("/"):] # file.get_uri()[7:]
        folderId = self.askForFolderCanvas(filePath)
        if folderId != '':
            syslog.syslog("monty.viewWithDeepaMehta:folderId => " + folderId + " is already known")
            canvasId = self.getFolderCanvasId(folderId)
            if canvasId == '':
                canvasId = self.createCanvasTopic(fileName, folderId)
                relationId = self.createRelation('FOLDER_CANVAS', folderId, canvasId)
                syslog.syslog('monty.createFolderCanvasRelation.resultId => ' + relationId + ' is now relating  ' + folderId + ' to ' + canvasId)
                self.updateFolderCanvasTopic(canvasId)
                self.openFolderCanvas(canvasId)
            else: 
                self.updateFolderCanvasTopic(canvasId)
                self.openFolderCanvas(canvasId)
        else:
            syslog.syslog("monty.createCanvasTopic for folderLocation " + filePath);
            topicId = self.createFolderTopic(filePath) ### FIXME: getFilePath not URI
            canvasId = self.createCanvasTopic(fileName, topicId)
            relationId = self.createRelation('FOLDER_CANVAS', topicId, canvasId)
            syslog.syslog('monty.createFolderCanvasRelation.resultId => ' + relationId + ' is now relating  ' + topicId + ' to ' + canvasId)
            self.updateFolderCanvasTopic(canvasId)
            self.openFolderCanvas(canvasId)

    # just another handlerand passing on the call to another handler does not work
    def menu_activate_view_folder(self, menu, fileItem):
        syslog.syslog("Trying HARD !! with => " + fileItem.get_location().get_path())
        # self.menu_activate_view(self, menu, fileItem) ### curiously this does not work
        # pasting code here from line 82 to 97
        filePath = urllib.unquote(fileItem.get_location().get_path())
        fileName = filePath[filePath.find("/"):] # file.get_uri()[7:]
        folderId = self.askForFolderCanvas(filePath)
        if folderId != '':
            syslog.syslog("monty.viewWithDeepaMehta:folderId => " + folderId + " is already known")
            canvasId = self.getFolderCanvasId(folderId)
            self.updateFolderCanvasTopic(canvasId)
            self.openFolderCanvas(canvasId)
        else:
            syslog.syslog("monty.createCanvasTopic for folderLocation " + filePath);
            topicId = self.createFolderTopic(filePath) ### FIXME: getFilePath not URI
            canvasId = self.createCanvasTopic(fileName, topicId)
            relationId = self.createRelation('FOLDER_CANVAS', topicId, canvasId)
            syslog.syslog('monty.createFolderCanvasRelation.resultId => ' + relationId + ' is now relating  ' + topicId + ' to ' + canvasId)
            self.updateFolderCanvasTopic(canvasId)
            self.openFolderCanvas(canvasId)

    # unused method starts the deepamehta server from an FIXME: hardcoded pathName# 
    def menu_activate_start(self, menu, file):
        syslog.syslog("INFO: your local DeepaMehta server is going to be started..")
        # this line does not working within python-nautilus - though it works within the python interpreter
        proc.call('gnome-terminal /home/malted/source/v3/dev/instance/deepamehta-linux.sh')

    # -------------------------------------
    ### Monty's REST Client Utility Methods
    # -------------------------------------
    
    def isDeepaMehtaRunning(self):
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

    
    def openFolderCanvas(self, mapId):
        # Open URL in new window, raising the window if possible.
        webbrowser.open(DM_CLIENT_URL+'?topicmap='+ mapId, 1, True)
        # using chrome in app mode is exactly what freaky javascript coders need'
        # proc.call(["google-chrome", "--app=http://localhost:7557/de.deepamehta.3-client/index.html?topicmap=" + mapId])

    # queries if there is a folderTopic known to dm with a Path property
    def askForFolderCanvas(self, folderPath):
        key = 'de/deepamehta/core/property/Path'.replace("/", "%2F")
        value = folderPath.replace("/", "%2F")
        url = SERVICE_URL + '/topic/by_property/' + key + '/' + value
        syslog.syslog("monty.askForFolderCanvas: " + folderPath)
        response = GET(url,
            headers={'Content-Type' : 'application/json', 'TE' : 'UTF-8'}, 
            accept=['application/json', 'text/plain']
        )
        resultId = self.getFieldFromResponse(response, 'id')
        if resultId == '':
            syslog.syslog(' ---: That folder is yet unknown to your DeepaMehta installation :--- ')
        return resultId

    def getFolderCanvasId(self, folderId):
        typeString = 'de/deepamehta/core/topictype/Topicmap'.replace("/", "%2F")
        url = SERVICE_URL + '/topic/' + folderId + '/related_topics?include_topic_types='+ typeString + '&include_rel_types=FOLDER_CANVAS;INCOMING'
        syslog.syslog("monty.getRelatedCanvasId: " + url)
        response = GET(url,
            headers={'Content-Type' : 'application/json', 'TE' : 'UTF-8'}, 
            accept=['application/json', 'text/plain']
        )
        resultId = self.getFieldFromResponse(response, 'id')
        if resultId == '':
            syslog.syslog(' ---: That folder was not yet turned into a Folder Canvas :--- ')
        else:
            syslog.syslog("monty.getRelatedCanvasId.canvasId => " + resultId + " :--- ")
        return resultId

    # create a relation of type_uri between two topicIds
    def createRelation(self, relation_type_uri, topicOne, topicTwo):
        message = '{"type_id":"' + relation_type_uri + '","src_topic_id":' + topicOne + ',"dst_topic_id":' + topicTwo + ',"properties":{}}'
        syslog.syslog("mondy.creatingFolderCanvasRelation from folderId => " + topicOne + " to canvasId =>  " + topicTwo + "")
        # syslog.syslog('monty.createRelation.sending ---: ' + repr(message))
        try:
            response = POST(SERVICE_URL + '/relation/',
              headers={'Content-Type' : 'application/json'}, 
              accept=['application/json', 'text/plain'],
              body = message
            )
            # response: {"id":541,"type_id":"RELATION","src_topic_id":98,"dst_topic_id":100,"properties":{}}
            resultId = self.getFieldFromResponse(response, 'id')
            syslog.syslog('monty.createdRelation.resultId => ' + resultId)
            return resultId
        except BaseException, e:
            syslog.syslog('EXCEPTION: ' + e)
        return ''

    # create a new topicmap
    def createNewTopicmap(self, title):
        # to /topic = 
        syslog.syslog("monty.createNewTopicmap.title => \"" + title + "\"")
        postBody = '{"type_uri":"de/deepamehta/core/topictype/Topicmap","properties":{"de/deepamehta/core/property/Title":"' + title + '"}}'
        try:
            response = POST(SERVICE_URL + '/topic',
                headers={'Content-Type' : 'application/json'},
                accept=['application/json', 'text/plain', 'text/html'],
                body = postBody
            )
            # syslog.syslog("monty.createNewTopicmap.response => " + repr(response))
            resultId = self.getFieldFromResponse(response, 'id')
            syslog.syslog('monty.createNewTopicmap.resultId => ' + repr(resultId))
            return resultId
        except BaseException, e:
            syslog.syslog('EXCEPTION: ' + e)
        return ''

    #
    # creates a topic of type de/deepamehta/core/topictype/Folder for the given pathName 
    # NOTE: before executing this, check if one is already one there !
    #
    # FIXME: empty spaces in filePath are not encoded correctly
    def createFolderTopic(self, filePath):
        # syslog.syslog('monty.createFolderTopic: ' + filePath)
        postBody = '{"type_uri":"de/deepamehta/core/topictype/Folder", "properties":{"de/deepamehta/core/property/Path":"' + filePath + '", "de/deepamehta/core/property/FolderName": "' + filePath[7:] + '"}}'
        response = POST(SERVICE_URL + '/topic', 
            headers={'Content-Type' : 'application/json'},
            accept=['application/json', 'text/plain', 'text/html'],
            body = postBody)
        try:
            # syslog.syslog(' ---: ' + simplejson.loads(response)['id'] + ' :---')
            resultId = self.getFieldFromResponse(response, 'id')
            syslog.syslog('monty.createFolderTopic.resultId => ' + resultId)
            return resultId
        except SyntaxException:
            syslog.syslog("SyntaxException while accessing the new folderTopicId")
        return ''

    # returns the relationId of the connection from folderTopic => topicmapTopic
    def createCanvasTopic(self, filePath, folderTopicId):
        canvasIndex = str.rfind(filePath, "/")
        canvasName = filePath[canvasIndex + 1:]
        syslog.syslog('monty.createFolderCanvas: ' + canvasName + ' and folderId: ' + folderTopicId)
        try:
            #syslog.syslog(' ---: ' + json.dumps(prettyRe) + ' :---')
            canvasId = self.createNewTopicmap(canvasName)
            return canvasId
            # 
            # return relationId
        except Exception, e:
            syslog.syslog('createAndRelateCanvasTopics.Exception: ' + e)
        return ''

    def updateFolderCanvasTopic(self, topicmapId):
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
        syslog.syslog('updateFolderCanvasTopic is returning nothing ')
        return ''
        

    # currently unused
    def getTopicsByType(self, topicTypeUri):
        # response = 
        # urllib.urlopen(SERVICE_URL + '/topic/by_type/' + topicTypeUri, None, ['Content-Type', 'application/json'])
        response = GET(SERVICE_URL + '/topic/by_type/' + urllib.urlencode(topicTypeUri), 
            headers={'Content-Type' : 'application/json'}, 
            accept=['application/json', 'text/plain']
        )
        syslog.syslog(' ---: ' + response + ' :--- ')

    # currently unused
    def getTopicById(self, topicId):
        syslog.syslog('monty.dmc.getTopicById: ' + topicId)
        response = GET(SERVICE_URL + '/topic/' + topicId, 
            headers={'Content-Type' : 'application/json'}, 
            accept=['application/json', 'text/plain']
        )
        syslog.syslog(' ---: ' + response + ' :--- ')

    # unused method, creates a new topic of type File
    def putFileTopic(self, filePath):
        syslog.syslog('monty.dmc.putFileTopic: ' + filePath)
        response = POST(SERVICE_URL + '/topic',
            headers={'Content-Type' : 'application/json' },
            accept=['application/json', 'text/plain', 'text/html'],
            body = '{ "type_uri":"de/deepamehta/core/topictype/File", "properties": { "de/deepamehta/core/property/FileName": "Hello World", "de/deepamehta/core/property/Path":"' + filePath + '", "de/deepamehta/core/property/MediaType":"text/plain", "de/deepamehta/core/property/Size":0, "de/deepamehta/core/property/Content":"Hello World!"}}'
        )

    # ----------------------
    ### Monty Parser Utility
    # ----------------------
    
    # this method was introduced cause of prblems wiht json decoding -- 
    # => see line 162 and forthcoming for detailed problem description
    # just tested with extracting numbers from JSON not working with string fields yet
    def getFieldFromResponse(self, responseString, string):
        field = '';
        firstIndex = responseString.find('"' + string + '"')
        # syslog.syslog('monty.getFieldFromResponse => ' + string +' firstIndex is: ' + repr(int(firstIndex)))
        scndIndex = responseString.find('"', int(firstIndex) + 1)
        # syslog.syslog('monty.getFieldFromResponse => ' + string +' scndIndex is: ' + repr(int(scndIndex)))
        thirdIndex = responseString.find('"', int(scndIndex) + 1)
        # syslog.syslog('monty.getFieldFromResponse => ' + string +' thirdIndex is: ' + repr(int(thirdIndex-2)))
        # syslog.syslog('monty.getFieldFromResponse => ' + string +' from: ' + repr(int(scndIndex+2)) + ' to ' +  repr(thirdIndex-1))
        field = responseString[int(scndIndex+2):int(thirdIndex-1)] # start, steps
        # syslog.syslog('monty.getFieldFromResponse => ' + field)
        return field

