import youtube_dl

class VideoGetter:
    def __init__(self):
        self.url = None
        self.title = None
        self.duracion = None
        self.imageurl = None
        self.video = None
        self.formats = None

    def getUrl(self, url):
        self.url = self.title = self.duracion = self.imageurl = self.video = self.formats = None
        try:
            with youtube_dl.YoutubeDL() as ydl:
                result = ydl.extract_info(
                    url,
                    download=False
                )
            if 'entries' in result:
                video = result['entries'][0]
            else:
                video = result
            self.url = url
            self.title = video["title"]
            self.imageurl = video["thumbnails"][0]["url"]
            self.video = video
            self.duracion = video["duration"]
        except youtube_dl.utils.DownloadError:
            pass

    def getVideo(self, parent, format, path):
        temp_filename = path.split(".")
        if len(temp_filename) > 1:
            if not temp_filename[len(temp_filename)-1] == format:
                path += "."+format
        else:
            path += "."+format
        ydl_options = {
            "format": self.formats[format]["format_id"],
            "progress_hooks": [parent.progressHook],
            'outtmpl': path,
        }
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            ydl.download([self.url])




    def get_audio_formats(self):
        self.formats = {item["ext"]:item for item in self.video["formats"]}