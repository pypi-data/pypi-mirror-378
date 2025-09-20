import sys,os,re
from typing import Any

from blues_lib.util.BluesDateTime import BluesDateTime
from blues_lib.behavior.general.General import General

class Wait(General):

  def _do(self)->Any:
    kwargs = self._get_kwargs(['duration','title'])
    return BluesDateTime.count_down(kwargs)