# Standard library imports
from docutils.frontend import OptionParser
import docutils.nodes as nodes
from docutils.parsers.rst import Parser
from docutils.utils import new_document
import copy
from string import Template

# Local imports
from variable import Variable
from function_signature import (call_signature, def_signature,
                                function_arguments)
from unit_manipulation import (convert_units, set_units, have_some_units,
    strip_units)

def has_units(func=None, summary='', doc='', inputs=None, outputs=None):
    r"""Function decorator: Wrap a standard python function for unit conversion.

        Parameters
        ----------
        func : function, optional
            The function to wrap. Usually, has_units will be used as a bare
            "@has_units" decorator, so this argument will usually be supplied by
            the interpreter as it interprets that syntax.
        summary : str, optional
            A short string describing the function.
        doc : str, optional
            A longer string describing the function in detail.
        inputs : str, optional
            A string containing information about unit conversion, etc.  for
            arguments in the function.  The argument names in this string must
            match those in the python signature.  The order the arguments are
            specified in does not matter as the order of arguments from the
            wrapped function is always used.  The format of the string is a as
            follows::

                "a: notes on a:units=m/s;b: notes on b:units=m/s"

             That is, information about each argument is separated by
             a semi-colon (';').  Each argument has three fields that are
             separated by colons (':').  The first is the name of the variable.
             The 2nd is a string.  The 3rd specified the units.  Other fields
             may be added later.
        outputs : str, optional
             A string with the same format as the 'inputs' string that specifies
             the output variables.  This *is* an ordered list as there is no way
             to determine the functions outputs from the function object.

        Description
        -----------
        This decorator adds a unit conversion step to input and output
        variables of a python function.  The resulting function can be used as
        a standard python function and has an identical calling signature to
        the wrapped function.  If passed standard scalars and arrays as input,
        it will behave identically.  If "unitted" objects, such as UnitArray,
        are handed in, however, they will be unit converted from their given
        units to the units expected by the function.  In this case, output
        variables are converted from arrays or scalars to UnitArray or
        UnitScalar so that the results carry the units with them.  Note that
        these objects are derived from standard numpy.ndarray and float objects,
        so they will behave exactly like them.  The only caveat to this is that
        you should use isinstance(value, ndarray) instead of "type(array) is
        ndarray" when testing for their type, but you should be doing that
        anyways.

        Regardless of whether the inputs have units or not, the actual values
        passed to the function will be stripped of units. The wrapped function
        will only deal with regular numpy arrays and scalars.

        If units are not assigned to a variable, absolutely no conversion is
        applied to that variable.

        Example definition of a unitted addition function:

            >>> from enthought.numerical_modeling.units.api import has_units, UnitArray
            >>> @has_units
            ... def add(a,b):
            ...     ''' Add two arrays in ft and convert them to m.
            ...
            ...         Parameters
            ...         ----------
            ...         a : array : units=ft
            ...             An array
            ...         b : array : units=ft
            ...             Another array
            ...
            ...         Returns
            ...         -------
            ...         c : array : units=m
            ...             c = a + b
            ...     '''
            ...     return (a+b)*0.3048

            >>> from numpy import array
            >>> a = array((1,2,3))
            >>> add(a,a)
            array([ 0.6096,  1.2192,  1.8288])

            >>> from enthought.units.length import m
            >>> a = UnitArray((1,2,3), units=m)
            >>> add(a,a) # (Converts m -> ft -> m)
            UnitArray([ 2.,  4.,  6.])
            >>> add(a,a).units
            1.0*m

        Alternatively, parameter information can be specified in the decorator:

            >>> from numpy import array
            >>> from enthought.numerical_modeling.units.api import has_units
            >>> @has_units(inputs="a:an array:units=ft;b:array:units=ft",
            ...            outputs="result:an array:units=m")
            ... def add(a,b):
            ...     " Add two arrays in ft and convert them to m. "
            ...     return (a+b)*0.3048

        The returned function has several attributes attached to it:

          summary: A short description of the function.  This is taken from the
                   'summary' argument to the decorator.
          doc:     A longer description of the function.  This is taken from the
                   'doc' argument to the decorator.
          inputs: A list of Variable objects, for each argument to the function
                  *in the order they are defined in the python function
                  signature*.  If you did not supply any information about the
                  argument in "inputs", then a default Variable object is
                  created.
          outputs: A list of Variable objects, for each output of the function
                   in the order they you specify them in the "outputs" variable
                   in the argument list.
    """
    
    # If has_units is applied on a function directly to make use of the
    # function's docstrings

    if func is not None:

        # Strip indentation/whitespace before and after each line of docstring
        stripped_lines = [line.strip()
                          for line in func.__doc__.expandtabs().splitlines()]

        # Parse the lines using docutil parser to get a document-tree
        settings = OptionParser(components=(Parser,)).get_default_values()
        # Silence warnings.
        settings.report_level = 3
        document = new_document("Docstring", settings)
        Parser().parse("\n".join(stripped_lines), document)

        # Filter out children of the root of the document-tree which are tagged
        # as "sections". Usually section has "title" and "paragraph" as
        # children. The inputs and outputs we are looking for are in the
        # "paragraph" section of the "section".

        sections = [child for child in document.children
                    if child.tagname.lower() == "section"]

        # Inputs are in the section with title "Parameters" and outputs are in
        # the section with title "Returns".

        inputtext = [
            section.children[1].children[0].data for section in sections
            if 'parameters' in section['names']
        ]
        outputtext = [
            section.children[1].children[0].data for section in sections
            if 'returns' in section['names']
        ]

        # Data in a paragraph comprises of variables in separate lines.
        # However each line for a variable is a combination of multiple lines,
        # and we are interested in retrieving only the first line for each
        # variable (in both inputs and outputs). Hence we join the separated
        # lines and then split all of them

        inputlines = "\n".join(inputtext).splitlines()
        outputlines = "\n".join(outputtext).splitlines()

        # Look for lines which give us the variable data with units

        unitted_inputlines = [line for line in inputlines if ":" in line]
        unitted_outputlines = [line for line in outputlines if ":" in line]

        # Process inputs and outputs to pass as parameters to _has_units
        # function
        inputs_dict = {}
        outputs_list = []
        for input_string in unitted_inputlines:
            input = Variable.from_string(input_string)
            inputs_dict[input.name] = input
        for output_string in unitted_outputlines:
            outputs_list.append(Variable.from_string(output_string))

        return _has_units(summary, doc, inputs_dict, outputs_list)(func)

    else: # func is None

        inputs_dict = {}
        if inputs is not None:
            # fixme:  extremely lame -- no error detection.
            for input_string in inputs.strip().split(';'):
                if input_string:
                    input = Variable.from_string(input_string)
                    inputs_dict[input.name] = input

        outputs_list = []
        if outputs is not None:
            for output_string in outputs.strip().split(';'):
                if output_string:
                    outputs_list.append(Variable.from_string(output_string))
        if not outputs_list:
            outputs_list = [Variable(name="result")]

        return _has_units(summary, doc, inputs_dict, outputs_list)

