"""
A video reader using the PyAv (av) library
that, using ffmpeg, detects the video and
audio streams from a filename (that can be
a video file including both streams or an
audio file including only the audio stream).

When reading packets directly from the stream
we can receive packets with size=0, but we need
to process them and decode (or yield them). It
is only when we are passing packets to the mux
when we need to ignore the ones that are empty
(size=0).

TODO: Do we need to ignore all? By now, ignoring
not is causing exceptions, and ignoring them is
making it work perfectly.

The number of audio samples per frame is related
to the audio codec and usually it is a fixed
value for that codec, but sometimes it can be
variable or defined by the user when writing. It
is, for example, 1152 for the mp3, but can be
960, 1920 or 2880 for opus.
"""
from yta_video_pyav.reader.filter.dataclass import GraphFilter
from yta_video_pyav.reader.cache.video import VideoFrameCache
from yta_video_pyav.reader.cache.audio import AudioFrameCache
from yta_video_frame_time.t_fraction import THandler
from yta_validation.parameter import ParameterValidator
from av.video.frame import VideoFrame
from av.audio.frame import AudioFrame
from av.video.stream import VideoStream
from av.audio.stream import AudioStream
from av.container.input import InputContainer
from quicktions import Fraction
from av import open as av_open
from typing import Union

    
class _Reader:
    """
    Internal class to be inherited by our
    specific reader classes.
    """

    @property
    def has_video(
        self
    ) -> bool:
        """
        Flag to indicate if there is a video stream
        or not.
        """
        return self.video_stream is not None

    @property
    def has_audio(
        self
    ) -> bool:
        """
        Flag to indicate if there is an audio stream
        or not.
        """
        return self.audio_stream is not None

    def __init__(
        self,
        filename: str,
        video_filters: list[GraphFilter] = [],
        audio_filters: list[GraphFilter] = []
    ):
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)
        ParameterValidator.validate_mandatory_list_of_these_instances('video_filters', video_filters, GraphFilter)
        ParameterValidator.validate_mandatory_list_of_these_instances('audio_filters', audio_filters, GraphFilter)

        self.filename: str = filename
        """
        The filename of the video source.
        """
        self.container: InputContainer = None
        """
        The av input general container of the
        video (that also includes the audio) we
        are reading.
        """
        self.video_stream: Union[VideoStream, None] = None
        """
        The stream that includes the video. If
        no video stream this will be None.
        """
        self.audio_stream: Union[AudioStream, None] = None
        """
        The stream that includes the audio. If
        no audio stream this will be None.
        """
        # TODO: What if an audio filter in the
        # video_filters list or viceversa (?)
        self._video_filters: list[GraphFilter] = video_filters
        """
        The filters we want to apply to the video
        frames we read.
        """
        self._audio_filters: list[GraphFilter] = audio_filters
        """
        The filters we want to apply to the audio
        frames we read.
        """

    def reset(
        self
    ) -> 'VideoReader':
        """
        Reset all the instances, closing the file
        and opening again.

        This will also return to the first frame.
        """
        if self.container is not None:
            # TODO: Maybe accept forcing it (?)
            self.seek_video(0)
            self.seek_audio(0)
            #self.container.seek(0)
            #self.container.close()
        else:
            self.container = av_open(self.filename)
            
            self.video_stream = (
                self.container.streams.video[0]
                if self.container.streams.video else
                None
            )

            self.audio_stream = (
                self.container.streams.audio[0]
                if self.container.streams.audio else
                None
            )

            if (
                not self.has_video and
                not self.has_audio
            ):
                raise Exception(f'No video nor audio stream found in the "{self.filename}" file.')

            if self.has_video:
                # TODO: Should this be 'AUTO' (?)
                self.video_stream.thread_type = 'AUTO'

            if self.has_audio:
                # TODO: Should this be 'AUTO' (?)
                self.audio_stream.thread_type = 'AUTO'

            self.video_cache = (
                VideoFrameCache(
                    container = self.container,
                    stream = self.video_stream,
                    filters = self._video_filters
                )
                if self.has_video else
                None
            )

            self.audio_cache = (
                AudioFrameCache(
                    container = self.container,
                    stream = self.audio_stream,
                    filters = self._audio_filters
                )
                if self.has_audio else
                None
            )

    def set_video_filters(
        self,
        filters: list[GraphFilter] = []
    ) -> '_Reader':
        """
        Set the provided 'filters' as the video filters
        to apply, replacing the previous ones if 
        existing.

        If the reader doesn't have video stream these
        filters will be useless...
        """
        self._video_filters = filters
        
        if self.has_video:
            self.video_cache.set_filters(filters)

        return self

    def set_audio_filters(
        self,
        filters: list[GraphFilter] = []
    ) -> '_Reader':
        """
        Set the provided 'filters' as the audio filters
        to apply, replacing the previous ones if 
        existing.

        If the reader doesn't have audio stream these
        filters will be useless...
        """
        self._audio_filters = filters

        if self.has_audio:
            self.audio_cache.set_filters(filters)

        return self

    def seek_video(
        self,
        pts: int
    ) -> '_Reader':
        """
        Call the container '.seek()' method with
        the given 'pts' packet time stamp for the
        video stream.
        """
        self.container.seek(
            offset = pts,
            # TODO: What happens if this is None (?)
            stream = self.video_stream
        )

        return self
    
    def seek_audio(
        self,
        pts: int
    ) -> '_Reader':
        """
        Call the container '.seek()' method with
        the given 'pts' packet time stamp for the
        audio stream.
        """
        self.container.seek(
            offset = pts,
            # TODO: What happens if this is None (?)
            stream = self.audio_stream
        )

        return self

    def close(
        self
    ) -> None:
        """
        Close the container to free it.
        """
        self.container.close()

