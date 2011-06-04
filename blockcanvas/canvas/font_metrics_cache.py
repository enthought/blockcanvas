# Enthought Library Imports
from enable.font_metrics_provider import font_metrics_provider
from enable.kiva.traits.api import KivaFont
from traits.api import Any, Dict, HasTraits

class FontMetricsCache(HasTraits):
    """ A shared cache containing height and width metrics for
        a single font.  This is meant to speed up the estimation
        of font metrics without having to call get_text_extent()
        in kiva as often.
    """

    #---------------------------------------------------------------------
    # Traits
    #---------------------------------------------------------------------

    # Dictionary of font bounds tuples (width, height)
    metrics_cache = Dict()

    # Object used to measure text extents
    metrics = Any

    # Default font for determining metrics
    font = KivaFont("Courier 12")

    #---------------------------------------------------------------------
    # Public methods
    #---------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super(FontMetricsCache, self).__init__(*args, **kwargs)

        if self.metrics is None:
            self.metrics = font_metrics_provider()


    def get_metrics(self, text):
        """ If the cache has metrics for this string, then return
            otherwise, look up each character and add their metrics
            to the cache.
        """
        if len(text) > 1:
            ## FIXME:  To Do.  Right now only handle single characters.
            return None

        else:
            try:
                return self.metrics_cache[text]
            except KeyError:
                self.metrics_cache[text] = self.metrics.get_text_extent(text)[2:4]
                return self.metrics_cache[text]

    def clear_metrics_cache(self):
        """ Clear the dictionary of font metrics.  To be called if the
            font changes etc.
        """
        self.metrics_cache = {}

    #---------------------------------------------------------------------
    # Trait Listeners
    #---------------------------------------------------------------------

    def _font_changed(self, old, new):
        self.clear_metrics_cache()
        try:
            self.metrics.set_font(self.font)
        except:
            raise RuntimeError("Unable to set font on FontMetricsCache.")

