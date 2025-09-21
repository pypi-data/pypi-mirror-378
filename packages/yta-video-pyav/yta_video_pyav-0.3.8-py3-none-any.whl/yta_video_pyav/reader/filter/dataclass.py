from yta_validation.parameter import ParameterValidator
from dataclasses import dataclass
from typing import Union


@dataclass
class GraphFilter:
    """
    A dataclass to hold the information about
    a graph filter we want to apply in our 
    stream decoders.
    """

    def __init__(
        self,
        name: str,
        args: Union[str, None]
    ):
        ParameterValidator.validate_mandatory_string('name', name, do_accept_empty = False)
        ParameterValidator.validate_string('args', args, do_accept_empty = False)

        self.name: str = name
        """
        The name of the filter we want to apply.
        """
        self.args: Union[str, None] = args
        """
        The arguments we want to apply on the filter,
        if we want to apply some (if no args, set
        None).
        """

    def to_str(
        self
    ):
        """
        The filter but as a string.

        Example of commands below:
        - `{name}:{args}`
        - `{name}` (if args is None)
        """
        return (
            f'{self.name}:{self.args}'
            if self.args is not None else
            f'{self.name}'
        )

class _VideoGraphFilters:
    """
    Class to warp the video GraphFilters.
    """

    # Geometry below
    @staticmethod
    def scale(
        width: int,
        height: int
    ) -> GraphFilter:
        """
        Graph filter to scale the video.

        The command:
        - `scale={width}:{height}`
        """
        return GraphFilter(
            name = 'scale',
            args = f'{str(width)}:{str(height)}'
        )
    
    @staticmethod
    def crop(
        x: int,
        y: int,
        width: int,
        height: int
    ) -> GraphFilter:
        """
        Graph filter to crop the video.

        The command:
        - `crop={weight}:{height}:{x}:{y}`
        """
        return GraphFilter(
            name = 'scale',
            args = f'{str(width)}:{str(height)}:{str(x)}:{str(y)}'
        )
    
    @staticmethod
    def pad(
        x: int,
        y: int,
        width: int,
        height: int,
        # TODO: What about the color (?)
        color: str
    ) -> GraphFilter:
        """
        Add border or margins (?)

        The command:
        - `pad={width}:{height}:{x}:{y}:{color}`

        TODO: I don't know how it works
        """
        # pad=w:h:x:y:color
        return GraphFilter(
            name = 'pad',
            args = f'{str(width)}:{str(height)}:{str(x)}:{str(y)}:{color}'
        )
    
    @staticmethod
    def horizontal_flip(
    ) -> GraphFilter:
        """
        Flip the video frame horizontally.

        The command:
        - `hflip`
        """
        return GraphFilter(
            name = 'hflip',
            args = None
        )
    
    @staticmethod
    def vertical_flip(
    ) -> GraphFilter:
        """
        Flip the video frame vertically.

        The command:
        - `vflip`
        """
        return GraphFilter(
            name = 'vflip',
            args = None
        )
    
    @staticmethod
    def transpose(
        times: int
    ) -> GraphFilter:
        """
        Rotate the video frame 90 degrees to the
        right the number of 'times' provided.

        The 'times' values must be:
        - 0 for no rotation
        - 1 for 90 degrees rotation
        - 2 for 180 degrees rotation
        - 3 for 270 degrees rotation

        # TODO: Am I sure of this above (?)
        """
        times %= 4

        return GraphFilter(
            name = 'transpose',
            args = f'{str(times)}'
        )
    
    @staticmethod
    def rotate(
        degrees: int
    ) -> GraphFilter:
        """
        Rotate the video frame.

        The command:
        - `rotate={degrees}`
        """
        return GraphFilter(
            name = 'rotate',
            args = f'{str(degrees)}'
        )
    
    # Enfoque y suavizado
    @staticmethod
    def unsharp(
    ) -> GraphFilter:
        """
        Highlight the edges.

        The command:
        - `unsharp`
        """
        return GraphFilter(
            name = 'unsharp',
            args = None
        )
    
    # TODO: This one doesn't exist in my distribution
    # @staticmethod
    # def smartblur(
    # ) -> GraphFilter:
    #     """
    #     Intelligent blur.

    #     The command:
    #     - `smartblur`
    #     """
    #     return GraphFilter(
    #         name = 'smartblur',
    #         args = None
    #     )

    @staticmethod
    def gaussianblur(
        # TODO: Make 'sigma' a parameter
        sigma: int = 2
    ) -> GraphFilter:
        """
        Gaussian blur.

        The command:
        - `gblur=sigma={sigma}`
        """
        return GraphFilter(
            name = 'gblur',
            args = f'sigma={str(sigma)}'
        )
    
    # TODO: This one doesn't exist in my distribution
    # @staticmethod
    # def boxblur(
    #     sigma: int = 2
    # ) -> GraphFilter:
    #     """
    #     Box blur.

    #     The command:
    #     - `boxblur={sigma}:1`
    #     """
    #     return GraphFilter(
    #         name = 'boxblur',
    #         # TODO: What is customizable in X:1 (?)
    #         args = f'{str(sigma)}:1'
    #     )

    # TODO: This one doesn't exist in my distribution
    # @staticmethod
    # def denoise(
    # ) -> GraphFilter:
    #     """
    #     Denoise.

    #     The command:
    #     - `hqdn3d`
    #     """
    #     return GraphFilter(
    #         name = 'hqdn3d',
    #         args = None
    #     )

    # Artistic and special effects
    @staticmethod
    def edgedetect(
    ) -> GraphFilter:
        """
        Detect the edges.

        The command:
        - `edgedetect`
        """
        return GraphFilter(
            name = 'edgedetect',
            args = None
        )
    
    @staticmethod
    def negate(
    ) -> GraphFilter:
        """
        Invert the colors.

        The command:
        - `negate`
        """
        return GraphFilter(
            name = 'negate',
            args = None
        )
    
    # TODO: This one doesn't exist in my distribution
    # @staticmethod
    # def frei0r(
    #     filter: str
    # ) -> GraphFilter:
    #     """
    #     Plugin custom filter.

    #     The command:
    #     - `frei0r={filter}`
    #     """
    #     # TODO: Customize the 'filter' possible values
    #     return GraphFilter(
    #         name = 'frei0r',
    #         args = filter
    #     )

    # Others
    @staticmethod
    def geq(
        # TODO: How to create expressions (?)
        expression: str = 'sin(2*PI*X/W)'
    ) -> GraphFilter:
        """
        TODO: What is this (?)
        """
        return GraphFilter(
            name = 'geq',
            args = f"lum='{expression}'"
        )
    
    @staticmethod
    def chromakey(
        hex_color: str,
        similarity: float = 0.01,
        alpha: float = 0.0
        # TODO: Add more params
    ) -> GraphFilter:
        """
        Turn the pixels with the 'hex_color'
        provided into transparent pixels.

        The 'similarity' is to include colors that
        are near the provided 'hex_color'. The 
        bigger the value is, the more colors will
        be included.

        The 'alpha' being 0.0 will make the pixels
        become fully opaque or fully transparent,
        while setting other value will make them
        partially transparent or opaque.

        The command:
        - `chromakey={hex_color}:{similarity}:{alpha}`

        See this:
        - https://ffmpeg.org/ffmpeg-filters.html#colorkey
        """
        # TODO: Accept colors as strings, rgbas,
        # etc. by using our custom library
        # Valid args = '0x00FF00:0.3:0.1'
        return GraphFilter(
            name = 'chromakey',
            args = f'{hex_color}:{str(float(similarity))}:{str(float(alpha))}'
        )
    
