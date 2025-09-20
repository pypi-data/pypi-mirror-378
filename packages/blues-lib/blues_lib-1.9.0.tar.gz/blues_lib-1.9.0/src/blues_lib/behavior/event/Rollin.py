import sys,os,re
from typing import Any

from blues_lib.behavior.event.Event import Event

class Rollin(Event):

  def _trigger(self)->Any:
    kwargs = self._get_kwargs(['target_CS_WE','amount_x','amount_y','parent_CS_WE'])
    return self._browser.action.wheel.scroll_from_element_to_offset(**kwargs)