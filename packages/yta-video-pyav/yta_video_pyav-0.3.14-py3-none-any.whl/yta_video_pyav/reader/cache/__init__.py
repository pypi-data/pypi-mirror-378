"""
The pyav container stores the information based
on the packets timestamps (called 'pts'). Some
of the packets are considered key_frames because
they include those key frames.

Also, this library uses those key frames to start
decodifying from there to the next one, obtaining
all the frames in between able to be read and
modified.

This cache system will look for the range of 
frames that belong to the key frame related to the
frame we are requesting in the moment, keeping in
memory all those frames to be handled fast. It
will remove the old frames if needed to use only
the 'size' we set when creating it.

A stream can have 'fps = 60' but use another
different time base that make the pts values go 0,
 256, 512... for example. The 'time_base' is the
only accurate way to obtain the pts.

Feel free to move this explanation to other
place, its about the duration.

The stream 'duration' parameter is measured
on ticks, the amount of ticks that the
stream lasts. Here below is an example:

- Duration raw: 529200
- Time base: 1/44100
- Duration (seconds): 12.0
"""
from yta_video_pyav.reader.filter.dataclass import GraphFilter
from yta_video_pyav.settings import Settings
from yta_validation.parameter import ParameterValidator
from av.container import InputContainer
from av.video.stream import VideoStream
from av.audio.stream import AudioStream
from av.video.frame import VideoFrame
from av.audio.frame import AudioFrame
from av.packet import Packet
from quicktions import Fraction
from collections import OrderedDict
from typing import Union
from abc import abstractmethod, ABC

import numpy as np
import math


