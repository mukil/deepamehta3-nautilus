import os
import syslog
import nautilus
import webbrowser
import urllib
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
            view_menuitem.connect('activate', self.menu_activate_view, file) ### Fixme: signal is not triggered.. mmh
            
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
        self.getTopicsByType(urllib.urlencode('de/deepamehta/core/topictype/ToDo', 'UTF-8'));
        syslog.syslog('Command came from: ' + repr(menu))
        for crtFile in files:
            filename = urllib.unquote(crtFile.get_uri()[7:])
            syslog.syslog('Associate Item/s: ' + filename + ' of Type: ' + crtFile.get_mime_type())
        #
        # self.putFileTopic(files[0].get_uri())
        
    def menu_activate_view(self, menu, file):
        #
        filename = urllib.unquote(file.get_uri()[7:])
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
        self.openFolderCanvas('96')
        # itemsInFolder = os.listdir(file.get_location().get_path())
        # syslog.syslog('backgroundItems:: ' + itemsInFolder)
        # fileInfo = nautilus.file_info_get_type(file)
        # fileType = fileInfo.get_file_type(file)
        # syslog.syslog('backgroundItems:fileInfo: ' + fileInfo)


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


    def getTopicsByType(self, topicTypeUri):
        # response = 
        # urllib.urlopen(SERVICE_URL + '/topic/by_type/' + topicTypeUri, None, ['Content-Type', 'application/json'])
        response = GET(SERVICE_URL + '/topic/by_type/' + topicTypeUri, 
          headers={'Content-Type' : 'application/json'}, 
          accept=['application/json', 'text/plain']
        )
        syslog.syslog('monty.dmc.getTopicsByType: ' + repr(response))
    
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
        # 
        # idStart = response.find(':')
        # idEnd = response.find('"', response.find(':')+1)
        syslog.syslog(' ---: ' + response + ' :--- ')
    
    def putTopicInMap(topicId):
        # {"topic_id":81,"x":496.0975611412235,"y":107.05648882256608}
        syslog.syslog('monty.dmc.putTopicInMap()')
    
