from PyQt5.QtWidgets import QLabel;
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
class EyeBreakMain( QLabel ):
  __showSig = pyqtSignal();
  __hideSig = pyqtSignal();
  def __init__(self, debug = False):
    QLabel.__init__(self, 'Take a Break');
    self.setAlignment( Qt.AlignCenter );
    self.setFont( QFont('SansSerif', 48) );
    self.setStyleSheet("background-color : black; color : gray;")
    self.__debug   = debug;
    self.__running = Event();
    signal.signal(signal.SIGINT,  self.__exit_gracefully)
    signal.signal(signal.SIGTERM, self.__exit_gracefully)
    
    self.__showSig.connect(self.__show)
    self.__hideSig.connect(self.__hide)
    
    self.thread    = Thread(target = self.__thread);
    self.thread.start();

  @pyqtSlot()
  def __show(self):
  	self.showFullScreen();
  @pyqtSlot()
  def __hide(self):
  	self.hide();
  
  def __exit_gracefully(self, *args):
    self.__running.clear();
  def __thread(self):
    self.__running.set();                                 # Set the event on thread start
    if self.__debug:                                      # If debug was set
      delay = [5] * 2;                                    # Set delays to 5 seconds each
    else:                                                 # Else
      delay = [20 * 60, 20];                              # Set delays to 20 minutes and 20 seconds
    i  = 0;                                               # Set index to 0
    t0 = time.time();                                     # Get current time
    while self.__running.is_set():                        # While the __running event is set
      if (time.time()-t0) >= delay[i]:                    # If difference between current time and t0 >= delay time
        if self.isVisible():                              # If the window is currently visible
          self.__hideSig.emit();                          # Hide the window
        else:                                             # Else, it is hidden so
          self.__showSig.emit();                          # Show the window
        Popen( cmd, stdout = DEVNULL, stderr = STDOUT );  # Play notification sound
        t0 = time.time();                                 # Update t0
        i  = (i + 1) % 2;                                 # Increment i ensuring it is always either 0 or 1
      time.sleep(0.1);                                    # Sleep for 100 ms
    self.close();                                         # Close the window at the end of the thread
