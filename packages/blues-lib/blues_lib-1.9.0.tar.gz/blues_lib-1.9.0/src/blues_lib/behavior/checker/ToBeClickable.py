import sys,os,re,time

from blues_lib.behavior.checker.Checker import Checker

class ToBeClickable(Checker):

  def _check(self)->bool:
    '''
    if the current url is equal to the expected url
    @returns {bool}
    '''
    kwargs = self._get_kwargs(['target_CS_WE','timeout'])
    stat:bool = self._browser.waiter.ec.to_be_clickable(**kwargs)

    if stat and (post_gurard_time:= self._config.get('post_guard_time',1)):
      time.sleep(post_gurard_time)
    return stat