class VideoReader(_Reader):
    """
    Class to read video files with the pyav
    library. Those videos include a video stream
    but also could include an audio stream.
    """

    @property
    def pixel_format(
        self
    ) -> Union[str, None]:
        """
        The format of the audio pixel. Can be None
        if the file we are reading is an audio file.
        """
        return (
            self.video_stream.pix_fmt
            if self.has_video else
            None
        )

    @property
    def codec_name(
        self
    ) -> Union[str, None]:
        """
        Get the name of the video codec. Can be None
        if the file we are reading is an audio file.
        """
        return (
            self.video_stream.codec_context.name
            if self.has_video else
            None
        )
    
    @property
    def audio_codec_name(
        self
    ) -> Union[str, None]:
        """
        Get the name of the audio codec. Can be None
        if the file we are reading is a video file.
        """
        return (
            self.audio_stream.codec_context.name
            if self.has_audio else
            None
        )
    
    @property
    def audio_layout(
        self
    ) -> Union[str, None]:
        """
        Get the audio layout.
        """
        return (
            self.audio_stream.codec_context.layout
            if self.has_audio else
            None
        )
    
    @property
    def audio_format(
        self
    ) -> Union[str, None]:
        """
        Get the audio format.
        """
        return (
            self.audio_stream.codec_context.format
            if self.has_audio else
            None
        )

    @property
    def number_of_frames(
        self
    ) -> Union[int, None]:
        """
        The number of frames in the video. Can be None
        if the file we are reading is an audio file.
        """
        return (
            self.video_stream.frames
            if self.has_video else
            None
        )

    @property
    def audio_samples_per_frame(
        self
    ) -> int:
        """
        The amount of audio samples we obtain for each
        audio frame.
        """
        return (
            self.audio_stream.codec_context.frame_size
            if self.has_audio else
            None
        )
    
    @property
    def fps(
        self
    ) -> Union[Fraction, None]:
        """
        The fps of the video. Can be None if the
        file we are reading is an audio file.
        """
        return (
            self.video_stream.average_rate
            if self.has_video else
            None
        )
    
    @property
    def audio_fps(
        self
    ) -> Union[int, None]:
        """
        The fps of the audio. Can be None if the
        file we are reading is a video file.
        """
        return (
            self.audio_stream.rate
            if self.has_audio else
            None
        )
    
    @property
    def time_base(
        self
    ) -> Union[Fraction, None]:
        """
        The time base of the video. Can be None
        if the file we are reading is an audio file.
        """
        return (
            self.video_stream.time_base
            if self.has_video else
            None
        )

    @property
    def audio_time_base(
        self
    ) -> Union[Fraction, None]:
        """
        The time base of the audio. Can be None
        if the file we are reading is a video file.
        """
        return (
            self.audio_stream.time_base
            if self.has_audio else
            None
        )
    
    @property
    def ticks_per_frame(
        self
    ) -> int:
        """
        The number of ticks per video frame. A
        tick is the minimum amount of time and
        is the way 'pts' is measured, in ticks.

        This means that the 'pts' value will
        be increased this amount from one video
        frame to the next one.

        How we obtain it:
        - `(1 / fps) / time_base`
        """
        return Fraction(1, int(self.fps)) / self.time_base
    
    @property
    def duration(
        self
    ) -> Union[float, None]:
        """
        The duration of the video.
        """
        # TODO: What to do in the case we have
        # video stream but not 'duration' 
        # attribute (?)
        return (
            float(self.video_stream.duration * self.video_stream.time_base)
            if (
                self.has_video and
                self.video_stream.duration
            ) else
            None
        )

    @property
    def audio_duration(
        self
    ) -> Union[float, None]:
        """
        The duration of the audio.
        """
        # TODO: What to do in the case we have
        # audio stream but not 'duration' 
        # attribute (?)
        return (
            float(self.audio_stream.duration * self.audio_stream.time_base)
            if (
                self.has_audio and
                self.audio_stream.duration
            ) else
            None
        )
    
    @property
    def size(
        self
    ) -> Union[tuple[int, int], None]:
        """
        The size of the video in a (width, height) format.
        """
        return (
            (
                self.video_stream.width,
                self.video_stream.height
            )
            if self.has_video else
            None
        )
    
    @property
    def width(
        self
    ) -> Union[int, None]:
        """
        The width of the video, in pixels.
        """
        return (
            self.size[0]
            if self.size is not None else
            None
        )
    
    @property
    def height(
        self
    ) -> Union[int, None]:
        """
        The height of the video, in pixels.
        """
        return (
            self.size[1]
            if self.size is not None else
            None
        )
    
    # Any property related to audio has to
    # start with 'audio_property_name'

    def __init__(
        self,
        filename: str,
        video_filters: list[GraphFilter] = [],
        audio_filters: list[GraphFilter] = []
    ):
        _Reader.__init__(
            self,
            filename = filename,
            video_filters = video_filters,
            audio_filters = audio_filters
        )

        self.video_cache: VideoFrameCache = None
        """
        The video frame cache system to optimize
        the way we access to the frames.
        """
        self.audio_cache: AudioFrameCache = None
        """
        The audio frame cache system to optimize
        the way we access to the frames.
        """

        # TODO: Maybe we can read the first 
        # frame, store it and reset, so we have
        # it in memory since the first moment.
        # We should do it here because if we
        # iterate in some moment and then we
        # want to obtain it... it will be 
        # difficult.
        # Lets load the variables
        self.reset()

    def get_frame(
        self,
        t: Union[int, float, Fraction],
        do_apply_filters: bool = True
    ) -> Union[VideoFrame, None]:
        """
        Get the video frame that is in the 't' time
        moment provided.

        If 't' is an invalid moment (out of the time
        limits) this method will return None.
        """
        return self.video_cache.get_frame(
            t = t,
            do_apply_filters = do_apply_filters
        )

    def get_frames(
        self,
        start: Union[int, float, Fraction] = 0.0,
        end: Union[int, float, Fraction, None] = None,
        do_apply_filters: bool = True
    ):
        """
        Iterator to get the video frames in between
        the provided 'start' and 'end' time moments.

        If the provided 'start' and 'end' are out of
        the time limits this method will return None.
        """
        for frame in get_frames(
            cache = self.video_cache,
            start = start,
            end = end,
            do_apply_filters = do_apply_filters
        ):
            yield frame

    def get_audio_frame_at_t(
        self,
        t: Union[int, float, Fraction],
        do_apply_filters: bool = True
    ) -> Union[AudioFrame, None]:
        """
        Get the audio frame with the given 't' time
        moment, using the audio cache system.

        
        If 't' is an invalid moment (out of the time
        limits) this method will return None.
        """
        return (
            self.audio_cache.get_frame(
                t = t,
                do_apply_filters = do_apply_filters
            )
            if self.has_audio else
            None
        )
    
    def get_audio_frames_at_t(
        self,
        t: Union[int, float, Fraction],
        video_fps: Union[int, float, Fraction, None] = None,
        do_apply_filters: bool = True
        # TODO: Put iterator type and None
    ):
        """
        Get the sequence of audio frames for the 
        given video 't' time moment, using the
        audio cache system.

        This is useful when we want to write a
        video frame with its audio, so we obtain
        all the audio frames associated to it
        (remember that a video frame is associated
        with more than 1 audio frame).

        This iterator will have no elements if
        there are no audio frames at the provided
        't' time moment.
        """
        if not self.has_audio:
            #TODO: Should we return an empty array
            # or None directly (?)
            #yield None
            return None

        video_fps = (
            self.fps
            if video_fps is None else
            video_fps
        )

        # TODO: If 'self.audio_cache' is None, omit
        for frame in get_audio_frames_at_t(
            cache = self.audio_cache,
            t = t,
            video_fps = video_fps,
            do_apply_filters = do_apply_filters
        ):
            yield frame

    def get_audio_frames(
        self,
        start: Union[int, float, Fraction] = 0.0,
        end: Union[int, float, Fraction, None] = None,
        do_apply_filters: bool = True
    ):
        """
        Iterator to get the audio frames in between
        the provided 'start' and 'end' time moments.

        This iterator will have no elements if
        there are no audio frames in the time 
        interval between the provided 'start' and
        'end'.

        This iterator will have no elements if
        there are no audio frames in the time
        interval defined by the given 'start' and
        'end'.
        """
        for frame in get_frames(
            cache = self.audio_cache,
            start = start,
            end = end,
            do_apply_filters = do_apply_filters
        ):
            yield frame

