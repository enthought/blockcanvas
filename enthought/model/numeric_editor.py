#-------------------------------------------------------------------------------
#  
#  Tools useful for visually editing the contents of a numeric model.  
#  
#  Written by: David C. Morrill
#  
#  Date: 11/23/2005
#  
#  (c) Copyright 2005 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:  
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import HasPrivateTraits, Instance
    
from enthought.traits.ui.api \
    import TreeEditor, TreeNode, View, HGroup, VGroup, Item
    
from enthought.traits.ui.menu \
    import NoButtons
    
from numeric_model \
    import FilterSet, AggregateFilter, ExpressionFilter
    
#-------------------------------------------------------------------------------
#  'FilterSet' view:  
#-------------------------------------------------------------------------------
        
root_view = View()
    
#-------------------------------------------------------------------------------
#  'AggregateFilter' view:  
#-------------------------------------------------------------------------------
        
group_view = View(
    VGroup(
        VGroup( 
            'name',  '_',
            'rule@', '_',
            VGroup(
                'enabled',
                'use_value{Use value information}',
                show_left = False
            ),
            show_border = True,
            label       = 'Filter'
        ),
        VGroup(
            HGroup( 
                '55', 'value', 
                HGroup(
                    'is_bit{Value is a bit number}',
                    show_left = False 
                )
            ),
            'foreground_color',
            'background_color',
            enabled_when = 'use_value',
            show_border  = True,
            label        = 'Value Information'
        )
    ),
    buttons = NoButtons
)

#-------------------------------------------------------------------------------
#  'ExpressionFilter' view:  
#-------------------------------------------------------------------------------

expression_view = View(
    VGroup(
        VGroup( 
            'filter{Expression}', '_',
            'name',               '_',
            VGroup( 
                'enabled',
                'use_value{Use value information}',
                show_left = False
            ),
            show_border = True,
            label       = 'Filter'
        ),
        VGroup(
            HGroup( 
                '55', 'value', 
                HGroup(
                    'is_bit{Value is a bit number}',
                    show_left = False 
                )
            ),
            'foreground_color',
            'background_color',
            enabled_when = 'use_value',
            show_border  = True,
            label        = 'Value Information'
        )
    ),
    buttons = NoButtons
)
    
#-------------------------------------------------------------------------------
#  NumericFilter editor:  
#-------------------------------------------------------------------------------

nodes = [
    TreeNode( node_for   = [ FilterSet ],
              add        = [ AggregateFilter, ExpressionFilter ],
              label      = 'name',
              name       = 'Group',
              children   = 'filters',
              auto_open  = True,
              view       = root_view,
              icon_group = 'filter_group',
              icon_open  = 'filter_group' ),

    TreeNode( node_for   = [ AggregateFilter ],
              add        = [ AggregateFilter, ExpressionFilter ],
              label      = 'name',
              name       = 'Group',
              children   = 'filters',
              auto_open  = True,
              view       = group_view,
              icon_group = 'filter_group',
              icon_open  = 'filter_group' ),
               
     TreeNode( node_for   = [ ExpressionFilter ],
               label      = 'name',
               name       = 'Expression',
               view       = expression_view,
               icon_item  = 'filter_expression' )
]

def NumericFilterEditor ( ):
    return TreeEditor( nodes = nodes )
    
#-------------------------------------------------------------------------------
#  Test case:  
#-------------------------------------------------------------------------------
        
class TestFilter ( HasPrivateTraits ):
    
    filter = Instance( AggregateFilter, () )
    
    view = View(
        VGroup( 
            Item( 'filter', editor = NumericFilterEditor() ),
            show_labels = False
        ),
        width     = 0.35,
        height    = 0.4,
        resizable = True,
        buttons   = NoButtons
    )
    
if __name__ == '__main__':    
    test = TestFilter()
    test.configure_traits() 
    print len( test.filter.filters )
