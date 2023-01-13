import os, json, time, signal, sys

from threading       import Lock
from subprocess      import check_call, Popen, STDOUT, DEVNULL

from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QLabel, QAction
from PyQt5.QtGui     import QIcon, QFont
from PyQt5.QtCore    import pyqtSignal, pyqtSlot, Qt, QThread, QTimer

#from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QLabel
#from PySide6.QtGui     import QIcon, QFont, QAction
#from PySide6.QtCore    import Qt, QThread, QTimer
#from PySide6.QtCore import Signal as pyqtSignal
#from PySide6.QtCore import Slot as pyqtSlot


if sys.platform == 'linux':
  cmd = ['paplay', '/usr/share/sounds/gnome/default/alerts/drip.ogg']
elif sys.platform == 'darwin':
  cmd = ['afplay', '/System/Library/Sounds/funk.aiff']
else:
  pass
  #raise Exception('Not coded/tested!')
#  cmd = ['afplay', 'C:\\Windows\\Media\\notify.wav']
#  powershell -c (New-Object Media.SoundPlayer "C:\Windows\Media\notify.wav").PlaySync()

def getDisplayName( display ):
  """
   Arguments:
    display : This is a display object returned from call to QApplication.screens()

  """

  return f"{display.model()} ({display.name()})"

def getAttachedDisplays( ):
  """
  Yeild displays and formatted names of currently attached displays 
  """

  for display in QApplication.screens():
    yield getDisplayName( display ), display

class EyeBreakLabel( QLabel ):

  showSig = pyqtSignal()                                       # Signal for showing window(s)
  hideSig = pyqtSignal()                                       # Signal for hiding window(s)
  def __init__(self, x, y, text = None):
    '''
    Inputs:
       x  : x coordinate of label location
       y  : y coordinate of label location
    Keywords:
       text  : Text displayed on window.
       debug : Set for faster switching time
    '''
    QLabel.__init__(self, 
      'Take a Break<br/><br/>And<br/><br/>Drink Water' if text is None else text
    )                                                                          # Initialize super class
    self.setAlignment( Qt.AlignCenter )                                        # Align text to middle of screen
    self.setFont( QFont('SansSerif', 48) )                                     # Set font an font size
    self.setStyleSheet("background-color : black; color : gray;")              # Set background to black and text color to gray
    self.setWindowFlags( Qt.FramelessWindowHint )
    self.setWindowFlags( Qt.WindowStaysOnTopHint )
    self.move( x, y )                                                          # Move label to given screen
    
    self.showSig.connect(self.__show)                                          # Connect __showSig signal to the __show method
    self.hideSig.connect(self.__hide)                                          # Connect __hideSig signal to the __hide method
  ##########################################
  @pyqtSlot()
  def __show(self, *args):
    self.showMaximized()
  ##########################################
  @pyqtSlot()
  def __hide(self, *args):
#    self.showNormal()
    self.close()

