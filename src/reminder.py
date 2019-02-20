import pickle as pk
from datetime import datetime as dt



class Page:
    def __init__(self, title, desc):
        """
        Initiate a generic note object

        :param title: task's title
        :param desc: task's description
        """

        self.title = title
        self.desc = desc




class ChecklistItem:
    def __init__(self, itemString, parent=None, expire=None):
        self.itemString = itemString
        self.itemBool = 0
        self.subItems = []
        self.parent = parent
        self.beginDT = dt.today() # datetime.datetime
        self.endDT = expire # datetime.datetime
        self.totalTime = (self.endDT - self.beginDT) if self.endDT else None
        if self.totalTime:
            if self.totalTime.days < 0:
                print("You can't go back to the past, kadoy :p")
                print("Today is",dt.strftime(self.beginDT, "%d/%m/%y %I:%M%p"), "and the deadline is", dt.strftime(self.endDT, "%d/%m/%y %I:%M%p"))
                del self
    def __str__(self):
        ret = ""
        if self.itemBool:
            ret = "[x] "
            ret += self.itemString + "\t[        DONE        ]\n"
        else:
            ret = "[ ] "
            elapsedBars = round((self.getTimeLeft() / self.totalTime) * 20) if self.endDT else None
            ret += self.itemString + (("\t[        DUE         ]\n" if self.getTimeLeft().days < 0 else "   [" + elapsedBars * '#' + (20 - elapsedBars) * ' ' + ']\n') if self.endDT else "\n")



        for item in self.subItems:
            ret += "\t"+str(item)

        return ret

    def __eq__(self, other):
        try:
            return self.itemString == other
        except:
            return 0

    def updateEndDT(self, newDT):
        self.endDT = newDT  # datetime.datetime
        self.totalTime = (self.endDT - self.beginDT) if self.endDT else None

    def getTimeLeft(self):
        return self.endDT - dt.today()

    def addSub(self, sitemString):
        self.subItems.append(ChecklistItem(sitemString, self))

    def check(self, forceValue=-1): #force value ONLY used in special case; correspondence with super and sub item will not be checked/adjusted when focce-check
        if forceValue >= 0:
            self.itemBool = forceValue
            return
        else:
            self. itemBool = not self.itemBool
        if self.parent:
            self.parent._sicb(self)
        for item in self.subItems:
            item.check(self.itemBool)
        return self.itemBool

    def _sicb(self, sitem): #subitem callback
        if not sitem.isChecked():
            self.check(0) #one subitem unchecked, must force uncheck
        else:
            for item in self.subItems:
                if not item.isChecked():
                    self.check(0)
                    return
            self.check(1) #all subitem checked, must force check

    def edit(self, string):
        self.itemString = string

    def isChecked(self):
        return self.itemBool

    def getSuper(self):
        return self.parent



class Checklist(Page):
    def __init__(self, title, desc, items=[]):
        Page.__init__(self, title, desc)
        self.items = self._cl_pop(items)
        self.index = {}
        self.lstPtr = None

    def __len__(self):
        return len(self.items)

    def __str__(self):
        ret = ""
        ret += self.title + "\n"
        ret += self.desc + "\n"
        for item in self.items:
            ret += str(item)
        return ret

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        f = open("./test", "wb")
        pk.dump(self, f)
        f.close()

    def _cl_pop(self, items):
        ret = []
        for item in items:
            ret.append(ChecklistItem(item))
        return ret

    def _genDT(self, date, time):
        try:
            if not date:
                return dt.combine(dt.today(), dt.strptime(time, "%I:%M%p").timetz())
            return dt.strptime(date+" "+time, "%d/%m/%y %I:%M%p")
        except:
            return None
    def _isDup(self, newItem, list):
        for item in list:
            if item == newItem:
                return 0
        return 1
    def add(self, newItem, parentName=None, date=None, time=None):
        itemList = [] # declaration for clarity.
        pendingParent = None
        if not parentName:
            itemList = self.items
        else:
            try:
                parent = self.lookupHelper(parentName)
                # if len(parentList) > 1:
                #     cnt = 1
                #     for item in parentList:
                #         if not item.parent:
                #             print(str(cnt) + ".",item)
                #         else:
                #             print(str(cnt) + ".",item.parent)
                #         cnt += 1
                #     print("Which one?")
                #     user = input("> ")
                #     itemList = parentList[int(user)-1].subItems
                #     pendingParent = parentList[int(user)-1]
                # else:
                #     itemList = parentList[0].subItems
                #     pendingParent = parentList[0]
                itemList = parent.subItems
                pendingParent = parent

            except:
                print("Error in finding parent")
                return
        if not self._isDup(newItem,itemList): return
        if date:
            if time:
                itemList.append(ChecklistItem(newItem, parent=pendingParent, expire=self._genDT(date, time)))
            else:
                itemList.append(ChecklistItem(newItem, parent=pendingParent, expire=self._genDT(date, "11:59pm"))) # default time is at the end of the due date
        elif time:
            itemList.append(ChecklistItem(newItem, parent=pendingParent, expire=self._genDT(0,time)))  # default date is today
        else:
            itemList.append(ChecklistItem(newItem, parent=pendingParent))
        itemList[-1].check(forceValue=0) # update parents if any

    def lookupHelper(self,findItem,itemList=None):
        res = self.lookup(findItem,itemList=itemList)
        if not res:
            return 0
        elif len(res) > 1:
            cnt = 1
            for item in res:
                if not item.parent:
                    print(str(cnt) + ".", item)
                else:
                    print(str(cnt) + ".", item.parent)
                cnt += 1
            print("Which one?")
            user = input("> ")
            return res[int(user) - 1]
        elif len(res) == 1:
            return res[0]

    def lookup(self, findItem, itemList=None, isRoot=1):  # BFS to prioritize super-most items when looking up
        subItemList = []
        ret = []
        targetList = itemList if itemList else self.items
        for item in targetList:
            if item == findItem:
                ret += [item]
            else:
                subItemList += item.subItems
        if subItemList == []: # there is no more layer
            return ret
        else:
            ret += self.lookup(findItem, subItemList)
            if not isRoot:
                return ret + self.lookup(findItem, subItemList)
            else:
                return ret

    def remove(self, delItem):
        for item in self.items:
            if item == delItem:
                del self.items[self.items.index(item)]

    def getIsChecked(self, status):
        ret = []
        for item in self.items:
            if not (item.isChecked() ^ status):
                ret.append(item)
        return ret

    # def sort(self, item, mode, list=None): # mode: 1 for alphabetical, 2 for






# task1 = Page("Shopping list", "Eggs, milk, cheese")
# with Checklist("Shopping list", "For trader joe", ["egg","milk"]) as checklist1:
#     checklist1.add("cheese", "egg", time="12:23pm")
#     checklist1.add("egg", "milk")
#     # checklist1.add("spinach","egg")
#
#     print(checklist1)
#     print("----------------")
#     for item in checklist1.getIsChecked(1):
#         print(item)
