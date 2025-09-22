from yta_constants.enum import YTAEnum as Enum
from yta_constants.ffmpeg import FfmpegPixelFormat, FfmpegVideoCodec, FfmpegAudioCodec, FfmpegAudioFormat, FfmpegAudioLayout
from yta_constants.file import FileExtension


class Settings(Enum):
    """
    The settings for our pyav video library.
    """

    DEFAULT_PIXEL_FORMAT: str = FfmpegPixelFormat.YUV420P.value
    """
    The pixel format we use by default.
    """
    # 'libx264' is an implementation of 'h264'
    DEFAULT_VIDEO_CODEC: str = FfmpegVideoCodec.LIBX264.value
    """
    The video codec we use by default.
    """
    DEFAULT_VIDEO_EXTENSION: str = FileExtension.MP4.value
    """
    The video file extension (and container)
    we use by default. Does not include the
    '.' at the begining.
    """
    DEFAULT_ALPHA_PIXEL_FORMAT: str = FfmpegPixelFormat.RGBA.value
    """
    The pixel format we use by default for
    videos with alpha layer.
    """
    DEFAULT_ALPHA_VIDEO_CODEC: str = FfmpegVideoCodec.LIBX264.value
    """
    The video codec we use by default for
    videos with alpha layer.
    """
    DEFAULT_ALPHA_VIDEO_EXTENSION: str = FileExtension.WEBM.value
    """
    The video file extension (and container)
    we use by default for videos with alpha
    layer. Does not include the '.' at the
    begining.
    """
    DEFAULT_VIDEO_FPS: int = 60
    """
    The video fps we use by default.
    """
    DEFAULT_VIDEO_SIZE: tuple[int, int] = (1920, 1080)
    """
    The video frame size we use by default.
    """

    DEFAULT_AUDIO_CODEC: str = FfmpegAudioCodec.AAC.value
    """
    The audio codec we use by default.
    """
    DEFAULT_AUDIO_EXTENSION: str = FileExtension.MP4.value
    """
    The audio file extension (and container)
    we use by default. Does not include the
    '.' at the begining.
    """
    DEFAULT_AUDIO_FORMAT: str = FfmpegAudioFormat.FLTP.value
    """
    The audio format we use by default.
    """
    DEFAULT_AUDIO_LAYOUT: str = FfmpegAudioLayout.STEREO.value
    """
    The audio layout we use by default.
    """
    DEFAULT_AUDIO_FPS: int = 44_100 # 48_000 is not working
    """
    The audio fps (or sample rate) we use by
    default.
    """
    DEFAULT_AUDIO_SAMPLES_PER_FRAME: int = 1_024
    """
    The samples per frame we use by default.
    """

    DEFAULT_FRAME_CACHE_SIZE: int = 60
    """
    The size we want for the cache size by
    default.

    TODO: This value is based on nothing
    """
    MIN_FRAME_CACHE_SIZE: int = 30
    """
    The minimum size we accept for the cache
    size.

    TODO: This value is based on nothing
    """
    MAX_FRAME_CACHE_SIZE: int = 120
    """
    The maximum size we accept for the cache
    size.

    TODO: This value is based on nothing
    """

"""
*Otros encoders posibles para H.264
Dependiendo de cómo tengas compilado FFmpeg, podrías tener más encoders disponibles:
libx264 → CPU (default, muy usado).
h264_nvenc → acelerado por GPU Nvidia.
h264_qsv → acelerado por Intel QuickSync.
h264_amf → acelerado por GPU AMD.
h264_videotoolbox → acelerado en macOS.
h264_v4l2m2m → acelerado en dispositivos Linux ARM (ej. Raspberry Pi).
Todos generan un bitstream H.264 válido, solo cambia la implementación.

---

This command will show all the H.264 encoders
my ffmpeg version has.
- ffmpeg -encoders | grep 264
"""