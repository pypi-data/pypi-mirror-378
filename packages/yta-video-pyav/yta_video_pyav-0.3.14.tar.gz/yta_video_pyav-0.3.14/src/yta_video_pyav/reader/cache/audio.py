
from yta_video_pyav.reader.cache import FrameCache
from yta_video_pyav.reader.filter.dataclass import GraphFilter
from yta_video_pyav.reader.filter.utils import get_filter_graph
from yta_video_pyav.reader.cache.utils import trim_audio_frame
from yta_video_frame_time.t_fraction import THandler, get_audio_frame_duration
from yta_validation.parameter import ParameterValidator
from av.container import InputContainer
from av.audio.stream import AudioStream
from av.audio.frame import AudioFrame
from quicktions import Fraction
from typing import Union


class AudioFrameCache(FrameCache):
    """
    Cache for the audio frames.
    """

    @property
    def fps(
        self
    ) -> Union[Fraction, int]:
        """
        The frames per second.

        The formula:
        - `stream.rate`
        """
        return self.stream.rate

    def __init__(
        self,
        container: InputContainer,
        stream: AudioStream,
        cache_size: Union[int, None] = None,
        filters: list[GraphFilter] = []
    ):
        ParameterValidator.validate_mandatory_instance_of('stream', stream, AudioStream)

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
    ) -> Union[AudioFrame, None]:
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
            return frame

    def get_frames(
        self,
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction],
        do_apply_filters: bool = True
    ):
        """
        Get all the audio frames in the range
        between the provided 'start' and 'end'
        time (in seconds).

        This method is an iterator that yields
        the frame and can be empty if no frames
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
        
        # Prepare this to apply the filters if needed
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

        # Relocate to the start to be able to read
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
        frame: AudioFrame,
        t_start: Union[int, float, Fraction],
        t_end: Union[int, float, Fraction],
        filter_graph: 'Graph'
    ):
        """
        *For internal use only*
        """
        if frame.pts is None:
            return None

        current_frame_start_t = self._t_handler.pts.to_t(
            pts = self._get_pts(frame.pts),
            do_truncate = True
        )
        duration = get_audio_frame_duration(frame.samples, self.fps)
        current_frame_end_t = Fraction(current_frame_start_t + duration)

        # For the next comments imagine we are looking
        # for the [1.0, 2.0) audio time range

        # Previous frame and nothing is inside
        if current_frame_end_t <= t_start:
            # From 0.25 to 1.0 => nothing
            return None
        
        # We finished, nothing is inside and its after
        if current_frame_start_t >= t_end:
            # From 2.0 to 2.75 => finished
            return 'STOP'
        
        """
        If we need audio from 1 to 2, audio is:
        - from 0 to 0.75    (Not included, omit)
        - from 0.5 to 1.5   (Included, take 1.0 to 1.5)
        - from 0.5 to 2.5   (Included, take 1.0 to 2.0)
        - from 1.25 to 1.5  (Included, take 1.25 to 1.5)
        - from 1.25 to 2.5  (Included, take 1.25 to 2.0)
        - from 2.5 to 3.5   (Not included, omit)
        """

        # Here below, at least a part is inside
        if current_frame_start_t < t_start < current_frame_end_t:
            # A part at the end is included
            end_time = (
                # From 0.5 to 1.5 => take 1.0 to 1.5
                current_frame_end_t
                if current_frame_end_t <= t_end else
                # From 0.5 to 2.5 => take 1.0 to 2.0
                t_end
            )

            frame = trim_audio_frame(
                frame = frame,
                start = t_start,
                end = end_time,
                time_base = self.time_base
            )
        # Here below, it starts inside the range
        elif t_start <= current_frame_start_t < t_end:
            end_time = (
                # From 1.25 to 1.5 => take 1.25 to 1.5
                current_frame_end_t
                if current_frame_end_t <= t_end else
                # From 1.25 to 2.5 => take 1.25 to 2.0
                t_end
            )
            # A part at the begining is included
            frame = trim_audio_frame(
                frame = frame,
                start = current_frame_start_t,
                end = end_time,
                time_base = self.time_base
            )

        # Apply filter only if needed
        if filter_graph is not None:
            filter_graph.push(frame)
            frame = filter_graph.pull()

        # If the whole frame is in just pass it
        return frame
