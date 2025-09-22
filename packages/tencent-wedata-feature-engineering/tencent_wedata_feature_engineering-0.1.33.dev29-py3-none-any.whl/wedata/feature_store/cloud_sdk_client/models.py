from tencentcloud.common.abstract_model import AbstractModel
import warnings


class OfflineFeatureConfiguration(AbstractModel):
    """
    创建在线表时的离线特征部分描述
    """

    def __init__(self):
        self._DatasourceName = None
        self._TableName = None
        self._DatasourceType = None
        self._PrimaryKeys = None
        self._TimestampColumn = None
        self._DatabaseName = None
        self._EngineName = None

    @property
    def DatasourceName(self):
        return self._DatasourceName

    @DatasourceName.setter
    def DatasourceName(self, DatasourceName):
        self._DatasourceName = DatasourceName

    @property
    def TableName(self):
        return self._TableName

    @TableName.setter
    def TableName(self, TableName):
        self._TableName = TableName

    @property
    def DatasourceType(self):
        return self._DatasourceType

    @DatasourceType.setter
    def DatasourceType(self, DatasourceType):
        self._DatasourceType = DatasourceType

    @property
    def PrimaryKeys(self):
        return self._PrimaryKeys

    @PrimaryKeys.setter
    def PrimaryKeys(self, PrimaryKeys):
        self._PrimaryKeys = PrimaryKeys

    @property
    def TimestampColumn(self):
        return self._TimestampColumn

    @TimestampColumn.setter
    def TimestampColumn(self, TimestampColumn):
        self._TimestampColumn = TimestampColumn

    @property
    def DatabaseName(self):
        return self._DatabaseName

    @DatabaseName.setter
    def DatabaseName(self, DatabaseName):
        self._DatabaseName = DatabaseName

    @property
    def EngineName(self):
        return self._EngineName

    @EngineName.setter
    def EngineName(self, EngineName):
        self._EngineName = EngineName

    def _deserialize(self, params):
        self._DatasourceName = params.get("DatasourceName")
        self._TableName = params.get("TableName")
        self._DatasourceType = params.get("DatasourceType")
        self._PrimaryKeys = params.get("PrimaryKeys")
        self._TimestampColumn = params.get("TimestampColumn")
        self._DatabaseName = params.get("DatabaseName")
        self._EngineName = params.get("EngineName")
        member_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in member_set:
                member_set.remove(property_name)
        if len(member_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(member_set))


class TaskSchedulerConfiguration(AbstractModel):
    """
    创建在线特征表时的调度信息描述
    CycleType: 调度周期类型
    ScheduleTimeZone: 调度时区
    StartTime: 调度开始时间
    EndTime: 调度结束时间
    ExecutionStartTime: 执行开始时间
    ExecutionEndTime: 执行结束时间
    RunPriority: 运行优先级
    CrontabExpression: cron表达式
    """

    def __init__(self):
        self._CycleType = None
        self._ScheduleTimeZone = None
        self._StartTime = None
        self._EndTime = None
        self._ExecutionStartTime = None
        self._ExecutionEndTime = None
        self._RunPriority = None
        self._CrontabExpression = None

    @property
    def CycleType(self):
        return self._CycleType

    @CycleType.setter
    def CycleType(self, CycleType):
        self._CycleType = CycleType

    @property
    def ScheduleTimeZone(self):
        return self._ScheduleTimeZone

    @ScheduleTimeZone.setter
    def ScheduleTimeZone(self, ScheduleTimeZone):
        self._ScheduleTimeZone = ScheduleTimeZone

    @property
    def StartTime(self):
        return self._StartTime

    @StartTime.setter
    def StartTime(self, StartTime):
        self._StartTime = StartTime

    @property
    def EndTime(self):
        return self._EndTime

    @EndTime.setter
    def EndTime(self, EndTime):
        self._EndTime = EndTime

    @property
    def ExecutionStartTime(self):
        return self._ExecutionStartTime

    @ExecutionStartTime.setter
    def ExecutionStartTime(self, ExecutionStartTime):
        self._ExecutionStartTime = ExecutionStartTime

    @property
    def ExecutionEndTime(self):
        return self._ExecutionEndTime

    @ExecutionEndTime.setter
    def ExecutionEndTime(self, ExecutionEndTime):
        self._ExecutionEndTime = ExecutionEndTime

    @property
    def RunPriority(self):
        return self._RunPriority

    @RunPriority.setter
    def RunPriority(self, RunPriority):
        self._RunPriority = RunPriority

    @property
    def CrontabExpression(self):
        return self._CrontabExpression

    @CrontabExpression.setter
    def CrontabExpression(self, CrontabExpression):
        self._CrontabExpression = CrontabExpression

    def _deserialize(self, params):
        self.CycleType = params.get("CycleType")
        self.ScheduleTimeZone = params.get("ScheduleTimeZone")
        self.StartTime = params.get("StartTime")
        self.EndTime = params.get("EndTime")
        self.ExecutionStartTime = params.get("ExecutionStartTime")
        self.ExecutionEndTime = params.get("ExecutionEndTime")
        self.RunPriority = params.get("RunPriority")
        self.CrontabExpression = params.get("CrontabExpression")
        member_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in member_set:
                member_set.remove(property_name)
        if len(member_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(member_set))


