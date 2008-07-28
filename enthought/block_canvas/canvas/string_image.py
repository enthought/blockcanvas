from enthought.traits.api import Str
from enthought.pyface.image_resource import ImageResource

from enthought.enable.base import gc_image_for

class StringImage(Str):

    default_value = ""

    is_mapped=True

    # A description of the type of value this trait accepts:
    info_text = 'the name of an image resource.  It creates a shadow ' \
                'attribute that is the actual image.'

    def post_setattr ( self, object, name, value ):
        """ Create a shadow variable that holds the actual image.
        """
        # fixme: Should this be try/except protected to prevent exceptions?
        ir = ImageResource(value)
        object.__dict__[ name + '_' ] = gc_image_for(ir.absolute_path)
