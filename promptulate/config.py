# Copyright (c) 2023 Zeeland
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Copyright Owner: Zeeland
# GitHub Link: https://github.com/Undertone0809/
# Project Link: https://github.com/Undertone0809/promptulate
# Contact Email: zeeland@foxmail.com

import os
from typing import Optional
from promptulate import utils
from promptulate.utils.singleton import Singleton
from promptulate.utils.openai_key_pool import OpenAIKeyPool
from promptulate.utils.logger import get_logger

PROXY_MODE = ["off", "custom", "promptulate"]
logger = get_logger()


def set_enable_cache(value: bool):
    """Caching is enabled by default. Disabling caching is not recommended."""
    Config().enable_cache = value


class Config(metaclass=Singleton):
    def __init__(self):
        logger.info(f"[promptulate config] Config initialization")
        self.enable_cache: bool = True
        self._proxy_mode: str = PROXY_MODE[0]
        self._proxies: Optional[dict] = None
        self.openai_url = "https://api.openai.com/v1/chat/completions"
        self.openai_proxy_url = "https://chatgpt-api.shn.hk/v1/"  # FREE API
        self.key_default_retry_times = 5
        """If llm(like OpenAI) unable to obtain data, retry request until the data is obtained."""

    @property
    def openai_api_key(self):
        """This attribution has deprecated to use. Using `get_openai_api_key`"""
        if "OPENAI_API_KEY" in os.environ.keys():
            if self.enable_cache:
                utils.get_cache()["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
            return os.getenv("OPENAI_API_KEY")
        if self.enable_cache and "OPENAI_API_KEY" in utils.get_cache():
            return utils.get_cache()["OPENAI_API_KEY"]
        raise ValueError("OPENAI API key is not provided. Please set your key.")

    def get_openai_api_key(self, model: str) -> str:
        if self.enable_cache:
            openai_key_pool: OpenAIKeyPool = OpenAIKeyPool()
            key = openai_key_pool.get(model)
            if key:
                return key
        return self.openai_api_key


    def get_key_retry_times(self, model: str) -> int:
        if self.enable_cache:
            openai_key_pool: OpenAIKeyPool = OpenAIKeyPool()
            return openai_key_pool.get_num(model)
        return self.key_default_retry_times

    @property
    def proxy_mode(self) -> str:
        if self.enable_cache and "PROXY_MODE" in utils.get_cache():
            return utils.get_cache()["PROXY_MODE"]
        return self._proxy_mode

    @proxy_mode.setter
    def proxy_mode(self, value):
        self._proxy_mode = value
        if self.enable_cache:
            utils.get_cache()["PROXY_MODE"] = value

    @property
    def proxies(self) -> Optional[dict]:
        if self.enable_cache and "PROXIES" in utils.get_cache():
            return utils.get_cache()["PROXIES"] if self.proxy_mode == "custom" else None
        return self._proxies

    @proxies.setter
    def proxies(self, value):
        self._proxies = value
        if self.enable_cache:
            utils.get_cache()["PROXIES"] = value

    @property
    def openai_request_url(self) -> str:
        if self.proxy_mode == PROXY_MODE[2]:
            self.proxies = None
            return self.openai_proxy_url
        return self.openai_url

    def set_proxy_mode(self, mode: str, proxies: Optional[dict] = None):
        self.proxy_mode = mode
        self.proxies = proxies
