"""Read public artifacts; write new standalone-question artifacts privately."""
import json
import os
from pathlib import Path
from triton.runtime.cache import FileCacheManager


class PublicReadThroughCache(FileCacheManager):
    def __init__(self,key,override=False,dump=False):
        super().__init__(key,override=override,dump=dump)
        self.public=None if override or dump else Path(os.environ['A100_PUBLIC_REFERENCE_CACHE'])/key

    def get_file(self,filename):
        own=super().get_file(filename)
        if own:return own
        if self.public is not None:
            path=self.public/filename
            if path.is_file():return str(path)
        return None

    def get_group(self,filename):
        own=super().get_group(filename)
        if own:return own
        if self.public is None:return None
        path=self.public/('__grp__'+filename)
        if not path.is_file():return None
        value=json.loads(path.read_text()).get('child_paths',{})
        if not value:return None
        root=self.public.parent.resolve()
        if all(Path(p).resolve().is_relative_to(root) and Path(p).is_file() for p in value.values()):
            return value
        return None