class AudioReader(_Reader):
    """
    Class to read video files with the PyAv (av)
    library that uses ffmpeg on the background.
    """

    @property
    def has_audio(
        self
    ) -> bool:
        """
        Flag to indicate if there is an audio stream
        or not.
        """
        return self.audio_stream is not None

    @property
    def audio_codec_name(
        self
    ) -> str:
        """
        Get the name of the audio codec.
        """
        return (
            self.audio_stream.codec_context.name
            if self.has_audio else
            None
        )

    @property
    def audio_fps(
        self
    ) -> Union[int, None]:
        """
        The fps of the audio.
        """
        return (
            self.audio_stream.rate
            if self.has_audio else
            None
        )
    
    @property
    def audio_codec_name(
        self
    ) -> Union[str, None]:
        """
        Get the name of the audio codec. Can be None
        if the file we are reading is a video file.
        """
        return (
            self.audio_stream.codec_context.name
            if self.has_audio else
            None
        )
    
    @property
    def audio_layout(
        self
    ) -> Union[str, None]:
        """
        Get the audio layout.
        """
        return (
            self.audio_stream.codec_context.layout
            if self.has_audio else
            None
        )
    
    @property
    def audio_format(
        self
    ) -> Union[str, None]:
        """
        Get the audio format.
        """
        return (
            self.audio_stream.codec_context.format
            if self.has_audio else
            None
        )
    
    @property
    def audio_time_base(
        self
    ) -> Union[Fraction, None]:
        """
        The time base of the audio.
        """
        return (
            self.audio_stream.time_base
            if self.has_audio else
            None
        )
    
    @property
    def audio_duration(
        self
    ) -> Union[float, None]:
        """
        The duration of the audio.
        """
        # TODO: What to do in the case we have
        # audio stream but not 'duration' 
        # attribute (?)
        return (
            float(self.audio_stream.duration * self.audio_stream.time_base)
            if (
                self.has_audio and
                self.audio_stream.duration
            ) else
            None
        )
    
    @property
    def audio_samples_per_frame(
        self
    ) -> int:
        """
        The amount of audio samples we obtain for each
        audio frame.
        """
        return (
            self.audio_stream.codec_context.frame_size
            if self.has_audio else
            None
        )
    
    # Any property related to audio has to
    # start with 'audio_property_name'

    def __init__(
        self,
        filename: str,
        audio_filters: list[GraphFilter] = []
    ):
        _Reader.__init__(
            self,
            filename = filename,
            video_filters = [],
            audio_filters = audio_filters
        )

        self.audio_cache: AudioFrameCache = None
        """
        The audio frame cache system to optimize
        the way we access to the frames.
        """

        # TODO: Maybe we can read the first 
        # frame, store it and reset, so we have
        # it in memory since the first moment.
        # We should do it here because if we
        # iterate in some moment and then we
        # want to obtain it... it will be 
        # difficult.
        # Lets load the variables
        self.reset()

    def get_audio_frame_at_t(
        self,
        t: Union[int, float, Fraction],
        do_apply_filters: bool = True
    ) -> Union[AudioFrame, None]:
        """
        Get the audio frame with the given 't' time
        moment, using the audio cache system.
        
        If 't' is an invalid moment (out of the time
        limits) this method will return None.
        """
        return self.audio_cache.get_frame(
            t = t,
            do_apply_filters = do_apply_filters
        )
    
    def get_audio_frames_at_t(
        self,
        t: Union[int, float, Fraction],
        video_fps: Union[int, float, Fraction],
        do_apply_filters: bool = True
    ):
        """
        Get the sequence of audio frames for the 
        given video 't' time moment, using the
        audio cache system and the provided
        'video_fps' to be able to claculate the
        time range.

        This is useful when we want to write a
        video frame with its audio, so we obtain
        all the audio frames associated to it
        (remember that a video frame is associated
        with more than 1 audio frame).

        This iterator will have no elements if
        there are no audio frames at the provided
        't' time moment.
        """
        for frame in get_audio_frames_at_t(
            cache = self.audio_cache,
            t = t,
            video_fps = video_fps,
            do_apply_filters = do_apply_filters
        ):
            yield frame

    def get_audio_frames(
        self,
        start: Union[int, float, Fraction] = 0.0,
        end: Union[int, float, Fraction, None] = None,
        do_apply_filters: bool = True
    ):
        """
        Iterator to get the audio frames in between
        the provided 'start' and 'end' time moments.
        
        This iterator will have no elements if
        there are no audio frames at the provided
        't' time moment.
        """
        for frame in get_frames(
            cache = self.audio_cache,
            start = start,
            end = end,
            do_apply_filters = do_apply_filters
        ):
            yield frame

def get_frames(
    cache: Union[AudioFrameCache, VideoFrameCache],
    start: Union[int, float, Fraction] = 0.0,
    end: Union[int, float, Fraction, None] = None,
    do_apply_filters: bool = True
):
    """
    Iterator to get the frames in the time range
    defined by the given 'start' and 'end' time
    moments.

    This iterator can be empty if no frames in
    the time interval between the given 'start'
    and 'end' time moments.
    """
    for frame in cache.get_frames(
        start = start,
        end = end,
        do_apply_filters = do_apply_filters
    ):
        yield frame

def get_audio_frames_at_t(
    cache: AudioFrameCache,
    t: Union[int, float, Fraction],
    video_fps: Union[int, float, Fraction],
    do_apply_filters: bool = True
):
    """
    This iterator can be empty if no frames in
    the time interval between the given 'start'
    and 'end' time moments.
    """
    thandler = THandler(video_fps)
    t_start = thandler.t.truncated(t)
    t_end = thandler.t.next(t, 1, do_truncate = True)

    # We want all the audios that must be played
    # during the video frame that starts in the
    # 't' time moment
    for frame in get_frames(
        cache = cache,
        start = t_start,
        end = t_end,
        do_apply_filters = do_apply_filters
    ):
        yield frame
