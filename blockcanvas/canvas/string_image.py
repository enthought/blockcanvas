from traits.api import Str
from pyface.image_resource import ImageResource

import sys
from zipfile import ZipFile, is_zipfile
from cStringIO import StringIO
from os.path import abspath
from types import TupleType
from enable.kiva.image import Image

# The gc_image_for() function was formerly in Enable but was deprecated,
# and since the StringImage class is the only place that used it, it has
# been moved here.  The parts of it that referenced the images/ directory
# in enable have been removed.

# Image cache dictionary (indexed by 'normalized' filename):
_image_cache = {}
_zip_cache   = {}
_app_path    = None
_enable_path = None

def gc_image_for ( name, path = None ):
    "Convert an image file name to a cached Kiva gc containing the image"
    global _app_path, _enable_path
    filename = abspath( name )
    image     = _image_cache.get( filename )
    if image is None:
        cachename = filename
        if path is not None:
            zip_path = abspath( path + '.zip' )
            zip_file = _zip_cache.get( zip_path )
            if zip_file is None:
               if is_zipfile( zip_path ):
                   zip_file = ZipFile( zip_path, 'r' )
               else:
                   zip_file = False
               _zip_cache[ zip_path ] = zip_file
            if isinstance( zip_file, ZipFile ):
                try:
                    filename = StringIO( zip_file.read( name ) )
                except:
                    pass
        try:
            _image_cache[ cachename ] = image = Image( filename )
        except:
            _image_cache[ filename ] = info = sys.exc_info()[:2]
            raise info[0], info[1]
    elif type( image ) is TupleType:
        raise image[0], image[1]
    return image


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
