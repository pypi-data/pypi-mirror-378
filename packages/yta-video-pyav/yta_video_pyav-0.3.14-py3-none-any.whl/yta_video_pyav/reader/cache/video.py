
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
        cache_size: Union[int, None] = None,
        filters: list[GraphFilter] = []
    ):
        ParameterValidator.validate_mandatory_instance_of('stream', stream, VideoStream)

        super().__init__(
            container = container,
            stream = stream,
            cache_size = cache_size,
            filters = filters
        )

        self._t_handler: THandler = THandler(self.fps, self.time_base)
        """
        Internal THandler instance to make time and
        pts conversions.
        """

    def get_frame(
        self,
        t: Union[int, float, Fraction],
        do_apply_filters: bool = True
    ) -> Union[VideoFrame, None]:
        """
        Get the video frame that is in the 't'
        time moment provided.
        """
        t_start = self._t_handler.t.truncated(t)
        t_end = self._t_handler.t.next(t, 1, do_truncate = True)
        
        for frame in self.get_frames(
            start = t_start,
            end = t_end,
            do_apply_filters = do_apply_filters
        ):
            print(f'> [VIDEO] Getting video frame from {str(float(t))}. FPS: {str(self.fps)}. Obtaining frame from [{str(float(t_start))}, {str(float(t_end))}) time interval.')
            return frame

    def get_frames(
        self,
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction],
        do_apply_filters: bool = True
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
        ParameterValidator.validate_mandatory_positive_number('start', start, do_include_zero = True)
        ParameterValidator.validate_mandatory_positive_number('end', end, do_include_zero = False)

        # Make sure the 'start' and 'end' time moments
        # provided are truncated values based on the
        # stream time base
        t_start = self._t_handler.t.truncated(start)
        t_end = self._t_handler.t.truncated(end)

        if t_end <= t_start:
            raise Exception(f'The time range start:{str(float(t_start))} - end:{str(float(t_end))}) is not valid.')
        
        # Filters to apply, that can be None
        filter_graph = (
            get_filter_graph(
                stream = self.stream,
                filters = self.filters
            )
            if (
                self.has_filters and
                do_apply_filters
            ) else
            None
        )

        # Relocate to the start to make
        # sure we will be able to read
        # the frames we are looking for
        # TODO: Is this optimal (?)
        seek_pts = self._t_handler.pts.from_t(t_start)
        self._seek(seek_pts)

        """
        When we decode the frames we can have
        frames remaining in the buffer so we
        need to make a final flush also.
        """

        # First iteration to obtain the frames
        for packet in self.container.demux(self.stream):
            if packet.pts is None:
                continue
            
            for frame in packet.decode():
                result = self._process_frame(frame, t_start, t_end, filter_graph)

                if result == 'STOP':
                    return
                
                if result is not None:
                    yield result

        # Final flush to obtain the remaining frames
        for frame in self.stream.decode():
            result = self._process_frame(frame, t_start, t_end, filter_graph)

            if result == 'STOP':
                return
            
            if result is not None:
                yield result

    def _process_frame(
        self,
        frame: VideoFrame,
        t_start: Union[int, float, Fraction],
        t_end: Union[int, float, Fraction],
        filter_graph: 'Graph'
    ):
        """
        *For internal use only*

        Check if the frame must be considered and,
        if needed, apply the filters and return 
        that frame to the main code flow.
        """
        if frame.pts is None:
            return None

        current_frame_start_t = self._t_handler.pts.to_t(
            pts = self._get_pts(frame.pts),
            do_truncate = True
        )

        # We want the range [t_start, t_end)
        if t_start <= current_frame_start_t < t_end:
            if filter_graph is not None:
                filter_graph.push(frame)
                frame = filter_graph.pull()

            return frame

        if current_frame_start_t >= t_end:
            return 'STOP'

        return None