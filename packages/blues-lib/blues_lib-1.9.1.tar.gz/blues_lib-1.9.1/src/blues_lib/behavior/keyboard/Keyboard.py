from abc import abstractmethod
from blues_lib.behavior.Trigger import Trigger

class Keyboard(Trigger):

  def _trigger(self):
    self._focus()
    self._do()

  @abstractmethod
  def _do(self):
    pass
  
  def _focus(self):
    selector = self._config.get('target_CS_WE')
    if selector and self._to_be_clickable():
      return self._browser.action.mouse.click(selector) 