class _AudioGraphFilters:
    """
    Class to warp the video GraphFilters.
    """

    # Volume and dynamic
    @staticmethod
    def volume(
        factor: float
    ) -> GraphFilter:
        """
        Graph filter to set the volume of the video.

        The command:
        - `volume={factor}`
        """
        return GraphFilter(
            name = 'volume',
            args = str(float(factor))
        )
    
    @staticmethod
    def dynamic_compressor(
    ) -> GraphFilter:
        """
        Graph filter to reduce the dynamic range.

        The command:
        - `acompressor`
        """
        return GraphFilter(
            name = 'acompressor',
            args = None
        )
    
    # TODO: This one doesn't exist in my distribution
    # @staticmethod
    # def limit_peaks(
    #     limit: float
    # ) -> GraphFilter:
    #     """
    #     Graph filter to limit peaks.

    #     The command:
    #     - `alimiter=limit={limit}`
    #     """
    #     return GraphFilter(
    #         name = 'alimit',
    #         args = f'limit={str(float(limit))}'
    #     )
    
    @staticmethod
    def noise_gate(
    ) -> GraphFilter:
        """
        Graph filter to remove background noise.

        The command:
        - `agate`
        """
        return GraphFilter(
            name = 'agate',
            args = None
        )
    
    # Equalize and tone
    @staticmethod
    def equalizer(
        frequency: int,
        bandwith: str, # 'h' (Hz), 'q' (Q), 'o' (octave) or 's' (slope)
        width: int,
        gain: int
    ) -> GraphFilter:
        """
        Graph filter to equalize (increase or decrease
        frequencies).

        The command:
        - `equalizer=f={frequency}:t={bandwith}:={width}:g={gain}`

        A valid example:
        - `equalizer=f=1000:t=q:w=200:g=3`

        See this:
        - https://superuser.com/a/696187
        """
        return GraphFilter(
            name = 'equalizer',
            args = f'f={str(int(frequency))}:t={bandwith}:=w={str(int(width))}:g={str(int(gain))}'
        )
    
    @staticmethod
    def bass(
        gain: int
    ) -> GraphFilter:
        """
        Graph filter to improve the graves.

        The command:
        - `bass=g={gain}`

        A valid command:
        - `bass=g=10`
        """
        return GraphFilter(
            name = 'bass',
            args = str(int(gain))
        )
    
    @staticmethod
    def bass(
        gain: int
    ) -> GraphFilter:
        """
        Graph filter to improve the agudos.

        The command:
        - `treble=g={gain}`

        A valid command:
        - `treble=g=5`
        """
        return GraphFilter(
            name = 'treble',
            args = str(int(gain))
        )
    
    @staticmethod
    def highpass(
        frequency: int
    ) -> GraphFilter:
        """
        Graph filter to remove the frequencies below the
        'frequency' parameter provided.

        The command:
        - `highpass=f={frequency}`

        A valid command:
        - `highpass=f=200`

        See this:
        - https://stackoverflow.com/a/78504325
        """
        return GraphFilter(
            name = 'highpass',
            args = f'f={str(int(frequency))}'
        )
    
    @staticmethod
    def lowpass(
        frequency: int
    ) -> GraphFilter:
        """
        Graph filter to remove the frequencies above the
        'frequency' parameter provided.

        The command:
        - `lowpass=f={frequency}`

        A valid command:
        - `lowpass=f=5000`
        """
        return GraphFilter(
            name = 'lowpass',
            args = f'f={str(int(frequency))}'
        )
    
    # TODO: Add 'anequalizer' and check if available

    @staticmethod
    def accelerate(
        factor: float
    ) -> GraphFilter:
        """
        Graph filter to accelerate the audio to
        a maximum of 2x (factor = 2.0).

        The command:
        - `atempo={factor}`

        A valid command:
        - `atempo=1.5`
        """
        # TODO: What if factor < 1 (?)
        # TODO: What if factor > 2 (?)
        return GraphFilter(
            name = 'atempo',
            args = str(float(factor))
        )
    
    # TODO: Add 
    # asetrate=44100*0.8 → cambia la frecuencia de muestreo para efecto “pitch shift”.
    # aresample=48000 → remuestrear a otra frecuencia.

    @staticmethod
    def echo(
        in_gain: float = 0.6,
        out_gain: float = 0.3,
        delays: int = 1_000,
        decays: float = 0.5
    ) -> GraphFilter:
        """
        Graph filter to apply echo.

        The command:
        - `aecho={in_gain}:{out_gain}:{delays}:{decays}

        A valid command:
        - `aecho=0.8:0.9:1000:0.3`

        See this:
        - https://ffmpeg.org/ffmpeg-filters.html#aecho
        """
        return GraphFilter(
            name = 'aecho',
            args = f'{str(float(in_gain))}:{str(float(out_gain))}:{str(int(delays))}:{str(float(decays))}'
        )
    
    @staticmethod
    def phaser(
    ) -> GraphFilter:
        """
        Graphic filter to apply a classic phaser effect.

        The command:
        - `aphaser`
        """
        return GraphFilter(
            name = 'aphaser',
            args = None
        )
    
    @staticmethod
    def chorus(
        in_gain: float = 0.4,
        out_gain: float = 0.4,
        delays: int = 50, # in ms
        decays: float = 0.4,
        speeds: float = 0.25,
        depths: int = 2
    ) -> GraphFilter:
        """
        Graph filter to apply a chorus effect.

        The command:
        - `chorus={in_gain}:{out_gain}:{delays}:{decays}:{speeds}:{depths}

        A valid command:
        - `chorus=0.5:0.9:50:0.4:0.25:2`

        See this:
        - https://ffmpeg.org/ffmpeg-filters.html#chorus
        """
        return GraphFilter(
            name = 'chorus',
            args = f'{str(float(in_gain))}:{str(float(out_gain))}:{str(int(delays))}:{str(float(decays))}:{str(float(speeds))}:{str(int(depths))}'
        )
    
    # TODO: Add these (if available):
    # flanger - flanger.
    # stereotools - manipulación de imagen estéreo (pan, balance, etc.).
    # pan=stereo|c0=0.5*c0+0.5*c1|c1=c1 - control de mezcla de canales.

    # TODO: Add these (if available):
    #  Limpieza y restauración
    # anlmdn - reducción de ruido no estacionario.
    # afftdn - reducción de ruido basada en FFT.
    # adeclip - reconstrucción de audio clippeado.
    # adeclick - elimina clics y pops.

    # TODO: Add these (if available):
    #  Misceláneos y creativos
    # asubboost - refuerzo de subgraves.
    # areverse - reproduce audio al revés.
    # silenceremove - elimina silencios.
    # compand - compresor/expansor flexible.
    # crystalizer - realce de agudos artificial.
    # anequalizer - ecualización multibanda avanzada.

