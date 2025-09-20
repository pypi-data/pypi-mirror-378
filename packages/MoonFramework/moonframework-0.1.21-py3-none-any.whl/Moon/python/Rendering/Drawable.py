from Moon.python.Rendering.Text import Text, BaseText
from Moon.python.Rendering.Shapes import (
    CircleShape, RectangleShape, LineShape, PolygoneShape,
    LineThinShape, LinesThinShape
)

type Drawable = CircleShape | RectangleShape | LineShape | PolygoneShape | LineThinShape | LinesThinShape
