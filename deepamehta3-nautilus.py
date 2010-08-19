import nautilus
import syslog
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
        # tag = self.getTopicById('65')

        top_menuitem = nautilus.MenuItem('DeepMenuProvider::Associate', 'Associate with ...', '')
        # dmsubmenu
        submenu = nautilus.Menu()
        sub_menuitem = nautilus.MenuItem('DeepMenuProvider::Tag', 'MuC2010', '')
        sub_menuitem.connect('activate', self.menu_activate_file_muc, files);
        #
        submenu.append_item(sub_menuitem)
        top_menuitem.set_submenu(submenu)
        
        return top_menuitem,

    def get_background_items(self, window, file):
        menuitem = nautilus.MenuItem('DeepMenuProvider::View', 'View with DeepaMehta', '')

        menuitem.connect('activate', self.menu_activate_view, file);
        
        return menuitem,

    ### Monty's REST Client Utility Methods

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
    
    
    
    ### Menu Item Handlers
        
    def menu_activate_file_muc(self, menu, files):
        syslog.syslog('Associate ' + files[0].get_uri() + ' with topic Muc2010')
        self.putFileTopic(files[0].get_uri())
        
    def menu_activate_view(self, menu, file):
        syslog.syslog('Folder Canvas: ' + file.get_uri())
        
