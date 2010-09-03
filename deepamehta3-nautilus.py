import os
import syslog
import nautilus
import webbrowser
import urllib
import simplejson
import sys

#
from restclient import GET, POST, PUT, DELETE

#
# deepamehta context menu for the nautilus filebrowser ( based on the submenu.py example )
# written by mr.mukil (malte@deepamehta.org)
# 
# date of the art: 19.August 2010
# 

SERVICE_URL = 'http://localhost:8080/core'
DM_CLIENT_URL = 'http://localhost:8080/de.deepamehta.3-client/index.html'

class DeepMenuProvider(nautilus.MenuProvider):
        
    # Nautilus crashes if a plugin doesn't implement the __init__ method.
    # See Bug #374958
    def __init__(self):
        pass

    # context menu provided directly on file and folder items
    def get_file_items(self, window, files):
        # topicType = urllib.urlencode('de/deepamehta/core/topictype/Note') ### fixme:
        # topics = self.getTopicsByType(topicType)
        # anway allow assocating
        assoc_menuitem = nautilus.MenuItem('DeepMenuProvider::Associate', 'Associate with ..', '')
        # assoc submenu
        submenu = nautilus.Menu()
        sub_menuitem = nautilus.MenuItem('DeepMenuProvider::Tag', 'MuC2010', '')
        sub_menuitem.connect('activate', self.menu_activate_file_muc, files)
        submenu.append_item(sub_menuitem)
        assoc_menuitem.set_submenu(submenu)
        #
        if files[0].is_directory(): # if a folder item is selected, provide a command for a folder canvas
            view_menuitem = nautilus.MenuItem('DeepMenuProvider::FolderView', 'View with DeepaMehta', '')
            view_menuitem.connect('activate', self.menu_activate_view_folder, file) ### Fixme: signal is not triggered.. mmh
            
            return assoc_menuitem, view_menuitem, 
        else:
        
            return assoc_menuitem,

    # context menu provided directly on "GNOME Backgrounds"
    def get_background_items(self, window, file):
        serviceAvailable = self.isDeepaMehtaRunning()
        #
        if serviceAvailable:          
            menuitem = nautilus.MenuItem('DeepMenuProvider::View', 'View with DeepaMehta', '')
            menuitem.connect('activate', self.menu_activate_view, file)
        else: 
            menuitem = nautilus.MenuItem('DeepMenuProvider::Start', 'Start DeepaMehta Server', '')
            menuitem.connect('activate', self.menu_activate_start, file)   
        
        return menuitem,

    ### Menu Item Handlers
        
    def menu_activate_file_muc(self, menu, files):
        # self.getTopicsByType(urllib.urlencode('de/deepamehta/core/topictype/ToDo', 'UTF-8'));
        syslog.syslog('Command came from: ' + repr(menu))
        for crtFile in files:
            filename = urllib.unquote(crtFile.get_uri()[7:])
            syslog.syslog('Associate Item/s: ' + filename + ' of Type: ' + crtFile.get_mime_type())
        #
        # self.putFileTopic(files[0].get_uri())
        
    def menu_activate_view(self, menu, file):
        #
        filePath = urllib.unquote(file.get_uri())
        fileName = urllib.unquote(file.get_uri()[7:])
        folderId = self.askForFolderCanvas(filePath)
        if folderId != '':
            syslog.syslog("monty.viewWithDeepaMehta:folderId => " + folderId + " is already known")
            self.updateFolderCanvasTopic(fileName)
        else:
            topicId = self.createFolderTopic(file.get_uri())
            syslog.syslog("monty.creatingCanvasTopic now for title: " + fileName + " and " + topicId)
            relationId = self.createCanvasTopic(fileName, topicId)
            syslog.syslog("monty.createdFolderCanvasRelation.resultId " + repr(relationId))
            # relationId = self.createRelation('FOLDER_CANVAS', topicId, canvasId)
            # syslog.syslog(' --  to create foldercanvas from ' + topicId + 'to -- ' + canvasId + ' => ' + relationId)
        files = []
        folders = []
        listedItems = os.listdir(filename)
        for element in listedItems:
            if not element.startswith('.'): 
                if os.path.isdir(filename+'/'+element): 
                    folders.append(filename+'/'+element)
                elif os.path.isfile(filename+'/'+element):
                    files.append(filename+'/'+element)
        syslog.syslog('Handle Folder Canvas for folders: ' + repr(folders) + ' & files ' + repr(files))
        # self.openFolderCanvas('96')
        #
        # itemsInFolder = os.listdir(file.get_location().get_path())
        # syslog.syslog('backgroundItems:: ' + itemsInFolder)
        # fileInfo = nautilus.file_info_get_type(file)
        # fileType = fileInfo.get_file_type(file)
        # syslog.syslog('backgroundItems:fileInfo: ' + fileInfo)
    
    # another registration passing on the call 
    def menu_activate_view_folder(self, menu, files):
        menu_activate_view(self, menu, files)

    def menu_activate_start(self, menu, file):
        syslog.syslog("INFO: your local DeepaMehta server is going to be started..")
        # this line does not working within python-nautilus - though it works within the python interpreter
        os.system('/home/malted/source/v3/dev/instance/deepamehta-linux.sh')
    
    ### 
    ### Monty's REST Client Utility Methods
    ###
    
    def isDeepaMehtaRunning(self):
        # check if default workspace topic is available
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
        #
        syslog.syslog('is now launching the folder canvas topicmap ('+mapId+') in your default webbrowser')

    
    def askForFolderCanvas(self, folderPath):
        # http://localhost:8080/core/topic/by_property/{key}/{value}
        key = 'de/deepamehta/core/property/Path'.replace("/", "%2F")
        # key = key.replace(" ", "%20")
        #
        value = folderPath.replace("/", "%2F")
        #value = value.replace(" ", "%20")
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
        else:
            try:
                correctedString = unicode("'" + str(response) + "'", "UTF-8")
                # uncomment the following line ...
                # syslog.syslog(" ---: monty.askForFolderCanvas RESPONSE: " + correctedString + " :--- ")
                # and paste the result of the line of this from your console as it is into your python interpreter..
                # in the following way, the result is astonishing cause decoding json works that way
                # result = simplejson.loads(correctedString)
                # the result is fine in the interpreter there !?
                # resultId = result['id'] 
                # now trying to get an exception with decoding the string to a proper format
                decodedString = correctedString.decode("UTF-8")
            except Exception, e:
                syslog.syslog("DecodingException: \"" + str(e) + "\" for JSON of ---: " + correctedString)
            syslog.syslog("monty.askForFolder.folderId => " + resultId + " :--- ")
            return resultId
    
    
    
    # typeUri=de/deepamehta/core/topictype/TopicmapRelationRef
    # of type "RELATION" from topicOne->topicTwo
    # of type "RELATION" from topicmapId->resultingRelationId
    # create a relation of type_uri between two topicIds
    def createRelation(self, relation_type_uri, topicOne, topicTwo):
        message = '{"type_id":"' + relation_type_uri + '","src_topic_id":'+topicOne+',"dst_topic_id":'+topicTwo+',"properties":{}}'
        # syslog.syslog('monty.createRelation.sending ---: ' + repr(message))
        try:
            response = POST(SERVICE_URL + '/relation/',
              headers={'Content-Type' : 'application/json',  'Cookie' : 'workspace_id=62'}, 
              accept=['application/json', 'text/plain'],
              body = message
            )
            # response: {"id":541,"type_id":"RELATION","src_topic_id":98,"dst_topic_id":100,"properties":{}}
            resultId = self.getFieldFromResponse(response, 'id')
            syslog.syslog('monty.createRelation.resultId => ' + resultId)
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
                headers={'Content-Type' : 'application/json', 'Cookie' : 'workspace_id=62' },
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
            headers={'Content-Type' : 'application/json', 'Cookie' : 'workspace_id=62' }, 
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
    
    def createCanvasTopic(self, filePath, folderTopicId):
        canvasIndex = str.rfind(filePath, "/")
        canvasName = filePath[canvasIndex + 1:]
        syslog.syslog('monty.createFolderCanvas: ' + canvasName + ' and folderId: ' + folderTopicId)
        try:
            #syslog.syslog(' ---: ' + json.dumps(prettyRe) + ' :---')
            canvasId = self.createNewTopicmap(canvasName)
            syslog.syslog("mondy.createFolderCanvasRelation from canvasId =>  " + canvasId + " to folderId => " + folderTopicId)
            relationId = self.createRelation('FOLDER_CANVAS', folderTopicId, canvasId)
            syslog.syslog('monty.createFolderCanvasRelation.resultId => ' + relationId + ' is now relating  ' + folderTopicId + ' to ' + canvasId)
            return relationId
        except Exception, e:
            syslog.syslog('createAndRelateCanvasTopics.Exception: ' + e)
        return ''
    
    def updateFolderCanvasTopic(self, filePath):
        syslog.syslog('monty.dmc.updateFolderCanvas: ' + filePath + ' (not yet implemented)')
    
    def putTopicInMap(topicId):
        # {"topic_id":81,"x":496.0975611412235,"y":107.05648882256608}
        # not yet TODO: put in topicmap
        # put: core/topicmap/id 
        # body: {"relation_id":541}
        # response: {"ref_id":177}
        syslog.syslog('monty.dmc.putTopicInMap()')
        
    
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
        
    def putFileTopic(self, filePath):
        syslog.syslog('monty.dmc.putFileTopic: ' + filePath)
        response = POST(SERVICE_URL + '/topic',
            headers={'Content-Type' : 'application/json', 'Cookie' : 'workspace_id=62' },
            accept=['application/json', 'text/plain', 'text/html'],
            body = '{ "type_uri":"de/deepamehta/core/topictype/File", "properties": { "de/deepamehta/core/property/FileName": "file:///home/malted/.nautilus/python-extensions/submenu.py", "de/deepamehta/core/property/Path":"", "de/deepamehta/core/property/MediaType":"text/plain", "de/deepamehta/core/property/Size":0, "de/deepamehta/core/property/Content":"Hello World!"}}'
        )



    ###
    ### --- Monty Parser Utility 
    ###

    # introduced cause of prblems wiht json decoding -- see line 162 and forthcoming for problemd description
    # just tested with extracting numbers from JSON not working with string fields yet
    def getFieldFromResponse(self, responseString, string):
        field = '';
        firstIndex = responseString.find('"' + string + '"')
        #syslog.syslog('monty.getFieldFromResponse => ' + string +' firstIndex is: ' + repr(int(firstIndex)))
        scndIndex = responseString.find('"', int(firstIndex) + 1)
        #syslog.syslog('monty.getFieldFromResponse => ' + string +' scndIndex is: ' + repr(int(scndIndex)))
        thirdIndex = responseString.find('"', int(scndIndex) + 1)
        #syslog.syslog('monty.getFieldFromResponse => ' + string +' thirdIndex is: ' + repr(int(thirdIndex-2)))
         # syslog.syslog('monty.getFieldFromResponse => ' + string +' from: ' + repr(int(scndIndex+2)) + ' to ' +  repr(thirdIndex-1))
        field = responseString[int(scndIndex+2):int(thirdIndex-1)] # start, steps
        # syslog.syslog('monty.getFieldFromResponse => ' + field)
        return field
    
