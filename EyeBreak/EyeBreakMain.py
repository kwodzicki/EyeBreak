from PyQt5.QtWidgets import QApplication, QDesktopWidget, QLabel
from PyQt5.QtGui     import QFont
from PyQt5.QtCore    import pyqtSignal, pyqtSlot, Qt, QThread, QTimer
from threading       import Thread, Event
from subprocess      import Popen, STDOUT, DEVNULL
import time, signal, sys

if sys.platform == 'linux':
  cmd = ['paplay', '/usr/share/sounds/gnome/default/alerts/drip.ogg']
elif sys.platform == 'darwin':
  cmd = ['afplay', '/System/Library/Sounds/funk.aiff']
else:
  raise Exception('Not coded/tested!')
#  cmd = ['afplay', 'C:\\Windows\\Media\\notify.wav']
#  powershell -c (New-Object Media.SoundPlayer "C:\Windows\Media\notify.wav").PlaySync()


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
      'Take a Break' if text is None else text
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
class EyeBreakMain( QDesktopWidget ):
  labels = []
  def __init__(self, text = None, debug = False):
    '''
    Keywords:
       text  : Text displayed on window.
       debug : Set for faster switching time
    '''
    QDesktopWidget.__init__(self)

    signal.signal(signal.SIGINT,  self.__exit_gracefully)                      # Set method to run on interupt signal
    signal.signal(signal.SIGTERM, self.__exit_gracefully)                      # Set method to run on kill signal

    self.__text    = text
    self.__debug   = debug
    self.__running = True                                                   # Initialize threading event
    self.__visible = False
    
    if self.__debug:                                                            # If debug was set
      self.delay = [5] * 2                                                          # Set delays to 5 seconds each
    else:                                                                       # Else
      self.delay = [20 * 60, 20]                                                    # Set delays to 20 minutes and 20 seconds
    self.i  = 0                                                                     # Set index to 0
    self.t0 = time.time()                                                           # Get current time

    self.timer = QTimer()
    self.timer.timeout.connect( self.toggleScreen )
    self.timer.start(100)
  #####################################################
  def check_screens(self):
    '''
    Method for creating EyeBreakLabel for each screen
    '''
    labels  = []
    nScreen = self.screenCount()                                               # Number of screens available
    for i in range( nScreen ):                                                  # Iterate over the number of screens
      x, y, height, width = self.availableGeometry(i).getRect()                # Get geometry of the ith screen
      labels.append( EyeBreakLabel(x, y, text = self.__text ) )         # Create a new label and append to the labels attribute
    return labels
  #######################################################
  def toggleScreen(self, *args):
    if (time.time()-self.t0) >= self.delay[ self.i ]:                                  # If difference between current time and t0 >= delay time
      if self.__visible:                                                      # If the window is currently visible
        for label in self.labels: label.hideSig.emit()                       # Hide the window
        Popen( cmd, stdout = DEVNULL, stderr = STDOUT )                      # Play notification sound
      else:                                                                   # Else, it is hidden so
        self.labels = self.check_screens()
        for label in self.labels: label.showSig.emit()                       # Hide the window 
      self.__visible = not self.__visible    
      self.t0 = time.time()                                                       # Update t0
      self.i  = (self.i + 1) % 2                                                       # Increment i ensuring it is always either 0 or 1
  #######################################################  
  def __exit_gracefully(self, *args):
    self.__running = False
    self.timer.stop()
    QApplication.quit()
