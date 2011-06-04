""" Helper functions for interactor classes.
"""

# Standard imports
import numpy, os

# ETS imports
from enthought.units.unit_db import UnitDB
from enthought.units.unit_manager import unit_manager


#-------------------------------------------------------------------------------
#  Import functions
#-------------------------------------------------------------------------------

def load_range_files( file_dict ):
    """ Load the files for determining ranges of interactors, plots, etc. for
        the block_unit.

        file_dict should give the following information:

        - file_dict['global'] gives path of file containing users' global
          preferences.
        - file_dict['project'] contains the preferences set for the project

        The file-formats for these files should be as shown; and the values
        used should be in the imperial unit-system, if required::

            <variable_name1>   <low_value> <high_value>

        Parameters:
        -----------
        file_dict : Dict
            Should contain keys 'global' and 'project';

        Returns:
        --------
        range_dict : Dict
            The dictionary contains names for lookup and tuples as values,
            where the tuple gives (low, high) value, for example::

                range_dict['psonic'] = (psonic_low_value, psonic_high_value)
    """

    # Global units preferences.
    udb = UnitDB()
    udb.get_family_ranges_from_file()
    current_unit_system = unit_manager.get_default().name.lower()
    range_dict = {'units': {}, 'user':{}}
    for k in udb.unit_ranges.keys():
        range_dict['units'][k] = udb.unit_ranges[k][current_unit_system]

    # Users' global preferences and project settings
    if file_dict.has_key('global'):
        file_list = [file_dict['global']]
    else:
        file_list = []
    if file_dict.has_key('project'):
        file_list.append(file_dict['project'])

    for filename in file_list:
        if os.path.exists(filename) and os.path.isfile(filename):
            file_object = open(filename, 'r')
            for line in file_object:
                values = line.split()
                key = values.pop(0)
                # FIXME: Unit conversions when there is change in unit system.
                range_dict['user'][key] = tuple([round_str_convert(value) for
                                                 value in values])


    return range_dict


#-------------------------------------------------------------------------------
#  Miscellaneous functions
#-------------------------------------------------------------------------------

def add_list_to_listed_list(new_list, listed_list):
    """ To add combinations to list of lists; thus building combinations.

        Parameters:
        -----------
        new_list: List(variables)
            eg: [v_1, v_2, ..., v_k]
        listed_list: List(List(variables))
            eg: [[v_01, v_02, ..., v_0n],[v_11, ..., v_1n],...,[v_m1,..., v_mn]]

        Returns:
        ---------
        new_listed_list: List(List(variables))
            eg: [[v_1, v_01, .. v_0n], [v_1, v_11,..], ..., [v_1, v_m1,...],
                 [v_2, v_01,.. v_0n], .... [v_k, v_m1, ..v_mn]]

    """

    new_listed_list = []
    if len(listed_list):
        for item in new_list:
            for l in listed_list:
                new_list = [item]
                new_list.extend(l)
                new_listed_list.append(new_list)
        if len(new_list) == 0:
            new_listed_list = listed_list
    else:
        new_listed_list = [[item] for item in new_list]

    return new_listed_list


def round_str_convert( str_val ):
    """ Rounding to get the best approximate float representation of a string.

        Parameters:
        -----------
        str_val : Str

    """

    value = float(str_val)
    if value != 0.0:
        exp_value = numpy.ceil(numpy.log10(value))
        return value*10**exp_value*10**-exp_value
    else:
        return 0.0

# Test
if __name__ == '__main__':
    testing_part = 'range_data'
#    testing_part = 'rounding'
    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')

    if testing_part == 'range_data':
        file_dict = {'global': os.path.join(tests_dir, 'data',
                                            'global_user_ranges.txt'),
                     'project': os.path.join(tests_dir, 'data',
                                             'project_ranges.txt')}
        range_dict = load_range_files(file_dict)

        for k in range_dict['units'].keys():
            print k,range_dict['units'][k]
        print 'USER:'
        for k in range_dict['user'].keys():
            print k,range_dict['user'][k]

    if testing_part == 'rounding':
        print round_str_convert('3.4')
        print round_str_convert('49')
        print round_str_convert('0.09')


### EOF ------------------------------------------------------------------------
