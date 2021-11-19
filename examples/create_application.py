import o2x5xx
import sys
import time

if len(sys.argv) > 1:
    address = sys.argv[1]
else:
    address = '192.168.0.69'

# create device
device = o2x5xx.Device(address)

# open a session and create an application for editing
session = device.requestSession()
session.startEdit()
applicationIndex = session.edit.createApplication()
application = session.edit.editApplication(applicationIndex)

# configure the application to
# - free-run at 10 Hz
application.setParameter("TriggerMode", "1")
application.setParameter("FrameRate", "10")
# name and save the application and stop editing
application.setParameter("Name", "o2x5xx-python example application")
application.save()
session.edit.stopEditingApplication()

# set the new application as active and save the change
session.edit.device.setParameter("ActiveApplication", str(applicationIndex))
session.edit.device.save()

# finish the session
session.cancelSession()
