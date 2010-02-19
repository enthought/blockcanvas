""" Helper functions for decorated functions
"""


# Standard imports
from docutils.frontend import OptionParser
from docutils.parsers.rst import Parser
from docutils.utils import new_document
import compiler, inspect, linecache, re, string

# ETS imports
from enthought.units.variable import Variable


#-------------------------------------------------------------------------------
#   All decorators
#-------------------------------------------------------------------------------

def getsource(func):
    """ Returning source code for a decoratted function.

        inspect.getsource fails on decoratted functions, hence, a more elaborate
        way to retrieve the source-code of such functions

        Parameters:
        -----------
        func: function object

    """

    # Obtain the module of the function
    module = inspect.getmodule(func)

    # Get the source lines of the file containing the module
    file = inspect.getsourcefile(module)
    lines = linecache.getlines(file)
    object = func.func_code

    # Using regular expressions find the lines of the source-code that
    # represent the function
    lnum = len(lines)-1
    pat = re.compile(r'^(\s*def\s%s)|(.*(?<!\w)lambda(:|\s))|^(\s*@)' %
                     func.__name__)

    found, source, code_object = 0, '', None
    while lnum >= 0 and found == 0:
        if pat.match(lines[lnum]):
            new_lines = inspect.getblock(lines[lnum:])
            source = string.join(new_lines,'')

            # Check if this is the right function, as reg-ex matches the
            # line with decorator definitions, i.e., @decorator-name, too.
            code_object = compiler.compile(source, '', 'exec')
            if func.__name__ in code_object.co_varnames:
                found = 1

        lnum = lnum - 1

    # Return the source code of the function block
    if found:
        return source
    else:
        return None


#-------------------------------------------------------------------------------
#   has_units decorator
#-------------------------------------------------------------------------------

def parse_docstrings_for_units(doc_value):
    """ Returns the inputs dictionary and outputs list after parsing docstrings

        Parameters:
        -----------
        doc_value : String
            Docstring of the function

        Returns:
        --------
        inputs_dict : Dict
            {variable_name: Variable}
        outputs_list : List
            list of Variables

    """

    # Checking if it is a valid string
    if doc_value is None:
        return {}, []

    # Strip indentation/whitespace before and after each line of docstring
    stripped_lines = [line.strip()
                      for line in doc_value.expandtabs().splitlines()]

    if len(stripped_lines) == 0:
        return

    # Parse the lines using docutil parser to get a document-tree
    settings = OptionParser(components=(Parser,)).get_default_values()
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

    return inputs_dict, outputs_list


### EOF ------------------------------------------------------------------------