# storage_backends.py
from cloudinary_storage.storage import VideoMediaCloudinaryStorage

class VariationSoundStorage(VideoMediaCloudinaryStorage):
    """Storage for variation sound files (MP3, etc.) using Cloudinary video asset type."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Explicitly set resource type to video (audio files are treated as video)
        self.RESOURCE_TYPE = 'video'