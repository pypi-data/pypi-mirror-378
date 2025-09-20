import sys,os,re

from blues_lib.behavior.checker.Checker import Checker

class ElePresents(Checker):

  def _check(self)->bool:
    '''
    check if the element is present in the page
    @returns {bool}
    '''
    target_CS_WE:str = self._config.get('target_CS_WE')
    wait_time:int = self._config.get('wait_time',3)
    return bool(self._browser.waiter.ec.to_be_presence(target_CS_WE,wait_time))
