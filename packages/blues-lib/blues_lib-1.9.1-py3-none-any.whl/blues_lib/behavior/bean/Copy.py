import time
from blues_lib.behavior.Bean import Bean
from blues_lib.util.Clipboard import Clipboard

class Copy(Bean):

  def _get(self)->str:
    # clear the clipboard before copy
    Clipboard.clear()
    
    # trigger the copy action
    kwargs = self._get_kwargs(['target_CS_WE','parent_CS_WE','timeout'])
    if self._to_be_clickable():
      self._scroll()
      self._browser.action.mouse.click(**kwargs)
      time.sleep(0.2)
      # get the text from the clipboard
      return Clipboard.paste()
