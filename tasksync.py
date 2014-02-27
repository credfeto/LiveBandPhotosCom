import webapp2
import logging
import datetime
import sync

class TaskSyncHandler(webapp2.RequestHandler):

    def get(self):

        today = datetime.date.today()
        startDate = today - datetime.timedelta(days=1)
        
        logging.info("Running daily Cron for : " + startDate.isoformat())

        url = 'http://admin.livebandphotos.co.uk/transfergigsonly.php'
        #url = 'http://localhost/GalleryMetadata/transfer.xml'

        url = url + '?startDate=' + startDate.isoformat()
        
        sync.sync_now(url)
        logging.info("Daily Cron finished")

app = webapp2.WSGIApplication([
    ('/tasks/sync', TaskSyncHandler)
])
