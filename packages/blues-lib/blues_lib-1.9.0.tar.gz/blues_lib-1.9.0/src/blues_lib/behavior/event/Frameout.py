import sys,os,re
from typing import Any

from blues_lib.behavior.event.Event import Event

class Frameout(Event):

  def _trigger(self)->Any:
    return self._browser.interactor.frame.switch_to_default()