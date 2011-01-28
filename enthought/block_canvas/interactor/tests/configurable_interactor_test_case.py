""" Unit testing for configurable interactor.
"""

# Standard imports
import os, tempfile, unittest

# ETS imports
from enthought.blocks.api import Block

# Local imports
from enthought.contexts.api import DataContext, MultiContext
from enthought.block_canvas.interactor.configurable_interactor import \
    ConfigurableInteractor
from enthought.block_canvas.interactor.interactor_config import \
    InteractorConfig, VariableConfig, PlotConfig
from enthought.block_canvas.interactor.shadow_interactor import ShadowInteractor
from enthought.block_canvas.interactor.parametric_interactor import \
    ParametricInteractor
from enthought.block_canvas.interactor.stochastic_interactor import \
     StochasticInteractor


class ConfigurableInteractorTestCase(unittest.TestCase):
    """ Unit testing for ConfigurableInteractor
    """

    def setUp(self):
        code = "from enthought.block_canvas.debug.my_operator import add,mul\n"\
               "c = add(a, b)\n" \
               "d = mul(c, 2)\n" \
               "e = mul(c, 3)\n" \
               "f = add(d, e)\n" \
               "g = add(f, 3)\n" \
               "h = mul(g, f)\n" \
               "i = mul(g,h)"

        self.block=Block(code)

        # Context setup.
        self.context = MultiContext(DataContext(name='Data'),{})
        self.context['a'] = 1.0
        self.context['b'] = 2

        self.block.execute(self.context)

        # ConfigurableInteractor setup
        i_config = InteractorConfig(var_configs=[VariableConfig(name='a',
                                                         type='Shadow'),
                                                 VariableConfig(name='b',
                                                         type='Parametric'),
                                                 VariableConfig(name='c',
                                                         type='Shadow'),
                                                 VariableConfig(name='d',
                                                         type='Parametric'),
                                                 VariableConfig(name='e',
                                                   type='Stochastic: Constant'),
                                                 VariableConfig(name='f',
                                                   type='Stochastic: Gaussian'),
                                                 VariableConfig(name='g',
                                                 type='Stochastic: Triangular'),
                                                 VariableConfig(name='h',
                                                    type='Stochastic: Uniform'),
                                                 ])
        self.interactor = ConfigurableInteractor(interactor_config=i_config,
                                                 block=self.block,
                                                 context=self.context)

        # Temp dir
        self.temp_dir = tempfile.gettempdir()


    def test_build_vars(self):
        """ Does the interactor create the right traits for the types of
            of interactors
        """

        self.failUnless(isinstance(self.interactor.interactor_shadow,
                                   ShadowInteractor))
        self.failUnless(isinstance(self.interactor.interactor_parametric,
                                   ParametricInteractor))
        self.failUnless(isinstance(
           self.interactor.interactor_stochastic_constant,StochasticInteractor))
        self.failUnless(isinstance(
           self.interactor.interactor_stochastic_gaussian,StochasticInteractor))
        self.failUnless(isinstance(
           self.interactor.interactor_stochastic_triangular,
           StochasticInteractor))
        self.failUnless(isinstance(
           self.interactor.interactor_stochastic_uniform, StochasticInteractor))


    def test_load_project_ranges_for_shadow_interactor(self):
        """ Does loading ranges from file work for shadow interactor ?
        """

        child_int = self.interactor.interactor_shadow
        file_path = os.path.join(os.path.dirname(__file__), 'data',
                                 'project_ranges.txt')

        # Applying the ranges to the shadow interactor in the configurable
        # interactor
        self.interactor.load_ranges_from_files({'shadow':file_path})
        child_int._view_items()

        self.assertEqual(len(child_int.ranges.keys()), 42)
        self.assertAlmostEqual(child_int.input_a__high, 5)
        self.assertAlmostEqual(child_int.input_a__low, 3.4)
        self.assertEqual(child_int.input_a, self.context['a'])


    def test_save_project_ranges_for_shadow_interactor(self):
        """ Does saving ranges to file work for shadow interactor ?
        """

        child_int = self.interactor.interactor_shadow
        f_path = os.path.join(self.temp_dir,'test_save_ranges_for_shadow.txt')

        child_int._view_items()
        child_int.input_a__high = 5.0
        self.interactor.save_ranges_to_files({'shadow': f_path})

        # Read the saved file
        file_object = open(f_path, 'r')
        line = file_object.read()
        line = [name.strip() for name in line.split()]
        file_object.close()
        os.remove(f_path)

        # Check results
        self.assertEqual(len(line), 6)
        self.assertEqual(line[2], str(5.0))


    def test_load_project_ranges_for_parametric_interactor(self):
        """ Does loading ranges from file work for parametric interactor ?
        """

        child_int = self.interactor.interactor_parametric
        file_path = os.path.join(os.path.dirname(__file__), 'data',
                                 'project_ranges.txt')

        self.interactor.load_ranges_from_files({'parametric': file_path})
        child_int._view_items()

        self.assertEqual(len(child_int.ranges.keys()), 42)
        self.assertAlmostEqual(child_int.input_b.low, 1.0)
        self.assertAlmostEqual(child_int.input_b.high, 6.0)
        self.assertEqual(child_int.input_b.step, 0.0)
        self.assertEqual(child_int.input_b.input_value, self.context['b'])


    def test_save_project_ranges_for_parametric_interactor(self):
        """ Does saving ranges to file work for parametric interactor ?
        """

        file_path = os.path.join(self.temp_dir,
                                 'test_save_ranges_for_parametric.txt')

        child_int = self.interactor.interactor_parametric
        child_int._view_items()

        child_int.input_b.low = 2
        child_int.input_b.high = 3
        child_int.input_b.step = 0.5
        self.interactor.save_ranges_to_files({'parametric':file_path})

        # Read the saved file
        file_object = open(file_path, 'r')
        lines = file_object.readlines()
        lines = [line.split() for line in lines]
        file_object.close()
        os.remove(file_path)

        self.assertEqual(len(lines), 2)
        self.assertEqual(len(lines[0]), 4)
        self.assertEqual(len(lines[1]), 4)
        self.assertEqual(lines[0][1], str(2))
        self.assertEqual(lines[0][2], str(3))
        self.assertEqual(lines[0][3], str(0))


    def test_load_project_ranges_for_stochastic_constant_interactor(self):
        """ Does loading parameters from file work for stochastic interactor
            with constant distribution ?
        """

        child_int = self.interactor.interactor_stochastic_constant
        file_path = os.path.join(os.path.dirname(__file__), 'data',
                                 'stochastic_constant_ranges.txt')

        self.interactor.load_ranges_from_files({'stochastic_constant':
                                                file_path})
        child_int._view_items()
        self.assertEqual(child_int.input_e.distribution.value, 45)


    def test_save_project_ranges_for_stochastic_constant_interactor(self):
        """ Does saving parameters to file work for stochastic interactor with
            constant distribution ?
        """

        file_path = os.path.join(self.temp_dir,
                                 'test_save_ranges_for_stoch_constant.txt')

        child_int = self.interactor.interactor_stochastic_constant
        child_int._view_items()

        child_int.input_e.distribution.value = 37.5
        self.interactor.save_ranges_to_files({'stochastic_constant': file_path})

        # Read the saved file
        file_object = open(file_path, 'r')
        lines = file_object.readlines()
        lines = [line.split() for line in lines]
        file_object.close()
        os.remove(file_path)

        self.assertEqual(len(lines), 1)
        self.assertEqual(len(lines[0]), 2)
        self.assertEqual(lines[0][1], str(37.5))


    def test_load_project_ranges_for_stochastic_gaussian_interactor(self):
        """ Does loading parameters from file work for stochastic interactor
            with gaussian distribution ?
        """

        child_int = self.interactor.interactor_stochastic_gaussian
        file_path = os.path.join(os.path.dirname(__file__), 'data',
                                 'stochastic_gaussian_ranges.txt')
        self.interactor.load_ranges_from_files({'stochastic_gaussian':
                                                file_path})
        child_int._view_items()
        self.assertEqual(child_int.input_f.distribution.mean, 39)
        self.assertEqual(child_int.input_f.distribution.std, 3)


    def test_save_project_ranges_for_stochastic_gaussian_interactor(self):
        """ Does saving parameters to file work for stochastic interactor
            with gaussian distribution ?
        """

        file_path = os.path.join(self.temp_dir,
                                 'test_save_ranges_for_stoch_gaussian.txt')
        child_int = self.interactor.interactor_stochastic_gaussian
        child_int._view_items()

        child_int.input_f.distribution.mean = 200
        child_int.input_f.distribution.std = 0.5
        self.interactor.save_ranges_to_files({'stochastic_gaussian': file_path})

        # Read the saved file
        file_object = open(file_path, 'r')
        lines = file_object.readlines()
        lines = [line.split() for line in lines]
        file_object.close()
        os.remove(file_path)

        self.assertEqual(len(lines), 1)
        self.assertEqual(len(lines[0]), 3)
        self.assertEqual(lines[0][1], str(200.0))
        self.assertEqual(lines[0][2], str(0.5))


    def test_load_project_ranges_for_stochastic_triangular_interactor(self):
        """ Does loading parameters from file work for triangular interactor
            with triangular distribution ?
        """

        child_int = self.interactor.interactor_stochastic_triangular
        file_path = os.path.join(os.path.dirname(__file__), 'data',
                                 'stochastic_triangular_ranges.txt')
        self.interactor.load_ranges_from_files({'stochastic_triangular':
                                                file_path})
        child_int._view_items()
        self.assertEqual(child_int.input_g.distribution.mode, 44)
        self.assertEqual(child_int.input_g.distribution.low, 39)
        self.assertEqual(child_int.input_g.distribution.high, 49)


    def test_save_project_ranges_for_stochastic_triangular_interactor(self):
        """ Does saving parameters to file work for stochastic interactor
            with triangular distribution ?
        """

        file_path = os.path.join(self.temp_dir,
                                 'test_save_ranges_for_stoch_triangular.txt')
        child_int = self.interactor.interactor_stochastic_triangular
        child_int._view_items()

        child_int.input_g.distribution.mode = 40.0
        child_int.input_g.distribution.low = 30.0
        child_int.input_g.distribution.high = 50.0
        self.interactor.save_ranges_to_files({'stochastic_triangular':
                                              file_path})

        # Read the saved file
        file_object = open(file_path, 'r')
        lines = file_object.readlines()
        lines = [line.split() for line in lines]
        file_object.close()
        os.remove(file_path)

        self.assertEqual(len(lines), 1)
        self.assertEqual(len(lines[0]), 4)
        self.assertEqual(lines[0][1], str(40.0))
        self.assertEqual(lines[0][2], str(30.0))
        self.assertEqual(lines[0][3], str(50.0))


    def test_load_project_ranges_for_stochastic_uniform_interactor(self):
        """ Does loading parameters from file work for stochastic interactor
            with uniform distribution ?
        """

        child_int = self.interactor.interactor_stochastic_uniform
        file_path = os.path.join(os.path.dirname(__file__), 'data',
                                 'stochastic_uniform_ranges.txt')
        self.interactor.load_ranges_from_files({'stochastic_uniform':file_path})
        child_int._view_items()
        self.assertEqual(child_int.input_h.distribution.low, 40)
        self.assertEqual(child_int.input_h.distribution.high, 58)


    def test_save_project_ranges_for_stochastic_uniform_interactor(self):
        """ Does saving parameters to file work for stochastic interactor
            with uniform distribution ?
        """

        file_path = os.path.join(self.temp_dir,
                                 'test_save_ranges_for_stoch_uniform.txt')
        child_int = self.interactor.interactor_stochastic_uniform
        child_int._view_items()

        child_int.input_h.distribution.low = 30.0
        child_int.input_h.distribution.high = 50.0
        self.interactor.save_ranges_to_files({'stochastic_uniform': file_path})

        # Read the saved file
        file_object = open(file_path, 'r')
        lines = file_object.readlines()
        lines = [line.split() for line in lines]
        file_object.close()
        os.remove(file_path)

        self.assertEqual(len(lines), 1)
        self.assertEqual(len(lines[0]), 3)
        self.assertEqual(lines[0][1], str(30.0))
        self.assertEqual(lines[0][2], str(50.0))


    def test_load_global_ranges_with_project_ranges(self):
        """ Do global ranges get overwritten by the project settings ?
        """

        code = "from enthought.block_canvas.debug.my_operator import add,mul\n"\
               "d = mul(a, b)\n" \
               "e = mul(c, 3)\n" \
               "f = add(d,e)"
        self.block = Block(code)
        self.context['c'] = 2.0

        # This is to be done because the interactor doesn't get updated with
        # change in block.
        i_config = InteractorConfig(var_configs=[VariableConfig(name='a',
                                                 type='Shadow'),
                                         VariableConfig(name='b',
                                                 type='Parametric'),
                                         VariableConfig(name='c',
                                                 type='Shadow'),
                                         VariableConfig(name='d',
                                                 type='Parametric')])
        self.interactor = ConfigurableInteractor(block=self.block,
                                                 context=self.context,
                                                 interactor_config=i_config)

        child_int = self.interactor.interactor_shadow
        global_file_path = os.path.join(os.path.dirname(__file__), 'data',
                                        'global_user_range.txt')
        project_file_path = os.path.join(os.path.dirname(__file__), 'data',
                                         'project_ranges.txt')

        self.interactor.load_ranges_from_files({'shadow':project_file_path},
                                               {'shadow':global_file_path})
        child_int._view_items()

        # Range of a is obtained from the project settings and not the
        # global preferences
        self.assertAlmostEqual(child_int.input_a__low, 3.4)
        self.assertAlmostEqual(child_int.input_a__high, 5.0)

        self.assertNotEqual(child_int.input_a__low, 0.15)
        self.assertNotEqual(child_int.input_a__high, 9.3)

        # Range of c is obtained from the global preferences
        self.assertAlmostEqual(child_int.input_c__low, 2.0)
        self.assertAlmostEqual(child_int.input_c__high, 7.0)


    def test_load_global_ranges_without_project_ranges(self):
        """ Do global ranges get used when there are no project settings ?
        """

        code = "from enthought.block_canvas.debug.my_operator import add,mul\n"\
               "d = mul(a, b)\n" \
               "e = mul(c, 3)\n" \
               "f = add(d,e)"
        self.block = Block(code)
        self.context['c'] = 2.0

        # This is to be done because the interactor doesn't get updated with
        # change in block.
        i_config = InteractorConfig(var_configs=[VariableConfig(name='a',
                                                         type='Shadow'),
                                                 VariableConfig(name='b',
                                                         type='Parametric'),
                                                 VariableConfig(name='c',
                                                         type='Shadow'),
                                                 VariableConfig(name='d',
                                                         type='Parametric')])
        self.interactor = ConfigurableInteractor(block=self.block,
                                                 context=self.context,
                                                 interactor_config=i_config)

        child_int = self.interactor.interactor_shadow
        global_file_path = os.path.join(os.path.dirname(__file__), 'data',
                                        'global_user_range.txt')

        self.interactor.load_ranges_from_files({}, {'shadow':global_file_path})
        child_int._view_items()

        # Range of a is obtained from the project settings and not the
        # global preferences
        self.assertAlmostEqual(child_int.input_a__low, 0.15)
        self.assertAlmostEqual(child_int.input_a__high, 9.3)

        # Range of c is obtained from the global preferences
        self.assertAlmostEqual(child_int.input_c__low, 2.0)
        self.assertAlmostEqual(child_int.input_c__high, 7.0)


### EOF ------------------------------------------------------------------------
