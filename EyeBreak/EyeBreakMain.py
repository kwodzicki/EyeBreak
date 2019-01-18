from PyQt5.QtWidgets import QLabel;
from PyQt5.QtCore import pyqtSignal, pyqtSlot;
from threading import Thread
import time;

class EyeBreakMain( QLabel )
  def __init__(self):
    QLabel.__init__(self);
    self.__showSig = pyqtSignal();
    self.__hideSig = pyqtSignal();

    self.__showSig.connect(self.__show)
    self.__hideSig.connect(self.__hide)

    self.thread = Thread(target = self.__thread);
    self.thread.start();
  @pyqtSlot();
  def __show(self):
  	self.show();
  @pyqtSlot();
  def __hide(self):
  	self.hide();

  def __thread(self):
  	while True:
  	  time.sleep( 20 * 60 );
      self.__showSig.emit();
      time.sleep( 20 );
      self.__hideSig.emit();