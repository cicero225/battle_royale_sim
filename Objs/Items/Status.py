from Objs.Items.Item import Item, ItemInstance
import collections

class StatusInstance(ItemInstance):    
    pass

class Status(Item):
   def makeInstance(self, count=1, data=None):
        if data is None:
            data = collections.OrderedDict()
        thisInstance = StatusInstance(self, count)
        thisInstance.data = data
        return thisInstance