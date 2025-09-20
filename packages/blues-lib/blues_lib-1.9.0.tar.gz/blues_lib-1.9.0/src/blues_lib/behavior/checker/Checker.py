import sys,os,re

from blues_lib.type.output.STDOut import STDOut
from blues_lib.type.executor.Behavior import Behavior

class Checker(Behavior):

  def _invoke(self)->STDOut:
    value = None
    try:
      value = self._check()
      return STDOut(200,'ok',value)
    except Exception as e:
      return STDOut(500,str(e),value)

  def _check(self)->bool:
    pass