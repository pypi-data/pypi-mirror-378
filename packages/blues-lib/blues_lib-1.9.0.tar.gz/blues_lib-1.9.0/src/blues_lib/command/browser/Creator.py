import sys,os,re

from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.type.output.STDOut import STDOut
from blues_lib.sele.browser.BrowserFactory import BrowserFactory   
from blues_lib.namespace.CommandName import CommandName
from blues_lib.config.ConfigManager import config

class Creator(NodeCommand):

  NAME = CommandName.Browser.CREATOR
  TYPE = CommandName.Type.ACTION

  def _invoke(self)->STDOut:
    mode =  self._node_conf.get('mode')
    kwargs = self._node_conf.get('kwargs') or config.get('webdriver')
    browser = BrowserFactory(mode).create(**kwargs)
    return STDOut(200,'ok',browser) if browser else STDOut(500,'failed to create the browser')