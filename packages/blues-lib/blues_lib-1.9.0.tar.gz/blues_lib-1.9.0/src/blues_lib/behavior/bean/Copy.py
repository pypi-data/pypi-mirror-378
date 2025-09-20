import sys,os,re,time

from blues_lib.behavior.bean.Bean import Bean
from blues_lib.util.Clipboard import Clipboard

class Copy(Bean):

  def _get(self)->str:
    # clear the clipboard before copy
    Clipboard.clear()
    
    # trigger the copy action
    kwargs = self._get_kwargs(['target_CS_WE','parent_CS_WE','timeout'])
    self._browser.action.mouse.click(**kwargs)
    time.sleep(0.5)
    
    # get the text from the clipboard
    return Clipboard.paste()