#################################################################
class EyeBreakTray( QSystemTrayIcon ):
  SETTINGS = os.path.join( os.path.expanduser('~'), '.eyebreak' )
  LOCK     = Lock()
  labels   = []
  def __init__(self, app, text = None, debug = False):
    '''
    Keywords:
       text  : Text displayed on window.
       debug : Set for faster switching time
    '''

    super().__init__()
    try:
      icon = sys._MEIPASS
    except:
      icon = os.path.dirname( os.path.realpath(__file__) )
    #icon = os.path.join( icon, 'trayicon.jpg' )

    icon = os.path.join( icon, 'trayicon.png' )
    self.setIcon( QIcon(icon) )
    self.setVisible(True)

    signal.signal(signal.SIGINT,  self.__exit_gracefully)                      # Set method to run on interupt signal
    signal.signal(signal.SIGTERM, self.__exit_gracefully)                      # Set method to run on kill signal

    self.__text    = text
    self.__debug   = debug
    self.__running = True                                                     # Initialize threading event
    self.__visible = False
    self.__displaySettings = {}                                               # Store settings for all previously/currently attached screens
    self.__attachedDisplays = {}                                               # Dictionary to hold information about currently attached
    
    if self.__debug:                                                          # If debug was set
      self.delay = [5] * 2                                                          # Set delays to 5 seconds each
    else:                                                                       # Else
      self.delay = [20 * 60, 20]                                                    # Set delays to 20 minutes and 20 seconds
    self.i  = 0                                                                     # Set index to 0
    self.t0 = time.monotonic()                                                           # Get current time

    self.menu     = QMenu()

    # Add QAction to display remaining time
    self.remain   = QAction('')
    self.remain.setEnabled( False )
    self.menu.addAction( self.remain )

    # Display menu
    self.menu.addSeparator()
    self.dMenu = self.menu.addMenu( 'Displays' )
    self.__displaySettings = self._loadSettings()
    for displayName, _ in getAttachedDisplays( ):
      self._addDisplay( 
        {displayName : self.__displaySettings.get( displayName, True )}
       )

    # Quit option
    self.menu.addSeparator()
    self._quit = QAction( 'Quit' )
    self._quit.triggered.connect( app.quit)
    self.menu.addAction( self._quit )

    # Set context menu for the sytem tray application
    self.setContextMenu(self.menu)

    self.timer = QTimer()
    self.timer.timeout.connect( self.toggleDisplay )
    self.timer.start(1000)

    self.show()

  def _addDisplay( self, displays ):
    """
    Add a display to the Display submenu

    This will define a QAction for enabling/disabling a given display
    and add it to the Displays submenu of the system tray.

    Arguments:
      displays : This is can be either the name of the display (as generated 
        by the getDisplayName function) or a display  object returned from call 
        to QApplication.screens()

    Returns:
      None.

    """

    for display, state in displays.items():
      if display in self.__attachedDisplays: continue

      action = QAction( display, checkable = True )                            # Create a new, checkable, action with name of display 
      action.triggered.connect( self._saveSettings )                          # Set method to run when state of the checkbox changes
      self.dMenu.addAction( action )                                          # Add the action to the displays submenu
      self.__attachedDisplays[display] = action                                 # Add QAction handle to the displays dictionary
      self.__attachedDisplays[display].setChecked( state )                      # Then set checked state

  def _removeDisplay( self, display ):
    """
    Remove a display from the displays submenu

    Arguments:
      display : This is a display object returned from call to QApplication.screens()

    """

    action = self.__attachedDisplays.pop( display , None )
    if action is not None:
      self.dMenu.removeAction( action )

  def _loadSettings( self ):
    """Load settings from the settings json file and return dict"""

    if os.path.isfile( self.SETTINGS ):
      with self.LOCK:
        with open(self.SETTINGS, 'r') as fid:
          return json.load( fid )
    return {}

  def _saveSettings( self, *args, **kwargs ):
    """Save settings to the settings json file"""
    with self.LOCK:
      for displayName, action in self.__attachedDisplays.items():              # Iterate over currently available displays/settings
        self.__displaySettings[displayName] = action.isChecked()               # Update/add settings for given display
  
      with open( self.SETTINGS, 'w') as fid:                                  # Open settings file for writing
        json.dump( self.__displaySettings, fid )                              # Write information
  
      if sys.platform == 'win32':
        check_call( ['attrib', '+H', self.SETTINGS] )

  #####################################################
  def check_displays(self):
    """Method for creating EyeBreakLabel for each display"""
 
    labels  = []
    current = {}

    for sName, sObj in getAttachedDisplays():
      current[sName] = sObj
      if sName not in self.__attachedDisplays: 
        self._addDisplay( {sName : True}  )
      if self.__attachedDisplays[sName].isChecked():
        x, y, height, width = sObj.availableGeometry().getRect()              # Get geometry of the ith screen
        labels.append( EyeBreakLabel(x, y, text = self.__text ) )             # Create a new label and append to the labels attribute

    for sName in list( self.__attachedDisplays.keys() ):
      if sName not in current:
        self._removeDisplay( sName )

    return labels

  def updateTime( self ):
    """Update time label in the system tray menu"""

    remain = self.delay[ self.i ] - (time.monotonic()-self.t0)                       # Get remaining time for given delay
    minute = remain // 60                                                       # Determine minutes
    second = remain % 60
    prefix = 'Break in - ' if self.i == 0 else 'Resume in - '                   # Prefixed based on value of i
    self.remain.setText( prefix + f"{minute:02.0f}:{second:02.0f}" )            # Update the text

#######################################################
  def toggleDisplay(self, *args):
    """Run to toggle banners on display for break"""

    if (time.monotonic()-self.t0) >= self.delay[ self.i ]:                                  # If difference between current time and t0 >= delay time
      if self.__visible:                                                      # If the window is currently visible
        for label in self.labels: label.hideSig.emit()                       # Hide the window
        Popen( cmd, stdout = DEVNULL, stderr = STDOUT )                      # Play notification sound
      else:                                                                   # Else, it is hidden so
        self.labels = self.check_displays()
        for label in self.labels: label.showSig.emit()                       # Hide the window 
      self.__visible = not self.__visible    
      self.t0 = time.monotonic()                                                       # Update t0
      self.i  = (self.i + 1) % 2                                                       # Increment i ensuring it is always either 0 or 1
    self.updateTime()

  #######################################################  
  def __exit_gracefully(self, *args):
    self.__running = False
    self.timer.stop()
    QApplication.quit()

if __name__ == "__main__":
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    inst = EyeBreakTray(app, debug = len(sys.argv) > 1 )
    res = app.exec_()
    exit( res )

