
from yta_video_pyav.reader.cache import FrameCache
from yta_video_pyav.reader.filter.utils import get_filter_graph
from yta_video_pyav.reader.filter.dataclass import GraphFilter
from yta_video_frame_time.t_fraction import THandler
from yta_validation.parameter import ParameterValidator
from av.container import InputContainer
from av.video.stream import VideoStream
from av.video.frame import VideoFrame
from quicktions import Fraction
from typing import Union


class VideoFrameCache(FrameCache):
    """
    Cache for the video frames.
    """

    @property
    def fps(
        self
    ) -> Union[Fraction, None]:
        """
        The frames per second.
        """
        return self.stream.average_rate

    @property
    def frame_duration(
        self
    ) -> int:
        """
        The frame duration in ticks, which is the
        minimum amount of time, 1 / time_base.
        """
        return self.stream.duration / self.stream.frames
    
    def __init__(
        self,
        container: InputContainer,
        stream: VideoStream,
        # TODO: Rename to 'cache_size' maybe (?)
        size: Union[int, None] = None,
        filters: list[GraphFilter] = []
    ):
        ParameterValidator.validate_mandatory_instance_of('stream', stream, VideoStream)

        super().__init__(
            container = container,
            stream = stream,
            size = size,
            filters = filters
        )

        self._t_handler: THandler = THandler(self.fps, self.time_base)
        """
        Internal THandler instance to make time and
        pts conversions.
        """

    def get_frame(
        self,
        t: Union[int, float, Fraction]
    ) -> Union[VideoFrame, None]:
        """
        Get the video frame that is in the 't'
        time moment provided.
        """
        t_start = self._t_handler.t.truncated(t)
        t_end = self._t_handler.t.next(t, 1, do_truncate = True)
        
        for frame in self.get_frames(t_start, t_end):
            print(f'> [VIDEO] Getting video frame from {str(float(t))}. FPS: {str(self.fps)}. Obtaining frame from [{str(float(t_start))}, {str(float(t_end))}) time interval.')
            return frame

    def get_frames(
        self,
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction]
    ):
        """
        Get all the frames in the range between
        the provided 'start' and 'end' time in
        seconds.

        This method is an iterator that yields
        the frame, and can be empty if no frames
        in the time interval between the given
        'start' and 'end' time moments.
        """
        # TODO: Validate 'start' and 'end' are mandatory
        # positive numbers
        # Make sure the 'start' and 'end' time moments
        # provided are truncated values based on the
        # stream time base
        start = self._t_handler.t.truncated(start)
        end = self._t_handler.t.truncated(end)

        if end <= start:
            raise Exception(f'The time range start:{str(float(start))} - end:{str(float(end))}) is not valid.')
        
        key_frame_pts = self._get_nearest_keyframe_pts(start / self.time_base)

        # Filters to apply, that can be None
        filter_graph = (
            get_filter_graph(
                stream = self.stream,
                filters = self.filters
            )
            if self.has_filters else
            None
        )

        if (
            self._last_packet_accessed is None or
            self._last_packet_accessed.pts != key_frame_pts
        ):
            self._seek(key_frame_pts)

        for packet in self.container.demux(self.stream):
            if packet.pts is None:
                continue

            self._last_packet_accessed = packet

            for frame in packet.decode():
                if frame.pts is None:
                    continue

                # We store all the frames in cache
                self._store_frame_in_cache(frame)
                
                current_frame_start_t = self._t_handler.pts.to_t(frame.pts, do_truncate = True)
                
                # We want the range [start, end)
                if start <= current_frame_start_t < end:
                    # Apply filter only if needed
                    if filter_graph is not None:
                        filter_graph.push(frame)
                        frame = filter_graph.pull()

                    yield frame

                if current_frame_start_t >= end:
                    return