class OnlineFeatureConfiguration(AbstractModel):
    """
    在线特征信息
    """

    def __init__(self):
        self._UseDefault = None
        self._DatasourceName = None
        self._DB = None
        self._Host = None
        self._Port = None

    @property
    def UserDefault(self):
        return self._UseDefault

    @UserDefault.setter
    def UserDefault(self, UseDefault):
        self._UseDefault = UseDefault

    @property
    def DataSourceName(self):
        return self._DataSourceName

    @DataSourceName.setter
    def DataSourceName(self, DataSourceName):
        self._DataSourceName = DataSourceName

    @property
    def DB(self):
        return self._DB

    @DB.setter
    def DB(self, DB):
        self._DB = DB

    @property
    def Host(self):
        return self._Host


    @Host.setter
    def Host(self, Host: str):
        self._Host = Host

    @property
    def Port(self):
        return self._Port

    @Port.setter
    def Port(self, Port: int):
        self._Port = Port

    def _deserialize(self, params):
        self.UseDefault = params.get("UseDefault")
        self.DataSourceName = params.get("DataSourceName")
        self.DB = params.get("DB")
        self.Host = params.get("Host")
        self.Port = params.get("Port")
        member_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in member_set:
                member_set.remove(property_name)
        if len(member_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(member_set))


class CreateOnlineFeatureTableRequest(AbstractModel):
    """
    创建在线特征表
    ProjectId
    ResourceGroupId
    OfflineFeatureConfiguration
    TaskSchedulerConfiguration
    OnlineFeatureConfiguration
    RequestFromSource
    """

    def __init__(self):
        self._ProjectId = None
        self._ResourceGroupId = None
        self._OfflineFeatureConfiguration = None
        self._TaskSchedulerConfiguration = None
        self._OnlineFeatureConfiguration = None
        self._RequestFromSource = None


    @property
    def ProjectId(self):
        return self._ProjectId

    @ProjectId.setter
    def ProjectId(self, ProjectId):
        self._ProjectId = ProjectId

    @property
    def ResourceGroupId(self):
        return self._ResourceGroupId

    @ResourceGroupId.setter
    def ResourceGroupId(self, ResourceGroupId):
        self._ResourceGroupId = ResourceGroupId

    @property
    def OfflineFeatureConfiguration(self):
        return self._OfflineFeatureConfiguration

    @OfflineFeatureConfiguration.setter
    def OfflineFeatureConfiguration(self, OfflineFeatureConfiguration):
        self._OfflineFeatureConfiguration = OfflineFeatureConfiguration

    @property
    def TaskSchedulerConfiguration(self):
        return self._TaskSchedulerConfiguration

    @TaskSchedulerConfiguration.setter
    def TaskSchedulerConfiguration(self, TaskSchedulerConfiguration):
        self._TaskSchedulerConfiguration = TaskSchedulerConfiguration

    @property
    def OnlineFeatureConfiguration(self):
        return self._OnlineFeatureConfiguration


    @OnlineFeatureConfiguration.setter
    def OnlineFeatureConfiguration(self, OnlineFeatureConfiguration):
        self._OnlineFeatureConfiguration = OnlineFeatureConfiguration

    @property
    def RequestFromSource(self):
        return self._RequestFromSource

    @RequestFromSource.setter
    def RequestFromSource(self, RequestFromSource):
        self._RequestFromSource = RequestFromSource

    def _deserialize(self, params):
        self.ProjectId = params.get("ProjectId")
        self.ResourceGroupId = params.get("ResourceGroupId")
        if params.get("OfflineFeatureConfiguration") is not None:
            self.OfflineFeatureConfiguration = OfflineFeatureConfiguration()
            self.OfflineFeatureConfiguration._deserialize(params.get("OfflineFeatureConfiguration"))
        if params.get("TaskSchedulerConfiguration") is not None:
            self.TaskSchedulerConfiguration = TaskSchedulerConfiguration()
            self.TaskSchedulerConfiguration._deserialize(params.get("TaskSchedulerConfiguration"))
        if params.get("OnlineFeatureConfiguration") is not None:
            self._OnlineFeatureConfiguration = OnlineFeatureConfiguration()
            self._OnlineFeatureConfiguration._deserialize(params.get("OnlineFeatureConfiguration"))
        self.RequestFromSource = params.get("RequestFromSource")
        member_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in member_set:
                member_set.remove(property_name)
        if len(member_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(member_set))


