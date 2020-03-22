import uuid
import datetime 

class upload:
    def __init__(self, filename, unique_filename, num_downloads, uploader, college, topic,created_at = datetime.datetime.now() ):
        self.filename = filename
        
        self.unique_filename = unique_filename 
        self.uploader = uploader
        self.created_at = created_at
        self.college = college
        self.num_downloads = num_downloads
        self.topic = topic



        