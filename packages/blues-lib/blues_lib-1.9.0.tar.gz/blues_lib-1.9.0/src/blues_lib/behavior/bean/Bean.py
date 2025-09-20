import sys,os,re
from typing import Any

from blues_lib.type.output.STDOut import STDOut
from blues_lib.type.executor.Behavior import Behavior

class Bean(Behavior):

  def _invoke(self)->STDOut:
    value = None
    try:
      if self._action()=='setter':
        value = self._set()
      else:
        value = self._get()
      return STDOut(200,'ok',value)
    except Exception as e:
      return STDOut(500,str(e),value)

  def _get(self)->Any:
    pass

  def _set(self)->Any:
    pass

  def _action(self)->str:
    action = 'getter'
    if 'value' in self._config:
      action = 'setter'
    return action