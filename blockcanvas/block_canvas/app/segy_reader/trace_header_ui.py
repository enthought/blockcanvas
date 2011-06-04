""" View for a TraceHeader of a Segy file.
"""

# Enthought library imports
from enthought.traits.api import HasTraits, Instance, List, Any, Str, Int
from enthought.traits.ui.api import View, Item, TableEditor, Group, HGroup, \
     spring, RangeEditor
from enthought.traits.ui.table_column import ObjectColumn
from enthought.traits.ui.api import WindowColor

# Geo imports
from geo.io.segy.trace_header import TraceHeader

#------------------------------------------------------------------------------
# Editor for TraceHeaderView view
#------------------------------------------------------------------------------
trace_header_byte_offsets = ['001-004', '005-008', '009-012', '013-016',
                             '017-020', '021-024', '025-028', '029-030',
                             '031-032', '033-034', '035-036', '037-040',
                             '041-044', '045-048', '049-052', '053-056',
                             '057-060', '061-064', '065-068', '069-070',
                             '071-072', '073-076', '077-080', '081-084',
                             '085-088', '089-090', '091-092', '093-094',
                             '095-096', '097-098', '099-100', '101-102',
                             '103-104', '105-106', '107-108', '109-110',
                             '111-112', '113-114', '115-116', '117-118',
                             '119-120', '121-122', '123-124', '125-126',
                             '127-128', '129-130', '131-132', '133-134',
                             '135-136', '137-138', '139-140', '141-142',
                             '143-144', '145-146', '147-148', '149-150',
                             '151-152', '153-154', '155-156', '157-158',
                             '159-160', '161-162', '163-164', '165-166',
                             '167-168', '169-170', '171-172', '173-174',
                             '175-176', '177-178', '179-180', '181-184',
                             '185-188', '189-192', '193-196', '197-200',
                             '201-202', '203-204', '205-240']

trace_header_columns = [ObjectColumn(name='byte_offset', editable=False),
                        ObjectColumn(name='name', label='Field',
                                     editable=False),
                        ObjectColumn(name='value', label='Value',
                                     editable=False)]
trace_header_editor = TableEditor(columns=trace_header_columns,
                                  editable=True,
                                  configurable=False,
                                  sortable=False,
                                  sort_model=True,
                                  selection_bg_color=None,
                                  label_bg_color=WindowColor,
                       )


#------------------------------------------------------------------------------
#  TraceHeaderItem class
#------------------------------------------------------------------------------

class TraceHeaderItem(HasTraits):
    """ Class for each object in trace header to be viewed.
    """

    byte_offset = Str('')
    name        = Str('')
    value       = Any

#------------------------------------------------------------------------------
#  TraceHeaderView class
#------------------------------------------------------------------------------

class TraceHeaderView(HasTraits):
    """ Modelview class for a TraceHeader
    """

    model                = Instance(TraceHeader)
    field_list           = List(TraceHeaderItem)
    trace_header_number  = Int(1)
    total_headers        = Int(250)

    # Default dynamic view
    def trait_view(self, name=None, view_element=None):
        """ The default view should account for the number of trace
            headers that can be displayed.
        """

        range_editor = RangeEditor(low = 1, high = self.total_headers)
        header_number_label = 'Trace header number (Total %s traces)' % \
                              self.total_headers
        return View(
            Group(
                HGroup(
                    Item('trace_header_number', editor=range_editor,
                         label=header_number_label),
                    spring,
                ),
                Item('field_list', editor=trace_header_editor,
                     show_label=False)),
            resizable = True
           )

    def _model_changed(self):
        """ Return a TraceHeaderItem
        """

        self.field_list = []
        if self.model is not None:
            for i,v in enumerate(self.model.FIELDS):
                self.field_list.append(
                    TraceHeaderItem(name=v,value=getattr(self.model, v),
                                    byte_offset=trace_header_byte_offsets[i]))

        return

    def _total_headers_changed(self):
        """ Reset trace_header_number
        """
        self.trace_header_number=1
        return


### EOF ------------------------------------------------------------------------




