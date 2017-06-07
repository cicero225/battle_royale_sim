from Objs.Items.Item import Item, ItemInstance


class StatusInstance(ItemInstance):    
    @staticmethod
    def copyOrMakeInstance(item):
        if hasattr(item, "item"):
            newStatus = copy.copy(item)
            newStatus.data = copy.deepcopy(item.data)
        else:
            newStatus = StatusInstance(item)
        return newStatus
    
    @staticmethod
    def takeOrMakeInstance(item):
        if hasattr(item, "item"):
            newStatus = item
        else:
            newStatus = StatusInstance(item)
        return newStatus

class Status(Item):
   def makeInstance(self, count=1, data=None):
        if data is None:
            data = {}
        thisInstance = StatusInstance(self, count)
        thisInstance.data = data
        return thisInstance