import sys,os,re
from typing import Any

from blues_lib.behavior.bean.Bean import Bean

class File(Bean):

  def _get(self)->Any:
    kwargs = self._get_kwargs(['target_CS_WE','parent_CS_WE','timeout'])
    return self._browser.element.info.get_value(**kwargs)

  def _set(self)->Any:
    kwargs = self._get_kwargs(['target_CS_WE','value','wait_time','parent_CS_WE','timeout'])
    return self._browser.element.file.write(**kwargs)
