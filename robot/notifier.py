#coding:utf-8
import Queue
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import logging

from robot.configuration import cmInstance


# from robot.modules import Email
class Notifier(object):

    class NotificationClient(object):

        def __init__(self, gather, timestamp):
            self.gather = gather
            self.timestamp = timestamp

        def run(self):
            self.timestamp = self.gather(self.timestamp)

    def __init__(self, brain):
        self._logger = logging.getLogger(__name__)
        self.q = Queue.Queue()
        self.profile = cmInstance.getRootConfig()
        self.notifiers = []
        self.brain = brain

        if 'email' in self.profile and \
           ('enable' not in self.profile['email'] or self.profile['email']['enable']):
            self.notifiers.append(self.NotificationClient(
                self.handleEmailNotifications, None))
        else:
            self._logger.warning('email account not set ' +
                                 'in profile, email notifier will not be used')

        sched = BackgroundScheduler(daemon=True)
        sched.start()
        sched.add_job(self.gather, 'interval', seconds=30)
        atexit.register(lambda: sched.shutdown(wait=False))

    def gather(self):
        [client.run() for client in self.notifiers]

    def handleEmailNotifications(self, lastDate):
        pass
#         """Places new email notifications in the Notifier's queue."""
#         emails = Email.fetchUnreadEmails(self.profile, since=lastDate)
#         if emails:
#             lastDate = Email.getMostRecentDate(emails)
# 
#         def styleEmail(e):
#             subject = Email.getSubject(e, self.profile)
#             if Email.isEchoEmail(e, self.profile):
#                 if Email.isNewEmail(e):
#                     return subject.replace('[echo]', '')
#                 else:
#                     return ""
#             elif Email.isControlEmail(e, self.profile):
#                 self.brain.query([subject.replace('[control]', '')
#                                   .strip()], None, True)
#                 return ""
#             sender = Email.getSender(e)
#             return "您有来自 %s 的新邮件 %s" % (sender, subject)
#         for e in emails:
#             self.q.put(styleEmail(e))
# 
#         return lastDate

    def getNotification(self):
        """Returns a notification. Note that this function is consuming."""
        try:
            notif = self.q.get(block=False)
            return notif
        except Queue.Empty:
            return None

    def getAllNotifications(self):
        """
            Return a list of notifications in chronological order.
            Note that this function is consuming, so consecutive calls
            will yield different results.
        """
        notifs = []

        notif = self.getNotification()
        while notif:
            notifs.append(notif)
            notif = self.getNotification()

        return notifs
