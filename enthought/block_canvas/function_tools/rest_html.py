""" Classes and functions for converting reST docstrings to HTML
"""

import cgi
import logging
import platform
import textwrap

import wx

from docutils import core
from docutils.writers.html4css1 import Writer, HTMLTranslator
from docutils.frontend import OptionParser
from docutils.parsers.rst import Parser
from docutils.utils import new_document


logger = logging.getLogger(__name__)


class HTMLFragmentTranslator(HTMLTranslator):
    """ A subclass of HTMLTranslator which produces only fragments of HTML.
        Used in convert_string_fragment.
    """

    def __init__(self, document):
        HTMLTranslator.__init__(self, document)
        self.head_prefix = ['','','','','']
        self.body_prefix = []
        self.body_suffix = []
        self.stylesheet = []
        self.initial_header_level = 5

    def astext(self):
        return ''.join(self.body)

def _count_indent(string):
    """ In a string, return the length of leading whitespace.
    """

    if string.lstrip() != string:
         return len(string) - len(string.lstrip())
    return 0

def _fix_indent(string):
    """ Attempts to fix abornaml indentation.
    """

    string_list = string.splitlines()

    start_first = 0
    if len(string_list) > 1:
        # The first line has it's own whitespace adjustment.
        # The 'first' line is actually the first line that is not blank
        while start_first < len(string_list):
            if string_list[start_first] == '':
                start_first += 1
            else:
                break
        # The following lines use a different one.
        # Starts from the first non-blank line
        start_next = start_first + 1
        while start_next < len(string_list):
            if string_list[start_next] == '':
                start_next += 1
            else:
                break
        indentRest = _count_indent(string_list[start_next])
        for i,line in enumerate(string_list[start_next:]):
            string_list[i+start_next] = line[indentRest:]
    indent_first = _count_indent(string_list[start_first])
    string_list[start_first] = string_list[start_first][indent_first:]

    # Join the split string back together and create HTML
    return '\n'.join(string_list)

def _html_header():
    """ Checks if on windows platform (this means that ie widget should have
        been used), and print an html header that provides a nicer font setting.
        Otherwise, print a standard header.
    """
    if platform.system() is 'Windows':
        return """<html>
                  <head>
                  <style type="text/css">
                  body, table
                  {
                      font-family: sans-serif;
                      font-size: 80%;
                      margin: 0px;
                      padding: 0px
                  }
                  .literal-block
                  {
                      margin-top: 0px;
                      margin-bottom: 0px;
                      margin-left: 15px
                  }
                  .desc { margin-top: 0px; margin-bottom: 0px }
                  </style>
                  </head>
                  <body>
                """
    else:
        return "<html>\n<body>\n"

def pre_formatted_html(text):
    """ Render the given text inside <pre> tags.
    """
    lines = text.split('\n')
    # Handle the first line specially.
    firstline = lines[0].strip()
    body = textwrap.dedent('\n'.join([line.rstrip() for line in lines[1:]]))
    text = '%s\n%s' % (firstline, body)
    html = '<html>\n<head></head>\n<body>\n<pre>\n%s</pre>\n</body>\n</html>' % cgi.escape(text)
    return html

def convert_string_fragment(string):
    """ Converts a string of reST text into an html fragment (ie no <header>,
        <body>, etc tags).
    """

    html_fragment_writer = Writer()
    html_fragment_writer.translator_class = HTMLFragmentTranslator
    return core.publish_string(_fix_indent(string),
                               writer = html_fragment_writer,
                               # Suppress output of warnings in html
                               settings_overrides={'report_level':'5'})

def convert_string(string):
    """ Converts a string of reST text into html.
    """

    return "<html>\n<body>\n" + convert_string_fragment(string) + "</body>\n</html>"

