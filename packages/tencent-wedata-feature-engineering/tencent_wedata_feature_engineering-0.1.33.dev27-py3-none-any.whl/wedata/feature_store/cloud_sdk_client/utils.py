from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.profile.client_profile import ClientProfile
from wedata.feature_store.cloud_sdk_client.models import TaskSchedulerConfiguration


def get_client_profile() -> 'ClientProfile':
    """
    获取网络客户端配置
    """
    http_profile = HttpProfile()
    http_profile.protocol = "https"
    http_profile.endpoint = "wedata.internal.tencentcloudapi.com"

    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile
    return client_profile
