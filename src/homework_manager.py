from reminder import Checklist, ChecklistItem
from datetime import datetime as dt, \
                     timedelta as td


HWM_FILE = "feb2019.hwm"
import time, os, sys

import pickle as pk

class Class(ChecklistItem):
    def __init__(self, className):
        ChecklistItem.__init__(self, className)

class Homework(ChecklistItem):
    def __init__(self, homeworkName, classObj, dueDT):
        ChecklistItem.__init__(self, homeworkName, expire=dueDT, parent=classObj)
    def __str__(self):
        ret = "\t"
        if self.itemBool:
            ret = "[x] "
            ret += self.itemString + "\t[        DONE        ]\n"
        else:
            ret = "[ ] "
            elapsedBars = round((self.getTimeLeft() / self.totalTime) * 20) if self.endDT else None
            ret += self.itemString + (("\t[        DUE         ]\n" if self.getTimeLeft().days < 0 else "\t[" + elapsedBars * '#' + (
                                                      20 - elapsedBars) * ' ' + '] Started on: '+dt.strftime(self.beginDT, "%d/%m/%y %I:%M%p")+'\tDue on: '+dt.strftime(self.endDT, "%d/%m/%y %I:%M%p")+'\n') if self.endDT else "\n")
        for item in self.subItems:
            ret += str(item)

        return ret

class HomeworkSubTask(ChecklistItem):
    def __init__(self, taskName):
        ChecklistItem.__init__(self, taskName)
    def __str__(self):
        ret = "\t\t"
        if self.itemBool:
            ret = "[x] "+self.itemString
        else:
            ret = "[ ] "+self.itemString

        return ret
class HomeworkManager(Checklist):
    def __init__(self):
        Checklist.__init__(self, "Homework Manage", "a homework manager")

    def getSgtStartDT(self, hw, reqHr, hrPerDay, skipDay):
        if (reqHr < hrPerDay):
            return hw.endDT - td(hours=reqHr) # just start it reqHr before the due time
        totalDay = td(days=reqHr//hrPerDay) - td(days=1) # the due date is included in the total time
        return hw.endDT - (totalDay + td(days=skipDay)) - min(td(hours=reqHr), td(hours=hrPerDay))

    def _save(self,name):
        pass


    def addClass(self, className):
        self.add(className)

    def addHomework(self, className, homeworkName, dueDate, dueTime="11:59pm"):
        # self.add(homeworkName, className, dueDate, dueTime)
        if not dueTime:
            dueTime="11:59pm"
        if not className:
            print("No class name specified. Aborting...")
            return 1
        foundClass = self.lookupHelper(className)
        if foundClass:
            foundClass.subItems.append(Homework(homeworkName, foundClass, self._genDT(dueDate, dueTime)))
            foundClass._sicb(foundClass.subItems[-1])
        else:
            self.items.append(Class(className))
            self.items[-1].subItems.append(Homework(homeworkName, self.items[-1], self._genDT(dueDate, dueTime)))
            self.items[-1]._sicb(self.items[-1].subItems[-1])
        return 0

    def update(self):
        pass

    def editHomework(self):
        pass

    def getHomework(self, hwName=None, className=None):
        classHWList = self.lookupHelper(className)
        return classHWList.subItems

    def showClassHW(self, className):
        classHW = self.lookupHelper(className) # should always be a singleton list bc why have 2 same class??
        if len(classHW.subItems) == 0 or classHW.isChecked():
            print("You don't have any homework for " + className + ". Great job!")
        print("Homework for " + className + ":")
        for item in classHW.subItems:
            print(" - " + str(item))

def save(hwm):
    with open(HWM_FILE, "wb+") as f:
        pk.dump(hwm, f)

def startHWM():
    if not os.path.exists(HWM_FILE):
        save(HomeworkManager())

    with open(HWM_FILE,"rb+") as f:
        return pk.load(f)

def ui(hwm):
    print("Homework Manager v0.1")
    while True:
        os.system('clear')
        print("~ Main Menu ~")
        print("1. Add new homework")
        print("2. View homework")
        print("3. Update homework")
        print("4. Live monitor")
        print("0. Save and exit")
        try:
            user = int(input("> "))
        except ValueError:
            continue
        os.system('clear')
        if user == 1:
            className = input("Enter class name: ")
            if className == 'c': continue
            homework = input("Enter homework name: ")
            if homework == 'c': continue
            dueDate = input("Enter due date as dd/mm/yy: ")
            if dueDate == 'c': continue
            dueTime = input("Enter due time as hh:mm[AM|PM]: ")
            if dueTime == 'c': continue
            retval = hwm.addHomework(className, homework,dueDate, dueTime)
            if retval:
                print("Something when wrong...")
            else:
                print("Successfully added")
                input("<Press enter to continue>")
        elif user == 2:
            print(hwm)
            input("<Press enter to continue>")

        elif user == 3:
            className = input("Enter class name: ")
            if not className: continue
            homework = input("Enter homework name: ")
            if not homework: continue
            selectedClass = hwm.lookupHelper(className)
            if not selectedClass:
                print("Class not found")
                continue
            selectedHW = hwm.lookupHelper(homework, itemList=selectedClass.subItems)
            if not selectedHW:
                print("Homework not found")
                continue
            print("Homework found. Now what?")
            print("1. Mark Homework Done")
            print("2. Edit due date")
            print("3. Edit name")
            print("4. Delete homework")
            user = int(input("> "))
            if user == 1:
                selectedHW.check()
                print("Marked done. Good job!")
            elif user == 2:
                user = input("Enter new due date as dd/mm/yy: ")
                selectedHW.updateEndDT(hwm._genDT(user))
        elif user == 4:
            try:
                while True:
                    os.system("clear")
                    print("Press ENTER to quit")
                    print(hwm)
                    time.sleep(0.5)
            except KeyboardInterrupt:
                continue


        else:
            save(hwm)
            print("Goodbye")

            break



def main():
    hwm = startHWM()

    ui(hwm)
    save(hwm)

main()
