import sys,os,re,time

from blues_lib.behavior.event.Event import Event
from blues_lib.util.AutoGUI import AutoGUI

class Keyboard(Event):

  def _trigger(self)->bool:
    key:str = self._config.get('key','')
    if not key:
      return False

    AutoGUI.press(key)
    return True