class GraphFilters:
    """
    Class to wrap a set of interesting GraphFilters
    that we can use in our video frames, making it
    easier to obtain them.
    """

    video = _VideoGraphFilters
    """
    Graph filters related to video frames.
    """
    audio = _AudioGraphFilters
    """
    Graph filters related to audio frames.
    """

    


"""
🔹 Transformaciones geométricas

scale=w:h → redimensionar (ej. scale=640:360).

crop=w:h:x:y → recortar región.

pad=w:h:x:y:color → añadir bordes/márgenes.

hflip / vflip → voltear horizontal/vertical.

transpose=1 → rotar 90° (hay variantes 0–3).

rotate=PI/6 → rotación libre en radianes.

🔹 Corrección de color y tono

eq=contrast=1.5:brightness=0.1:saturation=1.2 → ajuste global.

hue=s=0 → desaturación (blanco y negro).

hue=h=90 → rotación de tono (efecto “psicodélico”).

colorbalance=rs=.3:gs=-.3:bs=.0 → balance por canal.

curves=preset=strong_contrast → curvas estilo Photoshop.

lutrgb o lutyuv → modificar valores por canal con expresiones.

🔹 Enfoque y suavizado

unsharp → resaltar bordes (más nitidez).

smartblur → desenfoque inteligente.

boxblur=2:1 → desenfoque básico (rápido).

gblur=sigma=2 → desenfoque gaussiano.

hqdn3d → reducción de ruido (denoise).

🔹 Estilo artístico y efectos especiales

edgedetect → resaltado de bordes tipo dibujo a lápiz.

negate → invertir colores.

colorchannelmixer → combinar canales, simular filtros tipo Instagram.

frei0r=pixeliz0r:cell_size=10 → efecto pixelado.

frei0r=glow → halo de brillo.

frei0r=cartoon → aspecto de cómic.

🔹 Tiempo y FPS

fps=30 → remuestrear la frecuencia de frames.

setpts=0.5*PTS → cámara rápida (timelapse).

setpts=2.0*PTS → cámara lenta.

tinterlace → entrelazado/desentrelazado.

🔹 Otros curiosos

drawtext=text='Hello':x=10:y=20:fontsize=24:fontcolor=white → añadir texto.

drawbox=x=100:y=50:w=200:h=100:color=red@0.5 → dibujar cajas.

geq=lum='sin(2*PI*X/W)' → expresiones matemáticas para generar patrones.

chromakey=0x00FF00:0.3:0.1 → efecto “pantalla verde”.
"""