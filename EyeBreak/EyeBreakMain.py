from PyQt5.QtWidgets import QDesktopWidget, QLabel;
from PyQt5.QtGui     import QFont;
from PyQt5.QtCore    import pyqtSignal, pyqtSlot, Qt;
from threading       import Thread, Event;
from subprocess      import Popen, STDOUT, DEVNULL;
import time, signal, sys;

if sys.platform == 'linux':
  cmd = ['paplay', '/usr/share/sounds/gnome/default/alerts/drip.ogg'];
elif sys.platform == 'darwin':
  cmd = ['afplay', '/System/Library/Sounds/funk.aiff'];
else:
  raise Exception('Not code/tested!')
#  cmd = ['afplay', 'C:\\Windows\\Media\\notify.wav'];
#  powershell -c (New-Object Media.SoundPlayer "C:\Windows\Media\notify.wav").PlaySync();

class EyeBreakLabel( QLabel ):
  showSig = pyqtSignal();                                       # Signal for showing window(s)
  hideSig = pyqtSignal();                                       # Signal for hiding window(s)
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
    );                                                              # Initialize super class
    self.setAlignment( Qt.AlignCenter );                            # Align text to middle of screen
    self.setFont( QFont('SansSerif', 48) );                         # Set font an font size
    self.setStyleSheet("background-color : black; color : gray;");  # Set background to black and text color to gray
    self.move( x, y );                                              # Move label to given screen
    
    self.showSig.connect(self.__show);                            # Connect __showSig signal to the __show method
    self.hideSig.connect(self.__hide);                            # Connect __hideSig signal to the __hide method
  ##########################################
  @pyqtSlot()
  def __show(self, *args):
    self.showFullScreen();
  ##########################################
  @pyqtSlot()
  def __hide(self, *args):
    self.hide();

class EyeBreakMain( QDesktopWidget ):
  labels = [];
  def __init__(self, text = None, debug = False):
    '''
    Keywords:
       text  : Text displayed on window.
       debug : Set for faster switching time
    '''
    QDesktopWidget.__init__(self);

    signal.signal(signal.SIGINT,  self.__exit_gracefully);          # Set method to run on interupt signal
    signal.signal(signal.SIGTERM, self.__exit_gracefully);          # Set method to run on kill signal

    self.__text    = text;
    self.__debug   = debug;
    self.__running = Event();                                       # Initialize threading event
    self.__visible = False;

    self.add_screens();
    self.thread    = Thread(target = self.__thread);
    self.thread.start();
  #####################################################
  def add_screens(self):
    '''
    Method for creating EyeBreakLabel for each screen
    '''
    for i in range( self.screenCount() ):          # Iterate over the number of screens
      x, y, height, width = self.availableGeometry(i).getRect();
      self.labels.append( EyeBreakLabel(x, y, text = self.__text ) );
  #######################################################  
  def __exit_gracefully(self, *args):
    self.__running.clear();
  #######################################################
  def __thread(self):
    self.__running.set();                                                       # Set the event on thread start
    if self.__debug:                                                            # If debug was set
      delay = [5] * 2;                                                          # Set delays to 5 seconds each
    else:                                                                       # Else
      delay = [20 * 60, 20];                                                    # Set delays to 20 minutes and 20 seconds
    i  = 0;                                                                     # Set index to 0
    t0 = time.time();                                                           # Get current time
    while self.__running.is_set():                                              # While the __running event is set
      if (time.time()-t0) >= delay[i]:                                          # If difference between current time and t0 >= delay time
        if self.__visible:                                                      # If the window is currently visible
          for label in self.labels: label.hideSig.emit();                       # Hide the window
          Popen( cmd, stdout = DEVNULL, stderr = STDOUT );                      # Play notification sound
        else:                                                                   # Else, it is hidden so
          for label in self.labels: label.showSig.emit();                       # Hide the window
        self.__visible = not self.__visible;
        t0 = time.time();                                                       # Update t0
        i  = (i + 1) % 2;                                                       # Increment i ensuring it is always either 0 or 1
      time.sleep(0.1);                                                          # Sleep for 100 ms
    for label in self.labels: label.close();
    self.close();                                                               # Close the window at the end of the thread
