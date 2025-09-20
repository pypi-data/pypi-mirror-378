import sys,os,re

from blues_lib.behavior.checker.Checker import Checker

class UrlMatches(Checker):

  def _check(self)->bool:
    '''
    if the url changes in the wait time, it will ignore the query params and fragments
    @returns {bool}
    '''
    url_pattern = self._config.get('url_pattern')
    wait_time = self._config.get('wait_time',3)
    return self._browser.waiter.ec.url_matches(url_pattern,wait_time)
