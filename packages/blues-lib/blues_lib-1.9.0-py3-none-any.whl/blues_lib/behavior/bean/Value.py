import sys,os,re
from typing import Any

from blues_lib.behavior.bean.Bean import Bean

class Value(Bean):

  def _get(self)->Any:
    kwargs = self._get_kwargs(['target_CS_WE','parent_CS_WE','timeout'])
    return self._browser.element.info.get_value(**kwargs)