from lib.utils.logger import Logger
from utils.const import const

from rtm_item import RTMItem

logger = Logger.get_logger()


class RTMHostAPI(object):
    TEMP_ATT=["templateid","name","host"]
    
    @staticmethod
    def get_host_info(api,**kwargs):
        host_info = api.host.get(**kwargs)[0]
        return host_info

    @staticmethod
    def get_items(rtm_api,**kwargs):
        key_item_dict = {}
        items = rtm_api.item.get(**kwargs)
        for item in items:
            temp_item = RTMItem(item)
            key_item_dict.update({temp_item.get_key():temp_item})
        logger.debug("Get all %s items",str(len(key_item_dict)))
        return key_item_dict

    @staticmethod
    def get_templates(rtm_api,host_id):
        host_info = RTMHostAPI.get_host_info(rtm_api,hostids=host_id,selectParentTemplates=RTMHostAPI.TEMP_ATT)
        return RTMHostAPI.get_template_list(rtm_api,host_info)

    @staticmethod
    def get_template_list(rtm_api,host_info):
        #print host_info
        templates = []
        if (const.RtmTempKey in host_info.keys()): 
            if (len(host_info[const.RtmTempKey]) > 0):
                for tem in host_info[const.RtmTempKey]:
                    templates.append(tem["host"])
                    template = rtm_api.template.get(templateids=tem["templateid"],\
                            selectParentTemplates=RTMHostAPI.TEMP_ATT)[0]
                    tem_templates = RTMHostAPI.get_template_list(rtm_api,template)
                    if len(tem_templates) > 0:
                        templates = templates + tem_templates
            return templates
        else:
            return templates

