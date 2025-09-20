import sys,os,re,time

from blues_lib.behavior.bean.Bean import Bean
from blues_lib.util.Clipboard import Clipboard
from blues_lib.util.AutoGUI import AutoGUI

class Paste(Bean):

  def _set(self)->bool:
    text = self._config.get('value','')
    if not text:
      return False

    # step1: put the text into the clipboard
    Clipboard.copy(text)
    time.sleep(0.1)  

    # locate and focus the input controller
    kwargs = self._get_kwargs(['target_CS_WE','parent_CS_WE','timeout'])
    self._browser.action.mouse.click(**kwargs)
    time.sleep(0.1)  

    # 3. paste the text into the input controller
    AutoGUI.paste()
    time.sleep(0.2)
    return True

