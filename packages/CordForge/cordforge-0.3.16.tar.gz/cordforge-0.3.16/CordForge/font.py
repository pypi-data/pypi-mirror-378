from PIL import ImageFont


class Font:
    def __init__(_, font_path:str|None=None, size:int=24) -> None:
        _.size = size
        if isinstance(font_path, str):
            _.font = ImageFont.truetype(font_path, size)
        else:
            _.font = ImageFont.load_default(_.size)
        _.ascent, _.descent = _.font.getmetrics()
        _.height = _.ascent + _.descent