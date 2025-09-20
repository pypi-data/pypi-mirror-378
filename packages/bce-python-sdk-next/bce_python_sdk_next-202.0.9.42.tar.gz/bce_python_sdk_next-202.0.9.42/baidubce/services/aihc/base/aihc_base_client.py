# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the
# License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""
AIHC base client module.
"""
import copy
import json
import time

from baidubce import bce_base_client
from baidubce.auth import bce_v1_signer
from baidubce.http import handler, bce_http_client, http_methods
from baidubce.services.aihc import aihc_handler
from baidubce.services.aihc.base.aihc_request import aihc_request, get_utf8_value


class AIHCBaseClient(bce_base_client.BceBaseClient):
    """
    AIHC基础客户端类，提供公共方法
    """

    version = b'v2'

    def __init__(self, config=None):
        """
        初始化AIHC基础客户端
        
        Args:
            config: 配置对象，baidubce.bce_client_configuration.BceClientConfiguration实例
        """
        bce_base_client.BceBaseClient.__init__(self, config)

    def _merge_config(self, config=None):
        """
        合并配置对象
        
        Args:
            config: 要合并的配置对象，如果为None则返回当前配置
            
        Returns:
            baidubce.bce_client_configuration.BceClientConfiguration: 合并后的配置对象
        """
        if config is None:
            return self.config
        else:
            new_config = copy.copy(self.config)
            new_config.merge_non_none_values(config)
            return new_config
    
    def _aihc_request(self, http_method, path,
                      headers=None, params=None, body=None,
                      config=None, body_parser=None):
        config = self._merge_config(config)
        if body_parser is None:
            body_parser = aihc_handler.aihc_parse_json
        host = get_utf8_value(config.endpoint)
        # print(host)
        if headers is None:
            headers = {
                'version': 'v2',
                'Content-Type': 'application/json',
                'Host': host,
            }
        else:
            headers['version'] = 'v2'
            headers['Content-Type'] = 'application/json'
            headers[ 'Host'] = host

        http_method = get_utf8_value(http_method)
        # print(http_method, path, body, headers, params)
        return aihc_request(config,[aihc_handler.aihc_parse_error, body_parser],
            http_method, path, body, headers, params)

    def _send_request(self, http_method, path,
                      headers=None, params=None, body=None,
                      config=None, body_parser=None):
        """
        发送HTTP请求
        
        Args:
            http_method: HTTP方法
            path: 请求路径
            headers: 请求头（可选）
            params: 请求参数（可选）
            body: 请求体（可选）
            config: 配置对象（可选）
            body_parser: 响应体解析器（可选）
            
        Returns:
            baidubce.bce_response.BceResponse: 响应对象
        """
        config = self._merge_config(config)
        if body_parser is None:
            body_parser = aihc_handler.parse_json
        
        if headers is None:
            headers = {
                b'version': AIHCBaseClient.version,
                b'Content-Type': b'application/json',
            }
        else:
            headers[b'version'] = AIHCBaseClient.version
            headers[b'Content-Type'] = b'application/json'

        # headers[http_headers.HOST] = b'aihc.bj.baidubce.com'
        headers[b'x-bce-date'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()).encode('utf-8')

        return bce_http_client.send_request(
            config, bce_v1_signer.sign, [aihc_handler.parse_error, body_parser],
            http_method, path, body, headers, params)
    
    def _send_job_request(self, http_method, path,
                      body=None, headers=None, params=None,
                      config=None, body_parser=None):
        """
        发送任务相关HTTP请求
        
        Args:
            http_method: HTTP方法
            path: 请求路径
            body: 请求体（可选）
            headers: 请求头（可选）
            params: 请求参数（可选）
            config: 配置对象（可选）
            body_parser: 响应体解析器（可选）
            
        Returns:
            baidubce.bce_response.BceResponse: 响应对象
        """
        config = self._merge_config(config)
        if body_parser is None:
            body_parser = aihc_handler.parse_json
        
        if headers is None:
            headers = {
                b'X-API-Version': AIHCBaseClient.version,
                b'Content-Type': b'application/json'
            }
        else:
            headers[b'X-API-Version'] = AIHCBaseClient.version
            headers[b'Content-Type'] = b'application/json'

        return bce_http_client.send_request(
            config, bce_v1_signer.sign, [handler.parse_error, body_parser],
            http_method, path, body, headers, params) 