class CreateOnlineFeatureTableResponse(AbstractModel):
    """
    创建在线特征表返回包
    """
    def __init__(self):
        self._WorkflowId = None
        self._WorkflowTaskId = None


    @property
    def WorkflowId(self):
        return self._WorkflowId

    @WorkflowId.setter
    def WorkflowId(self, WorkflowId):
        self._WorkflowId = WorkflowId

    @property
    def WorkflowTaskId(self):
        return self._WorkflowTaskId

    @WorkflowTaskId.setter
    def WorkflowTaskId(self, WorkflowTaskId):
        self._WorkflowTaskId = WorkflowTaskId

    def _deserialize(self, params):
        self.WorkflowId = params.get("WorkflowId")
        self.WorkflowTaskId = params.get("WorkflowTaskId")
        member_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in member_set:
                member_set.remove(property_name)
        if len(member_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(member_set))


class DescribeNormalSchedulerExecutorGroupsData(AbstractModel):
    """
    执行资源组管理-可用的调度资源组列表
    ExecutorGroupId
    ExecutorGroupName
    ExecutorGroupDesc
    Available
    PythonSubVersions
    EnvJson
    """

    def __init__(self):
        self._ExecutorGroupId = None
        self._ExecutorGroupName = None
        self._ExecutorGroupDesc = None
        self._Available = None
        self._PythonSubVersions = None
        self._EnvJson = None


    @property
    def ExecutorGroupId(self):
        return self._ExecutorGroupId

    @ExecutorGroupId.setter
    def ExecutorGroupId(self, ExecutorGroupId):
        self._ExecutorGroupId = ExecutorGroupId

    @property
    def ExecutorGroupName(self):
        return self._ExecutorGroupName

    @ExecutorGroupName.setter
    def ExecutorGroupName(self, ExecutorGroupName):
        self._ExecutorGroupName = ExecutorGroupName

    @property
    def ExecutorGroupDesc(self):
        return self._ExecutorGroupDesc

    @ExecutorGroupDesc.setter
    def ExecutorGroupDesc(self, ExecutorGroupDesc):
        self._ExecutorGroupDesc = ExecutorGroupDesc

    @property
    def Available(self):
        return self._Available

    @Available.setter
    def Available(self, Available):
        self._Available = Available

    @property
    def PythonSubVersions(self):
        return self._PythonSubVersions

    @PythonSubVersions.setter
    def PythonSubVersions(self, PythonSubVersions):
        self._PythonSubVersions = PythonSubVersions

    @property
    def EnvJson(self):
        return self._EnvJson

    @EnvJson.setter
    def EnvJson(self, EnvJson):
        self._EnvJson = EnvJson

    def _deserialize(self, params):
        self._ExecutorGroupId = params.get("ExecutorGroupId")
        self._ExecutorGroupName = params.get("ExecutorGroupName")
        self._ExecutorGroupDesc = params.get("ExecutorGroupDesc")
        self._Available = params.get("Available")
        self._PythonSubVersions = params.get("PythonSubVersions")
        self._EnvJson = params.get("EnvJson")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            if name in memeber_set:
                memeber_set.remove(name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))


class DescribeNormalSchedulerExecutorGroupsResponse(AbstractModel):
    """
    查询可用的调度执行资源
    """
    def __init__(self):
        self._Data = None

    @property
    def Data(self) -> list[DescribeNormalSchedulerExecutorGroupsData]:
        return self._Data

    @Data.setter
    def Data(self, Data):
        self._Data = Data

    def _deserialize(self, params):
        if params.get("Data") is not None:
            self._Data = []
            for item in params.get("Data", []):
                self._Data.append(DescribeNormalSchedulerExecutorGroupsData()._deserialize(item))
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            if name in memeber_set:
                memeber_set.remove(name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))


class DescribeNormalSchedulerExecutorGroupsRequest(AbstractModel):
    """
    查询可用的调度执行资源
    """
    def __init__(self):
        self._ProjectId = None
        self._OnlyAvailable = None

    @property
    def ProjectId(self):
        return self._ProjectId

    @ProjectId.setter
    def ProjectId(self, ProjectId: str):
        self._ProjectId = ProjectId

    @property
    def OnlyAvailable(self):
        return self._OnlyAvailable

    @OnlyAvailable.setter
    def OnlyAvailable(self, OnlyAvailable: bool):
        self._OnlyAvailable = OnlyAvailable

    def _deserialize(self, params):
        self._ProjectId = params.get("ProjectId")
        self._OnlyAvailable = params.get("OnlyAvailable")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            if name in memeber_set:
                memeber_set.remove(name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))

