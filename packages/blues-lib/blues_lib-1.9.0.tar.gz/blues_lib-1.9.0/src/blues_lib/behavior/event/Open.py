import sys,os,re
from typing import Any

from blues_lib.behavior.event.Event import Event

class Open(Event):

  def _trigger(self)->Any:
    url = self._config.get('url')
    try:
      self._browser.open(url)
      return True
    except Exception as e:
      return False
