import webapp2
import logging

import sync

class TaskSyncHandler(webapp2.RequestHandler):

    def get(self):

        url = 'http://admin.livebandphotos.co.uk/transfergigsonly.php'
        #url = 'http://localhost/GalleryMetadata/transfer.xml'

        logging.info("Running daily Cron")
        sync.sync_now(url)
        logging.info("Daily Cron finished")

app = webapp2.WSGIApplication([
    ('/tasks/sync', TaskSyncHandler)
])
