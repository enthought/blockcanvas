from blockcanvas.numerical_modeling.name_magic import magically_bound_names # XXX
from blockcanvas.numerical_modeling.numeric_context.api import (
    MaskFilter, NumericContext, OpenContext, PassThruContext, ReductionContext
)

# XXX (Interactor should handle magically bound names itself)
# Tell the world about our magic
for name in 'push_mask', 'pop_mask', 'push_group', 'pop_group', \
            'associate_indices', 'primary_index':
    magically_bound_names.add(name)

def default_context(context=None, **kw):
    '(Build a context in which our things execute ...)'

    if context is None:
        context = NumericContext()
    else:
        context = context.context_base
    context = PassThruContext(context)

    # Include some magic
    context.update({

        # For introspection
        #'__context__' : context, # XXX numeric_context handles this

        # For testing whether a name is defined
        'isdef' : _isdef(context),

        # For masking arrays in scope
        'push_mask' : _push_mask(context),
        'pop_mask'  : _pop_mask(context),

        # For managing groups
        'push_log_group'    : _push_group(context),
        'pop_log_group'     : _pop_group(context),
        'associate_indices' : _associate_indices(context),
        'primary_index'     : _primary_index(context),
    })

    # Include the user's mappings (after our own)
    context.update(kw)

    return context

def _isdef(context):
    def f(name):
        return name in context
    return f

def _push_mask(context):
    def f(mask):
        context.insert_context(
            ReductionContext(context_filter=MaskFilter(mask=mask)))
    return f

def _pop_mask(context):
    def f():
        assert isinstance(context.context, ReductionContext)
        context.remove_context(context.context)
    return f

def _push_group(context):
    def f(group_name):
        print 'Not implemented: push_group' # TODO
    return f

def _pop_group(context):
    def f():
        print 'Not implemented: pop_group' # TODO
    return f

def _associate_indices(context):
    def f(*args):
        print 'Not implemented: associate_indices' # TODO
    return f

def _primary_index(context):
    def f(index):
        print 'Not implemented: primary_index' # TODO
    return f
