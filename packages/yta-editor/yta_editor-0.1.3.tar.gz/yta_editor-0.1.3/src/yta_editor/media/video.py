from yta_editor.media.abstract import _Media
from yta_editor.sources.abstract import _VideoSource
from yta_editor.sources.video import VideoFileSource, VideoImageSource, VideoColorSource, VideoNumpySource
from yta_editor.decorators import with_t_adjusted_to_media
from yta_editor.utils import apply_audio_effects_to_frame_at_t, apply_video_effects_to_frame_at_t
from yta_video_pyav.reader.filter.dataclass import GraphFilter
from yta_video_opengl.nodes import TimedNode
from av.video.frame import VideoFrame
from yta_validation.parameter import ParameterValidator
from quicktions import Fraction
from typing import Union

    
class _VideoMedia(_Media):

    @property
    def size(
        self
    ) -> tuple[int, int]:
        """
        The size of the video frame, expressed
        as (width, height).
        """
        return self.source.size

    def __init__(
        self,
        source: _VideoSource,
        start: Union[int, float, Fraction] = 0.0,
        end: Union[int, float, Fraction, None] = None,
    ):
        super().__init__(
            source = source,
            start = start,
            end = end
        )

    def add_effect(
        self,
        effect: TimedNode
    ) -> 'Video':
        """
        Add the provided 'effect' to the video.
        """
        ParameterValidator.validate_mandatory_instance_of('effect', effect, 'TimedNode')

        self._effects.add_effect(effect)
        
        return self
    
    @with_t_adjusted_to_media
    def get_video_frame_at_t(
        self,
        t: Union[int, float, Fraction]
    ) -> Union[VideoFrame, None]:
        """
        Get the video frame with the given 't' time
        moment, using the video cache system.
        """
        print(f'Getting frame from {str(float(t + self.start))} that is actually {str(float(t))}')
        
        frame = self.source.get_video_frame_at_t(t)

        return (
            apply_video_effects_to_frame_at_t(
                effects_stack = self._effects,
                frame = frame,
                t = t
            )
            if frame is not None else
            None
        )
    
    @with_t_adjusted_to_media
    def get_audio_frames_at_t(
        self,
        t: Union[int, float, Fraction],
        video_fps: Union[int, float, Fraction, None] = None
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
        """
        video_fps = (
            self.fps
            if video_fps is None else
            video_fps
        )

        print(f'Getting audio frames from {str(float(t + self.start))} that is actually {str(float(t))}')
        for frame in self.source.get_audio_frames_at_t(
            t = t,
            video_fps = video_fps
        ):
            yield apply_audio_effects_to_frame_at_t(
                effects_stack = self._effects,
                frame = frame,
                t = t
            )
    
class VideoFileMedia(_VideoMedia):
    """
    A video media that is read from a video
    file and can be subclipped to a specific
    time range.
    """

    @property
    def copy(
        self
    ) -> 'VideoFileMedia':
        """
        Get a copy of this instance with the same
        source, time range and effects.
        """
        copy = VideoFileMedia._init_with_source(
            source = self.source,
            start = self.start,
            end = self.end
        )

        copy._effects = self._effects.copy

        return copy

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
        return self.source.ticks_per_frame
    
    @property
    def duration(
        self
    ) -> Fraction:
        """
        The duration of the video, that can be
        shorter than the video file source
        duration if the user requested for it.

        The formula:
        - `self.end - self.start`
        """
        return self.end - self.start
    
    @property
    def number_of_frames(
        self
    ) -> Union[int, None]:
        """
        The number of frames of the video.
        """
        return self.source.number_of_frames
    
    @property
    def fps(
        self
    ) -> Union[Fraction, None]:
        """
        The frames per second of the video.
        """
        return self.source.fps
    
    @property
    def audio_fps(
        self
    ) -> Union[int, None]:
        """
        The frames per second of the audio.
        """
        return self.source.audio_fps
    
    @property
    def codec_name(
        self
    ) -> Union[str, None]:
        """
        The name of the codec.
        """
        return self.source.codec_name
    
    @property
    def pixel_format(
        self
    ) -> Union[str, None]:
        """
        The pixel format.
        """
        return self.source.pixel_format

    @property
    def size(
        self
    ) -> tuple[int, int]:
        """
        The size of the video frames expressed 
        like (width, height).
        """
        return self.source.size
    
    @property
    def width(
        self
    ) -> int:
        """
        The width of the video frames in pixels.
        """
        return self.size[0]
    
    @property
    def height(
        self
    ) -> int:
        """
        The height of the video frames in pixels.
        """
        return self.size[1]
    
    @property
    def time_base(
        self
    ) -> Union[Fraction, None]:
        """
        The time base of the video.
        """
        return self.source.time_base
    
    @property
    def audio_time_base(
        self
    ) -> Union[Fraction, None]:
        """
        The time base of the audio.
        """
        return self.source.audio_time_base

    def __init__(
        self,
        filename: str,
        start: Union[int, float, Fraction] = 0.0,
        end: Union[int, float, Fraction, None] = None,
        # These are ffmpeg filters
        video_filters: list[GraphFilter] = [],
        audio_filters: list[GraphFilter] = []
    ):
        super().__init__(
            source = VideoFileSource(
                filename = filename,
                video_filters = video_filters,
                audio_filters = audio_filters
            ),
            start = start,
            end = end
        )

    def add_video_filter(
        self,
        filter: GraphFilter
    ) -> 'VideoFileMedia':
        """
        Add a video filter to the list of filters
        to apply.
        """
        self.source.add_video_filter(filter)

        return self
    
    def add_audio_filter(
        self,
        filter: GraphFilter
    ) -> 'VideoFileMedia':
        """
        Add an audio filter to the list of filters
        to apply.
        """
        self.source.add_audio_filter(filter)

        return self

class VideoImageMedia(_VideoMedia):
    """
    A video media that is made by an static
    image file.
    """

    @property
    def copy(
        self
    ) -> 'VideoImageMedia':
        """
        Get a copy of this instance with the same
        source, time range and effects.
        """
        copy = VideoImageMedia._init_with_source(
            source = self.source,
            start = self.start,
            end = self.end
        )

        copy._effects = self._effects.copy

        return copy

    @property
    def filename(
        self
    ) -> str:
        """
        The filename of the original image.
        """
        return self.source.filename

    # TODO: Maybe rename this property (?)
    @property
    def do_include_alpha(
        self
    ) -> bool:
        """
        The internal flag to indicate if we
        want to consider the alpha channel or
        not.
        """
        return self.source._do_include_alpha

    def __init__(
        self,
        filename: str,
        duration: Union[int, float, Fraction],
        do_include_alpha: bool = True,
        size: Union[tuple[int, int], None] = None,
        # Need this to generate the silent audio frames
        audio_fps: int = 44_100,
        audio_samples_per_frame: int = 1024,
    ):
        """
        TODO: Maybe force size provided as parameter (?)
        """
        # We need to dynamically set the frame format
        # to accept (or not) the alpha channel
        frame_format = (
            'rgba'
            if do_include_alpha else
            'rgb24'
        )

        super().__init__(
            source = VideoImageSource(
                filename = filename,
                do_include_alpha = do_include_alpha,
                frame_format = frame_format,
                size = size,
                audio_fps = audio_fps,
                audio_samples_per_frame = audio_samples_per_frame
            ),
            start = 0,
            end = duration
        )

class VideoColorMedia(_VideoMedia):
    """
    A video media that is made with a static
    uniform color frame.
    """

    @property
    def copy(
        self
    ) -> 'VideoColorMedia':
        """
        Get a copy of this instance with the same
        source, time range and effects.
        """
        copy = VideoColorMedia._init_with_source(
            source = self.source,
            start = self.start,
            end = self.end
        )

        copy._effects = self._effects.copy

        return copy
    
    @property
    def color(
        self
        # TODO: Apply format
    ) -> any:
        """
        The color that will be used to make the
        frame that will be played its whole
        duration.
        """
        return self.source._color
    
    @property
    def size(
        self
    ) -> tuple[int, int]:
        """
        The size of the media frame.
        """
        return self.source.size

    def __init__(
        self,
        # TODO: Apply format
        color: any,
        duration: Union[int, float, Fraction],
        size: tuple[int, int] = (1920, 1080),
        transparency: Union[float, None] = 0.0,
        # TODO: Should we accept 'frame_format' (?)
        #frame_format: str = 'rgba',
        # Need this to generate the silent audio frames
        audio_fps: int = 44_100,
        audio_samples_per_frame: int = 1024,
    ):
        """
        TODO: The 'color' must be handled, by now
        we don't care about your argument x).
        """
        frame_format = (
            'rgba'
            if transparency is not None else
            'rgb24'
        )

        super().__init__(
            source = VideoColorSource(
                color = color,
                size = size,
                frame_format = frame_format,
                transparency = transparency,
                audio_fps = audio_fps,
                audio_samples_per_frame = audio_samples_per_frame
            ),
            start = 0,
            end = duration
        )

# TODO: Create 'VideoNumpyMedia'