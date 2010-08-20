import nautilus
import syslog
import urllib
import os
from restclient import GET, POST, PUT, DELETE

#
# deepamehta context menu for the nautilus filebrowser ( based on the submenu.py example )
# written by mr.mukil (malte@deepamehta.org)
# 
# date of the art: 19.August 2010
# 

SERVICE_URL = 'http://localhost:8080/core'

class DeepMenuProvider(nautilus.MenuProvider):
        
    # Nautilus crashes if a plugin doesn't implement the __init__ method.
    # See Bug #374958
    def __init__(self):
        pass

    def get_file_items(self, window, files):
        # anway allow assocating
        top2_menuitem = nautilus.MenuItem('DeepMenuProvider::Associate', 'Associate with ..', '')
        # assoc submenu
        submenu = nautilus.Menu()
        sub_menuitem = nautilus.MenuItem('DeepMenuProvider::Tag', 'MuC2010', '')
        sub_menuitem.connect('activate', self.menu_activate_file_muc, files)
        submenu.append_item(sub_menuitem)
        top2_menuitem.set_submenu(submenu)
        #
        if files[0].is_directory(): # if a folder item is selected, provide a command for a folder canvas
            top_menuitem = nautilus.MenuItem('DeepMenuProvider::FolderView', 'View with DeepaMehta', '')
            top_menuitem.connect('activate', self.menu_activate_view, file) ### Fixme: signal is never triggered
            
            return top_menuitem, top2_menuitem,
        else:
        
            return top2_menuitem,

    def get_background_items(self, window, file):
        menuitem = nautilus.MenuItem('DeepMenuProvider::View', 'View with DeepaMehta', '')
        menuitem.connect('activate', self.menu_activate_view, file)
        
        return menuitem,

    ### Menu Item Handlers
        
    def menu_activate_file_muc(self, menu, files):
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
        # itemsInFolder = os.listdir(file.get_location().get_path())
        # syslog.syslog('backgroundItems:: ' + itemsInFolder)
        # fileInfo = nautilus.file_info_get_type(file)
        # fileType = fileInfo.get_file_type(file)
        # syslog.syslog('backgroundItems:fileInfo: ' + fileInfo)

    ###    
    ### Monty's REST Client Utility Methods
    ###
    
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
    
