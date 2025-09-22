from yta_video_pyav.reader.filter.dataclass import GraphFilter
from yta_validation import PythonValidator
from av.filter.graph import Graph
from av.video.stream import VideoStream
from av.audio.stream import AudioStream
from typing import Union


def get_filter_graph(
    stream: Union[VideoStream, AudioStream],
    filters: Union[list[GraphFilter], dict]
) -> Graph:
    """
    Get a Graph instance that has been configured
    to apply the 'filters' provided on the frames
    from the 'stream' that has been also given.

    To apply the filter use the Graph returned for
    each frame with 2 simple lines:
    - `graph.push(frame)`
    - `frame = graph.pull()`
    """
    # TODO: Validate 'filters' is list[GraphFilter]
    # or dict (?)
    # TODO: Maybe return None if no filters (?)
    filters = (
        dict_to_graph_filters(filters)
        if PythonValidator.is_dict(filters) else
        filters
    )
    
    graph = Graph()

    # Entry point, input
    reference = (
        graph.add_buffer(
            template = stream
        )
        if PythonValidator.is_instance_of(stream, VideoStream) else
        graph.add_abuffer(
            template = stream
        )
    )

    for graph_filter in filters:
        # TODO: Remove, this is for debug
        print(f'Adding filter: {graph_filter.name}:{graph_filter.args}')
        
        """
        Filters can have or have not arguments so,
        if no arguments, the value must be None
        """
        try:
            node = graph.add(
                filter = graph_filter.name,
                args = graph_filter.args
            )
        except:
            # TODO: Remove, this is for debug
            print(f'   [ERROR] The filter "{graph_filter.name}" is not available in this ffmpeg distribution or it does not exist.')
            continue

        reference.link_to(node)
        reference = node

    # Exit point, output
    buffersink = (
        'buffersink'
        if PythonValidator.is_instance_of(stream, VideoStream) else
        'abuffersink'
    )
    reference.link_to(graph.add(buffersink))

    graph.configure()

    return graph

def dict_to_graph_filters(
    filters: dict
) -> list[GraphFilter]:
    """
    Turn a dict into a list of GraphFilter
    instances.

    Here is an example of a valid dict:
    ```
    filters = {
        'scale': '640:360',
        'hue': 's=0',
        'hflip': None
    }
    ```
    """
    return [
        GraphFilter(
            name = name,
            args = args
        )
        for name, args in filters.items()
    ]