import sys,os,re
from typing import Any

from blues_lib.behavior.event.Event import Event

class Hover(Event):

  def _trigger(self)->Any:
    kwargs = self._get_kwargs(['target_CS_WE','parent_CS_WE','timeout'])
    return self._browser.action.mouse.move_in(**kwargs)