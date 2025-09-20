import sys,os,re

from blues_lib.type.factory.Factory import Factory
from blues_lib.type.model.Model import Model

from blues_lib.behavior.bean.Attr import Attr
from blues_lib.behavior.bean.CSS import CSS
from blues_lib.behavior.bean.Choice import Choice
from blues_lib.behavior.bean.File import File
from blues_lib.behavior.bean.Input import Input
from blues_lib.behavior.bean.AuthCodeInput import AuthCodeInput
from blues_lib.behavior.bean.Select import Select
from blues_lib.behavior.bean.Screenshot import Screenshot
from blues_lib.behavior.bean.Text import Text
from blues_lib.behavior.bean.Textarea import Textarea
from blues_lib.behavior.bean.Value import Value
from blues_lib.behavior.bean.FileCookie import FileCookie
from blues_lib.behavior.bean.BrCookie import BrCookie
from blues_lib.behavior.bean.Url import Url
from blues_lib.behavior.bean.Copy import Copy
from blues_lib.behavior.bean.Paste import Paste

from blues_lib.behavior.event.Click import Click
from blues_lib.behavior.event.Keyboard import Keyboard
from blues_lib.behavior.event.Framein import Framein
from blues_lib.behavior.event.Frameout import Frameout
from blues_lib.behavior.event.Hover import Hover
from blues_lib.behavior.event.Remove import Remove
from blues_lib.behavior.event.Rollin import Rollin
from blues_lib.behavior.event.Open import Open
from blues_lib.behavior.event.Quit import Quit

from blues_lib.behavior.checker.ElePresents import ElePresents
from blues_lib.behavior.checker.EleAbsents import EleAbsents
from blues_lib.behavior.checker.EleInvisible import EleInvisible
from blues_lib.behavior.checker.UrlChanges import UrlChanges
from blues_lib.behavior.checker.UrlContains import UrlContains
from blues_lib.behavior.checker.UrlToBe import UrlToBe
from blues_lib.behavior.checker.UrlMatches import UrlMatches
from blues_lib.behavior.checker.ToBeClickable import ToBeClickable
from blues_lib.behavior.checker.ToBeSelected import ToBeSelected
from blues_lib.behavior.checker.ToBePresence import ToBePresence
from blues_lib.behavior.checker.ToBeVisible import ToBeVisible

from blues_lib.behavior.general.Wait import Wait
from blues_lib.behavior.general.Email import Email

class BhvFactory(Factory):
  def __init__(self,model:Model,browser=None):
    self._model = model
    self._browser = browser

  def create_attr(self):
    return Attr(self._model,self._browser)
  
  def create_css(self):
    return CSS(self._model,self._browser)
  
  def create_choice(self):
    return Choice(self._model,self._browser)
  
  def create_file(self):
    return File(self._model,self._browser)
  
  def create_input(self):
    return Input(self._model,self._browser)
  
  def create_auth_code_input(self):
    return AuthCodeInput(self._model,self._browser)
  
  def create_select(self):
    return Select(self._model,self._browser)
  
  def create_screenshot(self):
    return Screenshot(self._model,self._browser)
  
  def create_text(self):
    return Text(self._model,self._browser)
  
  def create_textarea(self):
    return Textarea(self._model,self._browser)
  
  def create_value(self):
    return Value(self._model,self._browser)
  
  def create_file_cookie(self):
    return FileCookie(self._model,self._browser)
  
  def create_br_cookie(self):
    return BrCookie(self._model,self._browser)
  
  def create_url(self):
    return Url(self._model,self._browser)
  
  def create_copy(self):
    return Copy(self._model,self._browser)
  
  def create_paste(self):
    return Paste(self._model,self._browser)
  
  def create_click(self):
    return Click(self._model,self._browser)
  
  def create_keyboard(self):
    return Keyboard(self._model,self._browser)
  
  def create_framein(self):
    return Framein(self._model,self._browser)
  
  def create_frameout(self):
    return Frameout(self._model,self._browser)
  
  def create_hover(self):
    return Hover(self._model,self._browser)
  
  def create_remove(self):
    return Remove(self._model,self._browser)
  
  def create_rollin(self):
    return Rollin(self._model,self._browser)
  
  def create_open(self):
    return Open(self._model,self._browser)
  
  def create_quit(self):
    return Quit(self._model,self._browser)
  
  def create_ele_presents(self):
    return ElePresents(self._model,self._browser)
  
  def create_ele_absents(self):
    return EleAbsents(self._model,self._browser)
  
  def create_ele_invisible(self):
    return EleInvisible(self._model,self._browser)

  def create_url_changes(self):
    return UrlChanges(self._model,self._browser)
    
  def create_url_contains(self):
    return UrlContains(self._model,self._browser)
  
  def create_url_to_be(self):
    return UrlToBe(self._model,self._browser)
  
  def create_url_matches(self):
    return UrlMatches(self._model,self._browser)
  
  def create_to_be_clickable(self):
    return ToBeClickable(self._model,self._browser)

  def create_to_be_selected(self):
    return ToBeSelected(self._model,self._browser)
  
  def create_to_be_presence(self):
    return ToBePresence(self._model,self._browser)
  
  def create_to_be_visible(self):
    return ToBeVisible(self._model,self._browser)
  
  def create_wait(self):
    return Wait(self._model)
  
  def create_email(self):
    return Email(self._model)
  