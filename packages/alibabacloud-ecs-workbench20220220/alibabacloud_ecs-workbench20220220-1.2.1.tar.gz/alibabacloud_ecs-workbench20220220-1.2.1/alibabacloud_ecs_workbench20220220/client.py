# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from typing import Dict
from Tea.core import TeaCore

from alibabacloud_tea_openapi.client import Client as OpenApiClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util.client import Client as UtilClient
from alibabacloud_endpoint_util.client import Client as EndpointUtilClient
from alibabacloud_ecs_workbench20220220 import models as ecs_workbench_20220220_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_openapi_util.client import Client as OpenApiUtilClient


class Client(OpenApiClient):
    """
    *\
    """
    def __init__(
        self, 
        config: open_api_models.Config,
    ):
        super().__init__(config)
        self._endpoint_rule = ''
        self.check_config(config)
        self._endpoint = self.get_endpoint('ecs-workbench', self._region_id, self._endpoint_rule, self._network, self._suffix, self._endpoint_map, self._endpoint)

    def get_endpoint(
        self,
        product_id: str,
        region_id: str,
        endpoint_rule: str,
        network: str,
        suffix: str,
        endpoint_map: Dict[str, str],
        endpoint: str,
    ) -> str:
        if not UtilClient.empty(endpoint):
            return endpoint
        if not UtilClient.is_unset(endpoint_map) and not UtilClient.empty(endpoint_map.get(region_id)):
            return endpoint_map.get(region_id)
        return EndpointUtilClient.get_endpoint_rules(product_id, region_id, endpoint_rule, network, suffix)

    def get_instance_record_config_with_options(
        self,
        request: ecs_workbench_20220220_models.GetInstanceRecordConfigRequest,
        runtime: util_models.RuntimeOptions,
    ) -> ecs_workbench_20220220_models.GetInstanceRecordConfigResponse:
        """
        @summary 获取实例录屏配置
        
        @param request: GetInstanceRecordConfigRequest
        @param runtime: runtime options for this request RuntimeOptions
        @return: GetInstanceRecordConfigResponse
        """
        UtilClient.validate_model(request)
        body = {}
        if not UtilClient.is_unset(request.instance_id):
            body['InstanceId'] = request.instance_id
        if not UtilClient.is_unset(request.region_id):
            body['RegionId'] = request.region_id
        req = open_api_models.OpenApiRequest(
            body=OpenApiUtilClient.parse_to_map(body)
        )
        params = open_api_models.Params(
            action='GetInstanceRecordConfig',
            version='2022-02-20',
            protocol='HTTPS',
            pathname='/',
            method='POST',
            auth_type='AK',
            style='RPC',
            req_body_type='formData',
            body_type='json'
        )
        return TeaCore.from_map(
            ecs_workbench_20220220_models.GetInstanceRecordConfigResponse(),
            self.call_api(params, req, runtime)
        )

    async def get_instance_record_config_with_options_async(
        self,
        request: ecs_workbench_20220220_models.GetInstanceRecordConfigRequest,
        runtime: util_models.RuntimeOptions,
    ) -> ecs_workbench_20220220_models.GetInstanceRecordConfigResponse:
        """
        @summary 获取实例录屏配置
        
        @param request: GetInstanceRecordConfigRequest
        @param runtime: runtime options for this request RuntimeOptions
        @return: GetInstanceRecordConfigResponse
        """
        UtilClient.validate_model(request)
        body = {}
        if not UtilClient.is_unset(request.instance_id):
            body['InstanceId'] = request.instance_id
        if not UtilClient.is_unset(request.region_id):
            body['RegionId'] = request.region_id
        req = open_api_models.OpenApiRequest(
            body=OpenApiUtilClient.parse_to_map(body)
        )
        params = open_api_models.Params(
            action='GetInstanceRecordConfig',
            version='2022-02-20',
            protocol='HTTPS',
            pathname='/',
            method='POST',
            auth_type='AK',
            style='RPC',
            req_body_type='formData',
            body_type='json'
        )
        return TeaCore.from_map(
            ecs_workbench_20220220_models.GetInstanceRecordConfigResponse(),
            await self.call_api_async(params, req, runtime)
        )

    def get_instance_record_config(
        self,
        request: ecs_workbench_20220220_models.GetInstanceRecordConfigRequest,
    ) -> ecs_workbench_20220220_models.GetInstanceRecordConfigResponse:
        """
        @summary 获取实例录屏配置
        
        @param request: GetInstanceRecordConfigRequest
        @return: GetInstanceRecordConfigResponse
        """
        runtime = util_models.RuntimeOptions()
        return self.get_instance_record_config_with_options(request, runtime)

    async def get_instance_record_config_async(
        self,
        request: ecs_workbench_20220220_models.GetInstanceRecordConfigRequest,
    ) -> ecs_workbench_20220220_models.GetInstanceRecordConfigResponse:
        """
        @summary 获取实例录屏配置
        
        @param request: GetInstanceRecordConfigRequest
        @return: GetInstanceRecordConfigResponse
        """
        runtime = util_models.RuntimeOptions()
        return await self.get_instance_record_config_with_options_async(request, runtime)

    def list_instance_records_with_options(
        self,
        request: ecs_workbench_20220220_models.ListInstanceRecordsRequest,
        runtime: util_models.RuntimeOptions,
    ) -> ecs_workbench_20220220_models.ListInstanceRecordsResponse:
        """
        @summary 获取实例录屏记录列表
        
        @param request: ListInstanceRecordsRequest
        @param runtime: runtime options for this request RuntimeOptions
        @return: ListInstanceRecordsResponse
        """
        UtilClient.validate_model(request)
        body = {}
        if not UtilClient.is_unset(request.instance_id):
            body['InstanceId'] = request.instance_id
        if not UtilClient.is_unset(request.page_number):
            body['PageNumber'] = request.page_number
        if not UtilClient.is_unset(request.page_size):
            body['PageSize'] = request.page_size
        if not UtilClient.is_unset(request.region_id):
            body['RegionId'] = request.region_id
        req = open_api_models.OpenApiRequest(
            body=OpenApiUtilClient.parse_to_map(body)
        )
        params = open_api_models.Params(
            action='ListInstanceRecords',
            version='2022-02-20',
            protocol='HTTPS',
            pathname='/',
            method='POST',
            auth_type='AK',
            style='RPC',
            req_body_type='formData',
            body_type='json'
        )
        return TeaCore.from_map(
            ecs_workbench_20220220_models.ListInstanceRecordsResponse(),
            self.call_api(params, req, runtime)
        )

    async def list_instance_records_with_options_async(
        self,
        request: ecs_workbench_20220220_models.ListInstanceRecordsRequest,
        runtime: util_models.RuntimeOptions,
    ) -> ecs_workbench_20220220_models.ListInstanceRecordsResponse:
        """
        @summary 获取实例录屏记录列表
        
        @param request: ListInstanceRecordsRequest
        @param runtime: runtime options for this request RuntimeOptions
        @return: ListInstanceRecordsResponse
        """
        UtilClient.validate_model(request)
        body = {}
        if not UtilClient.is_unset(request.instance_id):
            body['InstanceId'] = request.instance_id
        if not UtilClient.is_unset(request.page_number):
            body['PageNumber'] = request.page_number
        if not UtilClient.is_unset(request.page_size):
            body['PageSize'] = request.page_size
        if not UtilClient.is_unset(request.region_id):
            body['RegionId'] = request.region_id
        req = open_api_models.OpenApiRequest(
            body=OpenApiUtilClient.parse_to_map(body)
        )
        params = open_api_models.Params(
            action='ListInstanceRecords',
            version='2022-02-20',
            protocol='HTTPS',
            pathname='/',
            method='POST',
            auth_type='AK',
            style='RPC',
            req_body_type='formData',
            body_type='json'
        )
        return TeaCore.from_map(
            ecs_workbench_20220220_models.ListInstanceRecordsResponse(),
            await self.call_api_async(params, req, runtime)
        )

    def list_instance_records(
        self,
        request: ecs_workbench_20220220_models.ListInstanceRecordsRequest,
    ) -> ecs_workbench_20220220_models.ListInstanceRecordsResponse:
        """
        @summary 获取实例录屏记录列表
        
        @param request: ListInstanceRecordsRequest
        @return: ListInstanceRecordsResponse
        """
        runtime = util_models.RuntimeOptions()
        return self.list_instance_records_with_options(request, runtime)

    async def list_instance_records_async(
        self,
        request: ecs_workbench_20220220_models.ListInstanceRecordsRequest,
    ) -> ecs_workbench_20220220_models.ListInstanceRecordsResponse:
        """
        @summary 获取实例录屏记录列表
        
        @param request: ListInstanceRecordsRequest
        @return: ListInstanceRecordsResponse
        """
        runtime = util_models.RuntimeOptions()
        return await self.list_instance_records_with_options_async(request, runtime)

    def list_terminal_commands_with_options(
        self,
        request: ecs_workbench_20220220_models.ListTerminalCommandsRequest,
        runtime: util_models.RuntimeOptions,
    ) -> ecs_workbench_20220220_models.ListTerminalCommandsResponse:
        """
        @summary 查看实例Workbench登录后执行命令的历史列表。
        
        @param request: ListTerminalCommandsRequest
        @param runtime: runtime options for this request RuntimeOptions
        @return: ListTerminalCommandsResponse
        """
        UtilClient.validate_model(request)
        body = {}
        if not UtilClient.is_unset(request.page_number):
            body['PageNumber'] = request.page_number
        if not UtilClient.is_unset(request.page_size):
            body['PageSize'] = request.page_size
        if not UtilClient.is_unset(request.region_id):
            body['RegionId'] = request.region_id
        if not UtilClient.is_unset(request.terminal_session_token):
            body['TerminalSessionToken'] = request.terminal_session_token
        req = open_api_models.OpenApiRequest(
            body=OpenApiUtilClient.parse_to_map(body)
        )
        params = open_api_models.Params(
            action='ListTerminalCommands',
            version='2022-02-20',
            protocol='HTTPS',
            pathname='/',
            method='POST',
            auth_type='AK',
            style='RPC',
            req_body_type='formData',
            body_type='json'
        )
        return TeaCore.from_map(
            ecs_workbench_20220220_models.ListTerminalCommandsResponse(),
            self.call_api(params, req, runtime)
        )

    async def list_terminal_commands_with_options_async(
        self,
        request: ecs_workbench_20220220_models.ListTerminalCommandsRequest,
        runtime: util_models.RuntimeOptions,
    ) -> ecs_workbench_20220220_models.ListTerminalCommandsResponse:
        """
        @summary 查看实例Workbench登录后执行命令的历史列表。
        
        @param request: ListTerminalCommandsRequest
        @param runtime: runtime options for this request RuntimeOptions
        @return: ListTerminalCommandsResponse
        """
        UtilClient.validate_model(request)
        body = {}
        if not UtilClient.is_unset(request.page_number):
            body['PageNumber'] = request.page_number
        if not UtilClient.is_unset(request.page_size):
            body['PageSize'] = request.page_size
        if not UtilClient.is_unset(request.region_id):
            body['RegionId'] = request.region_id
        if not UtilClient.is_unset(request.terminal_session_token):
            body['TerminalSessionToken'] = request.terminal_session_token
        req = open_api_models.OpenApiRequest(
            body=OpenApiUtilClient.parse_to_map(body)
        )
        params = open_api_models.Params(
            action='ListTerminalCommands',
            version='2022-02-20',
            protocol='HTTPS',
            pathname='/',
            method='POST',
            auth_type='AK',
            style='RPC',
            req_body_type='formData',
            body_type='json'
        )
        return TeaCore.from_map(
            ecs_workbench_20220220_models.ListTerminalCommandsResponse(),
            await self.call_api_async(params, req, runtime)
        )

    def list_terminal_commands(
        self,
        request: ecs_workbench_20220220_models.ListTerminalCommandsRequest,
    ) -> ecs_workbench_20220220_models.ListTerminalCommandsResponse:
        """
        @summary 查看实例Workbench登录后执行命令的历史列表。
        
        @param request: ListTerminalCommandsRequest
        @return: ListTerminalCommandsResponse
        """
        runtime = util_models.RuntimeOptions()
        return self.list_terminal_commands_with_options(request, runtime)

    async def list_terminal_commands_async(
        self,
        request: ecs_workbench_20220220_models.ListTerminalCommandsRequest,
    ) -> ecs_workbench_20220220_models.ListTerminalCommandsResponse:
        """
        @summary 查看实例Workbench登录后执行命令的历史列表。
        
        @param request: ListTerminalCommandsRequest
        @return: ListTerminalCommandsResponse
        """
        runtime = util_models.RuntimeOptions()
        return await self.list_terminal_commands_with_options_async(request, runtime)

    def login_instance_with_options(
        self,
        request: ecs_workbench_20220220_models.LoginInstanceRequest,
        runtime: util_models.RuntimeOptions,
    ) -> ecs_workbench_20220220_models.LoginInstanceResponse:
        """
        @summary 登录实例
        
        @param request: LoginInstanceRequest
        @param runtime: runtime options for this request RuntimeOptions
        @return: LoginInstanceResponse
        """
        UtilClient.validate_model(request)
        query = {}
        if not UtilClient.is_unset(request.instance_login_info):
            query['InstanceLoginInfo'] = request.instance_login_info
        if not UtilClient.is_unset(request.partner_info):
            query['PartnerInfo'] = request.partner_info
        if not UtilClient.is_unset(request.user_account):
            query['UserAccount'] = request.user_account
        req = open_api_models.OpenApiRequest(
            query=OpenApiUtilClient.query(query)
        )
        params = open_api_models.Params(
            action='LoginInstance',
            version='2022-02-20',
            protocol='HTTPS',
            pathname='/',
            method='POST',
            auth_type='AK',
            style='RPC',
            req_body_type='formData',
            body_type='json'
        )
        return TeaCore.from_map(
            ecs_workbench_20220220_models.LoginInstanceResponse(),
            self.call_api(params, req, runtime)
        )

    async def login_instance_with_options_async(
        self,
        request: ecs_workbench_20220220_models.LoginInstanceRequest,
        runtime: util_models.RuntimeOptions,
    ) -> ecs_workbench_20220220_models.LoginInstanceResponse:
        """
        @summary 登录实例
        
        @param request: LoginInstanceRequest
        @param runtime: runtime options for this request RuntimeOptions
        @return: LoginInstanceResponse
        """
        UtilClient.validate_model(request)
        query = {}
        if not UtilClient.is_unset(request.instance_login_info):
            query['InstanceLoginInfo'] = request.instance_login_info
        if not UtilClient.is_unset(request.partner_info):
            query['PartnerInfo'] = request.partner_info
        if not UtilClient.is_unset(request.user_account):
            query['UserAccount'] = request.user_account
        req = open_api_models.OpenApiRequest(
            query=OpenApiUtilClient.query(query)
        )
        params = open_api_models.Params(
            action='LoginInstance',
            version='2022-02-20',
            protocol='HTTPS',
            pathname='/',
            method='POST',
            auth_type='AK',
            style='RPC',
            req_body_type='formData',
            body_type='json'
        )
        return TeaCore.from_map(
            ecs_workbench_20220220_models.LoginInstanceResponse(),
            await self.call_api_async(params, req, runtime)
        )

    def login_instance(
        self,
        request: ecs_workbench_20220220_models.LoginInstanceRequest,
    ) -> ecs_workbench_20220220_models.LoginInstanceResponse:
        """
        @summary 登录实例
        
        @param request: LoginInstanceRequest
        @return: LoginInstanceResponse
        """
        runtime = util_models.RuntimeOptions()
        return self.login_instance_with_options(request, runtime)

    async def login_instance_async(
        self,
        request: ecs_workbench_20220220_models.LoginInstanceRequest,
    ) -> ecs_workbench_20220220_models.LoginInstanceResponse:
        """
        @summary 登录实例
        
        @param request: LoginInstanceRequest
        @return: LoginInstanceResponse
        """
        runtime = util_models.RuntimeOptions()
        return await self.login_instance_with_options_async(request, runtime)

    def set_instance_record_config_with_options(
        self,
        request: ecs_workbench_20220220_models.SetInstanceRecordConfigRequest,
        runtime: util_models.RuntimeOptions,
    ) -> ecs_workbench_20220220_models.SetInstanceRecordConfigResponse:
        """
        @summary 设置实例录屏配置
        
        @param request: SetInstanceRecordConfigRequest
        @param runtime: runtime options for this request RuntimeOptions
        @return: SetInstanceRecordConfigResponse
        """
        UtilClient.validate_model(request)
        body = {}
        if not UtilClient.is_unset(request.enabled):
            body['Enabled'] = request.enabled
        if not UtilClient.is_unset(request.expiration_days):
            body['ExpirationDays'] = request.expiration_days
        if not UtilClient.is_unset(request.instance_id):
            body['InstanceId'] = request.instance_id
        if not UtilClient.is_unset(request.record_storage_target):
            body['RecordStorageTarget'] = request.record_storage_target
        if not UtilClient.is_unset(request.region_id):
            body['RegionId'] = request.region_id
        req = open_api_models.OpenApiRequest(
            body=OpenApiUtilClient.parse_to_map(body)
        )
        params = open_api_models.Params(
            action='SetInstanceRecordConfig',
            version='2022-02-20',
            protocol='HTTPS',
            pathname='/',
            method='POST',
            auth_type='AK',
            style='RPC',
            req_body_type='formData',
            body_type='json'
        )
        return TeaCore.from_map(
            ecs_workbench_20220220_models.SetInstanceRecordConfigResponse(),
            self.call_api(params, req, runtime)
        )

    async def set_instance_record_config_with_options_async(
        self,
        request: ecs_workbench_20220220_models.SetInstanceRecordConfigRequest,
        runtime: util_models.RuntimeOptions,
    ) -> ecs_workbench_20220220_models.SetInstanceRecordConfigResponse:
        """
        @summary 设置实例录屏配置
        
        @param request: SetInstanceRecordConfigRequest
        @param runtime: runtime options for this request RuntimeOptions
        @return: SetInstanceRecordConfigResponse
        """
        UtilClient.validate_model(request)
        body = {}
        if not UtilClient.is_unset(request.enabled):
            body['Enabled'] = request.enabled
        if not UtilClient.is_unset(request.expiration_days):
            body['ExpirationDays'] = request.expiration_days
        if not UtilClient.is_unset(request.instance_id):
            body['InstanceId'] = request.instance_id
        if not UtilClient.is_unset(request.record_storage_target):
            body['RecordStorageTarget'] = request.record_storage_target
        if not UtilClient.is_unset(request.region_id):
            body['RegionId'] = request.region_id
        req = open_api_models.OpenApiRequest(
            body=OpenApiUtilClient.parse_to_map(body)
        )
        params = open_api_models.Params(
            action='SetInstanceRecordConfig',
            version='2022-02-20',
            protocol='HTTPS',
            pathname='/',
            method='POST',
            auth_type='AK',
            style='RPC',
            req_body_type='formData',
            body_type='json'
        )
        return TeaCore.from_map(
            ecs_workbench_20220220_models.SetInstanceRecordConfigResponse(),
            await self.call_api_async(params, req, runtime)
        )

    def set_instance_record_config(
        self,
        request: ecs_workbench_20220220_models.SetInstanceRecordConfigRequest,
    ) -> ecs_workbench_20220220_models.SetInstanceRecordConfigResponse:
        """
        @summary 设置实例录屏配置
        
        @param request: SetInstanceRecordConfigRequest
        @return: SetInstanceRecordConfigResponse
        """
        runtime = util_models.RuntimeOptions()
        return self.set_instance_record_config_with_options(request, runtime)

    async def set_instance_record_config_async(
        self,
        request: ecs_workbench_20220220_models.SetInstanceRecordConfigRequest,
    ) -> ecs_workbench_20220220_models.SetInstanceRecordConfigResponse:
        """
        @summary 设置实例录屏配置
        
        @param request: SetInstanceRecordConfigRequest
        @return: SetInstanceRecordConfigResponse
        """
        runtime = util_models.RuntimeOptions()
        return await self.set_instance_record_config_with_options_async(request, runtime)

    def view_instance_records_with_options(
        self,
        request: ecs_workbench_20220220_models.ViewInstanceRecordsRequest,
        runtime: util_models.RuntimeOptions,
    ) -> ecs_workbench_20220220_models.ViewInstanceRecordsResponse:
        """
        @summary 查看实例录屏内容
        
        @param request: ViewInstanceRecordsRequest
        @param runtime: runtime options for this request RuntimeOptions
        @return: ViewInstanceRecordsResponse
        """
        UtilClient.validate_model(request)
        body = {}
        if not UtilClient.is_unset(request.instance_id):
            body['InstanceId'] = request.instance_id
        if not UtilClient.is_unset(request.region_id):
            body['RegionId'] = request.region_id
        if not UtilClient.is_unset(request.terminal_session_token):
            body['TerminalSessionToken'] = request.terminal_session_token
        req = open_api_models.OpenApiRequest(
            body=OpenApiUtilClient.parse_to_map(body)
        )
        params = open_api_models.Params(
            action='ViewInstanceRecords',
            version='2022-02-20',
            protocol='HTTPS',
            pathname='/',
            method='POST',
            auth_type='AK',
            style='RPC',
            req_body_type='formData',
            body_type='json'
        )
        return TeaCore.from_map(
            ecs_workbench_20220220_models.ViewInstanceRecordsResponse(),
            self.call_api(params, req, runtime)
        )

    async def view_instance_records_with_options_async(
        self,
        request: ecs_workbench_20220220_models.ViewInstanceRecordsRequest,
        runtime: util_models.RuntimeOptions,
    ) -> ecs_workbench_20220220_models.ViewInstanceRecordsResponse:
        """
        @summary 查看实例录屏内容
        
        @param request: ViewInstanceRecordsRequest
        @param runtime: runtime options for this request RuntimeOptions
        @return: ViewInstanceRecordsResponse
        """
        UtilClient.validate_model(request)
        body = {}
        if not UtilClient.is_unset(request.instance_id):
            body['InstanceId'] = request.instance_id
        if not UtilClient.is_unset(request.region_id):
            body['RegionId'] = request.region_id
        if not UtilClient.is_unset(request.terminal_session_token):
            body['TerminalSessionToken'] = request.terminal_session_token
        req = open_api_models.OpenApiRequest(
            body=OpenApiUtilClient.parse_to_map(body)
        )
        params = open_api_models.Params(
            action='ViewInstanceRecords',
            version='2022-02-20',
            protocol='HTTPS',
            pathname='/',
            method='POST',
            auth_type='AK',
            style='RPC',
            req_body_type='formData',
            body_type='json'
        )
        return TeaCore.from_map(
            ecs_workbench_20220220_models.ViewInstanceRecordsResponse(),
            await self.call_api_async(params, req, runtime)
        )

    def view_instance_records(
        self,
        request: ecs_workbench_20220220_models.ViewInstanceRecordsRequest,
    ) -> ecs_workbench_20220220_models.ViewInstanceRecordsResponse:
        """
        @summary 查看实例录屏内容
        
        @param request: ViewInstanceRecordsRequest
        @return: ViewInstanceRecordsResponse
        """
        runtime = util_models.RuntimeOptions()
        return self.view_instance_records_with_options(request, runtime)

    async def view_instance_records_async(
        self,
        request: ecs_workbench_20220220_models.ViewInstanceRecordsRequest,
    ) -> ecs_workbench_20220220_models.ViewInstanceRecordsResponse:
        """
        @summary 查看实例录屏内容
        
        @param request: ViewInstanceRecordsRequest
        @return: ViewInstanceRecordsResponse
        """
        runtime = util_models.RuntimeOptions()
        return await self.view_instance_records_with_options_async(request, runtime)
