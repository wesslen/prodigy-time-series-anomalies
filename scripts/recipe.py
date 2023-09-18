import prodigy

from prodigy.components.preprocess import fetch_media
from prodigy.components.stream import get_stream

@prodigy.recipe("classify-images")
def classify_images(
        dataset, 
        source
        ):

    OPTIONS = [
        {"id": 0, "text": "Anamoly"},
        {"id": 1, "text": "Normal"},
        {"id": 2, "text": "Missing"},
        {"id": -1, "text": "Other"}
    ]

    def add_options(stream):
        for eg in stream:
            eg["options"] = OPTIONS
            yield eg

    stream = get_stream(source)
    stream = stream.apply(add_options)

    return {
        "dataset": dataset,
        "stream": stream,
        "view_id": "choice",
        "config": {
            "choice_style": "single",  # or "multiple"
            # Automatically accept and submit the answer if an option is
            # selected (only available for single-choice tasks)
            "choice_auto_accept": True
        }
    }