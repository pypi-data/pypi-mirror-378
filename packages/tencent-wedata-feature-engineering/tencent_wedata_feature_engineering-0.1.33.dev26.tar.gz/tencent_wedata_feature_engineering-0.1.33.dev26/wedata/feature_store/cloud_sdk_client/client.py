import json
from tencentcloud.wedata.v20210820.wedata_client import WedataClient, models
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from wedata.feature_store.cloud_sdk_client.utils import get_client_profile
from wedata.feature_store.cloud_sdk_client.models import (
    CreateOnlineFeatureTableRequest,
    CreateOnlineFeatureTableResponse,
    DescribeNormalSchedulerExecutorGroupsRequest,
    DescribeNormalSchedulerExecutorGroupsResponse)


class FeatureCloudSDK:
    def __init__(self, secret_id: str, secret_key: str, region: str):
        self._client = WedataClient(credential.Credential(secret_id, secret_key), region, get_client_profile())

    def CreateOnlineFeatureTable(self, request: CreateOnlineFeatureTableRequest) -> 'CreateOnlineFeatureTableResponse':
        """
        创建在线特征表
        Args:
            request: 创建请求参数

        Returns:
            创建结果响应
        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self._client.call("CreateOnlineFeatureTable", params, headers=headers)
            response = json.loads(body)
            model = CreateOnlineFeatureTableResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))

    def DescribeNormalSchedulerExecutorGroups(self, request: DescribeNormalSchedulerExecutorGroupsRequest) -> 'DescribeNormalSchedulerExecutorGroupsResponse':
        """
        查询普通调度器执行器组
        Args:
            request: 查询请求参数

        Returns:
            查询结果响应
        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self._client.call("DescribeNormalSchedulerExecutorGroups", params, headers=headers)
            response = json.loads(body)
            model = DescribeNormalSchedulerExecutorGroupsResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))