class FrameCache(ABC):
    """
    Class to manage the frames cache of a video
    or audio.
    """

    @property
    @abstractmethod
    def fps(
        self
    ) -> Union[int, Fraction, None]:
        """
        The frames per second.
        """
        pass
    
    @property
    def time_base(
        self
    ) -> Union[Fraction, None]:
        """
        The time base of the stream.
        """
        return self.stream.time_base
    
    @property
    def has_filters(
        self
    ) -> bool:
        """
        A flag to indicate if the cache has filters
        to be applied or not.
        """
        return len(self.filters) > 0

    def __init__(
        self,
        container: InputContainer,
        stream: Union[VideoStream, AudioStream],
        cache_size: Union[int, None] = None,
        filters: list[GraphFilter] = []
    ):
        ParameterValidator.validate_mandatory_instance_of('container', container, InputContainer)
        ParameterValidator.validate_mandatory_instance_of('stream', stream, [VideoStream, AudioStream])
        ParameterValidator.validate_number_between('cache_size', cache_size, Settings.MIN_FRAME_CACHE_SIZE.value, Settings.MAX_FRAME_CACHE_SIZE.value)

        self.container: InputContainer = container
        """
        The pyav container.
        """
        self.stream: Union[VideoStream, AudioStream] = stream
        """
        The pyav stream.
        """
        
        self.cache: OrderedDict = OrderedDict()
        """
        The cache ordered dictionary.
        """
        self.key_frames_pts: list[int] = []
        """
        The list that contains the timestamps of the
        key frame packets, ordered from begining to
        end.
        """
        self.cache_size: int = cache_size
        """
        The size of the cache.
        """
        self.filters: list[GraphFilter] = filters
        """
        The filters we want to apply to each frame we
        read.
        """

        self._last_packet_accessed: Union[Packet, None] = None
        """
        The last packet that has been accessed
        """
        self._offset_pts: Union[int, None] = None
        """
        The 'pts' value of the first decoded frame,
        that must be substracted from any pts to 
        obtain the real value (we want to consider
        0 as the first one but it can be a greater
        value, it depends on the way the video/audio
        source was decoded).
        """

        self._prepare()

    def _prepare(
        self
    ) -> 'FrameCache':
        """
        Prepare the cache by reading the pts of the
        first decoded frame so we can access correctly
        to all the frames, and by storing the key 
        frames pts values.
        """
        self._seek(0)

        # Index key frames and save offset pts
        for packet in self.container.demux(self.stream):
            if packet.pts is None:
                continue

            if packet.is_keyframe:
                self.key_frames_pts.append(packet.pts)

            if self._offset_pts is None:
                for frame in packet.decode():
                    if frame.pts is not None:
                        self._offset_pts = frame.pts
                        break

        """
        The cache size will be auto-calculated to
        use the amount of frames of the biggest
        interval of frames that belongs to a key
        frame, or a value by default
        """
        # TODO: By now I'm not using the cache
        # TODO: Careful if this is too big
        # Intervals, but in number of frames
        intervals = np.diff(
            # Intervals of time between keyframes
            np.array(self.key_frames_pts) * self.time_base
        ) * self.fps
        
        self.cache_size = (
            math.ceil(np.max(intervals))
            if intervals.size > 0 else
            getattr(self, 'cache_size', Settings.DEFAULT_FRAME_CACHE_SIZE.value)
        )

        self._seek(0)

    def _get_nearest_keyframe_pts(
        self,
        pts: int
    ):
        """
        Get the fps of the keyframe that is the
        nearest to the provided 'pts'. Useful to
        seek and start decoding frames from that
        keyframe.

        The pts values stored here are the original
        ones and the offset has not been
        substracted. The 'pts' provided has to be
        the original one (do not substract the 
        offset).
        """
        return max(
            (
                key_frame_pts
                for key_frame_pts in self.key_frames_pts
                if key_frame_pts <= pts
            ),
            # If no key frames, just 0
            default = 0
        )

    # TODO: This is not working well by now
    def _store_frame_in_cache(
        self,
        frame: Union[VideoFrame, AudioFrame]
    ) -> Union[VideoFrame, AudioFrame]:
        """
        Store the provided 'frame' in cache if it
        is not on it, removing the first item of
        the cache if full.
        """
        if frame.pts not in self.cache:
            self.cache[frame.pts] = frame

            # Clean cache if full
            if len(self.cache) > self.size:
                self.cache.popitem(last = False)

        return frame
    
    def _get_pts(
        self,
        pts: int
    ) -> int:
        """
        Get the real pts value according to the
        offset we have extracted from the first
        frame.

        The 'pts' value returned must be used to
        calculate the real time moment. Some 
        videos can have the first frame with
        pts=256 (or other value greater than 0),
        but being the first frame it should be
        (at least for us) the pts=0. Thats why
        this method exist, to substract that
        offset and obtain the 'pts' value that
        is valid for us.

        The formula:
        - `pts - self._offset_pts`
        """
        return pts - self._offset_pts
    
    def _seek(
        self,
        pts: int
    ):
        """
        Seek to the given 'pts' only if it is not
        the next 'pts' to the last read, and it 
        will also apply a pad to avoid problems
        when reading audio frames.
        """

        """
        I found that it is recommended to
        read ~100ms before the pts we want to
        actually read so we obtain the frames
        clean (this is important in audio).
        This solves a problem I had related
        to some artifacts on the audio when
        trimming exactly without this pad.
        """
        # TODO: Maybe we can differentiate
        # between audio and video and apply
        # the pad only for audio, but I think
        # this is also ok
        pts_pad = int(0.1 / self.time_base)
        self.container.seek(
            offset = max(0, pts - pts_pad),
            stream = self.stream
        )

    def set_filters(
        self,
        filters: list[GraphFilter] = []
    ) -> 'FrameCache':
        """
        Set the provided 'filters' as the new
        filters to be applied, replacing the
        previous ones if existing.
        """
        self.filters = filters

        return self
    
    def clear(
        self
    ) -> 'VideoFrameCache':
        """
        Clear the cache by removing all the items.
        """
        self.cache.clear()

        return self

    def get_frame(
        self,
        t: Union[int, float, Fraction]
    ) -> Union[VideoFrame, AudioFrame]:
        """
        Get the single frame that is in the 't'
        time moment provided.
        """
        for frame in self.get_frames(t):
            return frame
        
    @abstractmethod
    def get_frames(
        self,
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction]
    ):
        pass


"""
There is a way of editing videos being
able to arbitrary access to frames, that
is transforming the source videos to
intra-frame videos. This is a ffmpeg
command that can do it:

- `ffmpeg -i input.mp4 -c:v libx264 -x264opts keyint=1 -preset fast -crf 18 -c:a copy output_intra.mp4`

Once you have the 'output_intra.mp4',
each packet can decodify its frame 
depending not on the previous one, being
able to seek and jump easy.

There are 3 type of video codifications,
the I-frame (intra-coded), in which any
frame can be decoded by itself, P-frame
(predicted), that need one or more 
previous frames to be decoded, and 
B-frame (bidirectional predicted), that
needs previous and future frames.
"""