import youtube_dl
import os
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
            ydl_options = {
                "noplaylist": True
            }
            with youtube_dl.YoutubeDL(ydl_options) as ydl:
                result = ydl.extract_info(
                    url,
                    download=False
                )
            if 'entries' in result:
                print(result['entries'])
            else:
                video = result
            self.url = url
            self.title = video["title"]
            self.imageurl = video["thumbnails"][0]["url"]
            self.video = video
            self.duracion = video["duration"]
            return 0
        except youtube_dl.DownloadError as error:
            if "is not a valid URL" in str(error):
                return -1
            elif "Unable to download webpage" in str(error):
                return -2
        except IndexError:
            return -1

    def getVideo(self, parent, format, path):
        temp_filename = path.split(".")
        if len(temp_filename) > 1:
            if not temp_filename[len(temp_filename)-1] == format:
                path += "."+format
        else:
            path += "."+format
        ydl_options = {
            "format": self.formats[format]["format_id"],
            "noplaylist": True,
            "progress_hooks": [parent.progressHook],
            'outtmpl': path,
        }
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            try:
                ydl.download([self.url])
            except ValueError:
                os.remove(f"{path}.part")
                return




    def get_audio_formats(self):
        self.formats = {item["ext"]:item for item in self.video["formats"]}