def _has_units(summary="", doc="", inputs=(), outputs=()): #@UnusedVariable
    inputs = dict(inputs)
    outputs = list(outputs)

    def units_wrap(_func_):
        name = _func_.func_name
        define = def_signature(_func_) #@UnusedVariable
        call = call_signature(_func_, '_func_') #@UnusedVariable
        args, kw, args_ordered = function_arguments(_func_) #@UnusedVariable
        args_string = ', '.join(args_ordered) #@UnusedVariable

        # build list of units for the arguments
        # fixme: We should detect when someone has specified an input name
        #        that isn't actually used because it doesn't match an actual
        #        input name.
        # fixme: Should input_list and output_list be tuples to prevent people
        #        from mutating them.
        input_units = []
        input_list = []
        for arg in args_ordered:
            if inputs.has_key(arg):
                input_units.append(inputs[arg].units)
                input_list.append(copy.copy(inputs[arg]))
            else:
                # If no units were specified for the variable, set them to
                # None, and put a Variable place holder for it in the
                # inputs list.
                input_units.append(None)
                input_list.append(Variable(name=arg))

        # Build the output units list.
        output_units = [output.units for output in outputs]
        output_list = [copy.copy(output) for output in outputs]

        # Here is the function wrapper, built from the values that we set up
        # above.
        template = Template('\n'.join([
            '$define',
            '    # Only convert units if at least one of the inputs already has units.',
            '    any_units = have_some_units($args_string)',
            '    if any_units:',
            '        $args_string = convert_units(input_units, $args_string)',
            '        # Now remove the units.',
            '        $args_string = strip_units($args_string)',
            '    results = $call',
            '    if any_units:',
            '        if len(output_units) == 1:',
            '            results = set_units(output_units, results)',
            '        elif len(output_units) > 1:',
            '            results = set_units(output_units, *results)',
            '    return results',
            '$name.func_name = _func_.func_name',
            '$name.__doc__ = _func_.__doc__',
            '$name.__module__ = _func_.__module__',
            '$name.inputs = input_list[:]',
            '$name.outputs = output_list[:]',
            '$name.summary = summary',
            '$name.doc = doc',
            ]))
        code = template.substitute(**locals())

        # Create the namespace in which the code will be executed.
        # fixme: This might work fine if it were just locals()
        vars = {'_func_':_func_,
                'convert_units': convert_units,
                'set_units': set_units,
                'have_some_units': have_some_units,
                'strip_units': strip_units,
                'input_list': input_list,
                'output_list': output_list,
                'input_units':input_units,
                'output_units':output_units,
                'summary':summary,
                'doc':doc,
                }
        exec code in vars

        # return freshly created wrapper version of the function.
        return vars[name]

    # Return the function decorator function (whew!)
    return units_wrap
