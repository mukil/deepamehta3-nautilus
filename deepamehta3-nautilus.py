import syslog
import urllib
import nautilus
import webbrowser
import subprocess as proc
import monty as dmc

# -----------------------------------------------------------------
#### a simple context menu extension for the nautilus filebrowser
### which allows you to turn your folder window into a canvas
# ---------------------------------------------------------------
# @author http://github.com/mukil (malte@deepamehta.org) 
# @last modified: 15.September 2010
#
# Requirements: nautilus, running jiri's deepamehta3-foldercanvas plugin, monty.py
#
# TODO: proper testing

DM_CLIENT_URL = 'http://localhost:8080/de.deepamehta.3-client/index.html'
START_DM_IN_CHROME = False

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
        syslog.syslog("Files: " + repr(files))
        #
        if files[0].is_directory(): # if a folder item is selected, provide a command for a folder canvas
            view_menuitem = nautilus.MenuItem('DeepMenuProvider::FolderView', 'Open with DeepaMehta', '')
            ### FIXME doesnt work when clicking on folder items yet
            view_menuitem.connect('activate', self.menu_activate_view_folder, files[0])
            return view_menuitem,
            # assoc_menuitem, 
        # else:
            #return assoc_menuitem,

    def get_background_items(self, window, file):
        # context menu provided directly on all "Folder Windows Backgrounds"
        serviceAvailable = dmc.isDeepaMehtaRunning()
        #
        if serviceAvailable:
            menuitem = nautilus.MenuItem('DeepMenuProvider::View', 'Open with DeepaMehta', '')
            menuitem.connect('activate', self.menu_activate_view, file)
            syslog.syslog("INFO: DeepaMehta Server is available, NICE.");
            return menuitem,
        else:
            menuitem = nautilus.MenuItem('DeepMenuProvider::Start', 'Start DeepaMehta Server', '')
            menuitem.connect('activate', self.menu_activate_start, file)   
            syslog.syslog("WARNING: DeepaMehta Server is not running ! Please start your DeepaMehta Server.");
            return menuitem,
    

    # ------------------------
    ### Menu Item Handlers
    # ------------------------

    def menu_activate_view(self, menu, file):
        # performs the main action of this plugin, invoked through a background right click
        filePath = urllib.unquote(file.get_location().get_path())
        fileName = filePath[filePath.find("/"):] # file.get_uri()[7:]
        folderId = dmc.getFolderTopicIdByPath(filePath)
        if folderId != '':
            syslog.syslog("dmc.viewWithDeepaMehta:folderId => " + folderId + " is already known")
            canvasId = dmc.getFolderCanvasId(folderId)
            if canvasId == '':
                canvasId = dmc.createCanvasTopic(fileName, folderId)
                relationId = dmc.createRelation('FOLDER_CANVAS', folderId, canvasId)
                syslog.syslog('dmc.createFolderCanvasRelation.resultId => '\
                  + relationId + ' is now relating' + folderId + ' to ' + canvasId)
                dmc.updateFolderCanvasTopic(canvasId)
                self.openFolderCanvas(canvasId)
            else:
                dmc.updateFolderCanvasTopic(canvasId)
                self.openFolderCanvas(canvasId)
        else:
            syslog.syslog("dmc.createCanvasTopic for folderLocation " + filePath);
            topicId = dmc.createFolderTopic(filePath) # tocheck
            canvasId = dmc.createCanvasTopic(fileName, topicId)  # tocheck
            relationId = dmc.createRelation('FOLDER_CANVAS', topicId, canvasId)  # tocheck
            syslog.syslog('dmc.createFolderCanvasRelation.resultId => '\
              + relationId + ' is now relating  ' + topicId + ' to ' + canvasId)
            dmc.updateFolderCanvasTopic(canvasId)  # tocheck
            self.openFolderCanvas(canvasId)
    

    def menu_activate_view_folder(self, menu, fileItem):
        # just another handler - passing on the call to another handler does not work
        # self.menu_activate_view(self, menu, fileItem) ### FIXME curiously this does not work
        # therefore we are pasting code here (see line 82 to 97)
        filePath = urllib.unquote(fileItem.get_location().get_path())
        fileName = filePath[filePath.find("/"):] # file.get_uri()[7:]
        folderId = dmc.getFolderTopicIdByPath(filePath)
        if folderId != '':
            syslog.syslog("dmc.viewWithDeepaMehta:folderId => " + folderId + " is already known")
            canvasId = dmc.getFolderCanvasId(folderId)
            dmc.updateFolderCanvasTopic(canvasId)
            self.openFolderCanvas(canvasId)
        else:
            syslog.syslog("dmc.createCanvasTopic for folderLocation " + filePath);
            topicId = dmc.createFolderTopic(filePath)
            canvasId = dmc.createCanvasTopic(fileName, topicId)
            relationId = dmc.createRelation('FOLDER_CANVAS', topicId, canvasId)
            syslog.syslog('dmc.createFolderCanvasRelation.resultId => '\
              + relationId + ' is now relating  ' + topicId + ' to ' + canvasId)
            dmc.updateFolderCanvasTopic(canvasId)
            self.openFolderCanvas(canvasId)
    

    def openFolderCanvas(self, mapId):
        # Open URL in new window, raising the window if possible.
        if START_DM_IN_CHROME:
            argument = '--app=' + DM_CLIENT_URL + '?topicmap=' + mapId
            proc.Popen(['google-chrome', argument]) # using chrome
        else:
            # using the system default browser through the pymodule
            webbrowser.open(DM_CLIENT_URL+'?topicmap='+ mapId, 1, True)

    def menu_activate_start(self, menu, file):
        # starts the deepamehta server from your installation directory configured in monty.py
        dmc.startDeepaMehtaServer()

    def menu_activate_file_muc(self, menu, files):
        # unused method to associate files or folders
        # TODO: load all topics of a certain type, e.g. ToDo's and serve all instances as associatable
        # to have the topictype configurable would be needed and definitely introduce a file correctly to dm with..
        # mime/type, size and other properties which the dmc relies on
        # self.getTopicsByType(urllib.urlencode('de/deepamehta/core/topictype/ToDo', 'UTF-8'));
        syslog.syslog('Item to associate with is: ' + repr(menu))
        for crtFile in files:
            filename = urllib.unquote(crtFile.get_uri()[7:])
            syslog.syslog('Associate Item/s: ' + filename + ' of Type: ' + crtFile.get_mime_type())
    

