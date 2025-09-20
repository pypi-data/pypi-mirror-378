import sys,os,re

from blues_lib.behavior.checker.Checker import Checker

class ToBeSelected(Checker):

  def _check(self)->bool:
    '''
    if the current url is equal to the expected url
    @returns {bool}
    '''
    kwargs = self._get_kwargs(['target_CS_WE','timeout'])
    return self._browser.waiter.ec.to_be_selected(**kwargs)
