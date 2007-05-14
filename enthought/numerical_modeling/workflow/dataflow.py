from numpy import alltrue
from enthought.util.sequence import all

from enthought.numerical_modeling.workflow.block.api import Block

# Possible future direction: Respond to changes in 'block 'and 'context', i.e.
# a dataflow object "links" a block and a context such that changes to the
# block's inputs in the context trigger the block to evaluate and update the
# outputs in the context. How does this interact with disconnecting outputs?
# How would we set multiple inputs and only recompute once for the whole set --
# currently, NumericContext.update fires multiple events.

class Dataflow:

    def __init__(self, block, context):
        self.block = block
        self.context = context
        self._populated_context = False

    def set(self, **inputs):
        'Set data in our context and recompute dependent data as necessary.'

        # Do as little as possible
        for k,v in inputs.items():
            # (Use 'alltrue' because numpy.array violates the __eq__ protocol)
            if k in self.context and alltrue(self.context[k] == v):
                del inputs[k]
        if inputs != {}:

            # Set the inputs in the context
            self.context.update(**inputs)

            # Execute the whole block once initially to populate the context
            # with intermediate values so that arbitrary sub-blocks can run
            # safely
            if not self._populated_context:
                self.block.execute(self.context)
                self._populated_context = True

            # Propogate the effects of setting the inputs in the context
            self.block.restrict(inputs=set(inputs)).execute(self.context)
