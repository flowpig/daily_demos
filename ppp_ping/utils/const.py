class _const(object):
    class ConstError(TypeError):
        pass
    def __setattr__(self,name,value):
        if self.__dict__.has_key(name):
            raise ConstError("can't rebind const (%s)"%name)
        self.__dict__[name]=value
const = _const()

const.HourSec   = 3600
const.DaySec    = 24 * const.HourSec
#config related items
const.CFDE = "DEFAULT"
const.CFMain = "main"
const.CFFile   = '/conf/sr_service.cfg'
const.SERVICE = 'service'
const.CFSer  = 'sr_url'
const.CFUser  = 'sr_user'
const.CFPass = 'sr_passwd'
const.CFSR   = "service_robot"
const.ALLEMEM = "allocate_memory"
const.TRAPPERIP   = "trapper_ip"
const.TRAPPERPORT = "trapper_port"
const.GRPCWORKER  = "grpc_worker_count"
const.CONFFD      = "bake_folder"
const.BAKEMD      = "bake_method"

const.PROCPOLLCOUT = "process_count"
const.TASKPERPROCESS = "task_per_process"
const.SREVENTSER   = "sr_event_server"
const.SRCRONTABSER = "crontab_task"
const.CFBAKETIME = "conf_bak_time"

#RTM API info
const.ID = "id"
const.RtmAuth = "auth"
const.RtmTempKey = "parentTemplates"
const.HostName = "host"
const.MACRO = "macro"
const.VALUE = "value"
const.MacroProto = "{$PROTOCOL}"

#RTM Template ID
const.SR7750 = "7750_ip_route"
const.SR7750EN = "7750_ip_route_en"
const.SR7950 = "7950_ip_route"
const.SR7210 = "7210_ip_route"
const.SR7705 = "7705_ip_route"
const.SR7950EN = "7950_ip_route_en"
const.SR7210EN = "7210_ip_route_en"
const.SR7705EN = "7705_ip_route_en"
const.BitRate = 100
 
#task related
const.TaskInit  = 'Init'
const.TaskRun   = 'Running'
const.TaskSuc   = 'Success'
const.TaskFail  = 'Failed'

const.MaxTrendValue = -9223372036854775807
const.MinTrendValue = 9223372036854775807

const.ConfBakeFolder = "/var/www/html/service_robot/conf_bake/"