def convert_function_info(function_name, doc_string, defaults=[]):
    """ Given a documentation string, writes html documentation. First tries 
        to identify the standard docstring format for has_units objects. If 
        sucessful, outputs a nicely formatted html. Otherwise, converts to html 
        with no other changes.

        Code borrowed from numerical_modelling's has_unit.py
    """
    system = platform.system()
    
    stripped_lines = [line.strip() for line in doc_string.splitlines()]

    # XXX: hack to avoid expensive formatting. Remove later.
    if len(stripped_lines) > 100:
        return pre_formatted_html(doc_string)

    try:
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

        # If things aren't looking right at this point, the docstring isn't
        # properly formatted, so we're done.
        if len(sections) == 0 or len(inputtext) == 0 or len(outputtext) == 0:
            html = _html_header()
            # For some reason, the font size is huge when the native wx widgt is
            # used. Reduce its size:
            if system is not 'Windows' and wx.VERSION[1] < 8:
                html += '<font size="-2">\n'
            html += convert_string_fragment(doc_string)
            if system is not 'Windows' and wx.VERSION[1] < 8:
                    html += '</font>\n'
            html += "</body>\n</html>"

        # Continue building the 'proper' html
        else:
            # Data in a paragraph comprises of variables in separate lines.
            # However each line for a variable is a combination of multiple lines,
            # and we are interested in retrieving only the first line for each
            # variable (in both inputs and outputs). Hence we join the separated
            # lines and then split all of them

            inputlines = "\n".join(inputtext).splitlines()
            outputlines = "\n".join(outputtext).splitlines()

            # Split into lines which give description and line which give
            # variable data with units

            inputdesc = [line for line in inputlines if not " :" in line and
                         _count_indent(line) == 0]
            outputdesc = [line for line in outputlines if not " :" in line and
                          _count_indent(line) == 0]
            inputlines = [line.split(" :") for line in inputlines if " :" in line
                          or _count_indent(line) > 0]
            outputlines = [line.split(" :") for line in outputlines if " :" in line
                           or _count_indent(line) > 0]

            # Create first line, listing function parameters and return vals.
            html = _html_header()
            if system is not 'Windows' and wx.VERSION[1] < 8:
                html += '<font size="-2">\n'
            html += "<p>"
            check_returns = False
            for i,var in enumerate(outputlines):
                check_returns = True
                html += var[0]
                if i < len(outputlines) - 1:
                    html += ", "
                else:
                    html += " "
            if check_returns:
                html += "="
            html += " <b>" + function_name + "</b>("
            for i,var in enumerate(inputlines):
                html += var[0]         
                if len(defaults) is not 0:
                    index = len(defaults) - len(inputlines) + i
                    if index >= 0:
                        html += "=" + str(defaults[index])
                if i < len(inputlines) - 1:
                    html += ", "
            html += ")\n"

            # Add a brief description. Should be the first line of docstring.
            html += "<br>" + stripped_lines[0] + "</p>\n"

            # Add a list of inputs
            html += "<p><u>Inputs</u>\n<table>"
            for var,desc in map(None, inputlines, inputdesc):
                # fixme: Failing for "marine_environment" function.
                html += "\n<tr><td></td><td><b>" + var[0] + "</b>"
                # The format for the units section is ' units=x', so we slice
                # off the first seven characters. fixme: support for spacing
                # between equal sign, despite the incorrectness of this syntax.
                if (len(var) == 3 )and (var[2][7:] != 'dimensionless'):
                    html+= " [" + var[2][7:] + "]"
                if desc is None:
                    html += "</td>"
                else:
                    html += ":</td><td>" + desc + "</td>"
                html += "</tr>"
            html += "\n</table></p>"

            # Add a list of ouputs
            html += "\n<p><u>Outputs</u>\n<table>"
            for var,desc in map(None, outputlines, outputdesc):
                html += "\n<tr><td>"
                if var is not None:
                    html += "</td><td><b>" + var[0] + "</b>"
                    if (len(var) == 3 )and (var[2][7:] != 'dimensionless'):
                        html+= " [" + var[2][7:] + "]"
                    if desc is None:
                        html += "</td>"
                    else:
                        html += ":</td><td>" + desc + "</td>"
                html += "</tr>"
            html += "\n</table></p>"

            # Give a more detailed description, if available
            # Get the description text directly from the string. The parser will not
            # produce useful output for a description with blank lines in the section
            # (these are required for certain reST structures)
            try:
                desc_html = convert_string_fragment(doc_string)
                if system is 'Windows':
                    desc_html = desc_html.replace('<p>','<p style="margin: 0px; padding:0px">')
                startSearch = 'ion</a></h5>'
                start = desc_html.rindex(startSearch)
                end = desc_html.rindex(r'</div>', start)
                html += '\n<p style="margin: 0px; padding:0px">'
                html += '<u>Description</u></p>\n<table><tr><td></td><td>'
                if system is not 'Windows' and wx.VERSION[1] < 8:
                    html += '<font size="-2">'
                html += desc_html[start+len(startSearch):end]
                if system is not 'Windows' and wx.VERSION[1] < 8:
                    html += '</font>'
                html += "\n</td></tr></table>\n"
            except ValueError: pass

            if system is not 'Windows' and wx.VERSION[1] < 8:
                html += '</font>\n'
            html += "</body>\n</html>"
    except Exception, e:
        logger.warning('Could not parse docstring; %s: %s' % (e.__class__.__name__, e))
        html = pre_formatted_html(doc_string)
    return html

def get_html_from_function_info(function_info):
    """Convenience function to get html from a FunctionInfo object"""
    # FIXME: Pass in default arguments
    return convert_function_info(function_info.name, function_info.doc_string)
