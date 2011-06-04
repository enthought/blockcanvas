""" Utility functions for testing experiments """



from blockcanvas.app.experiment import Experiment
from blockcanvas.app.project import Project
from enthought.contexts.api import DataContext


#-------------------------------------------------------------------------------
# Comparison functions
# TODO: Integrate these somehow into their respective classes.  (This is
#       tricky because for some of these objects, different use cases imply
#       different interpretations of equality.)
#-------------------------------------------------------------------------------

def compare_contexts(a, b):
    if a is None or b is None:
        return False
    if (a.name != b.name) or (a.defer_events != b.defer_events):
        return False

    if hasattr(a, "subcontexts"):
        if a.subcontexts != b.subcontexts:
            return False
    elif hasattr(b, "subcontexts"):
        return False
    elif a != b:
        return False
    return True

def compare_experiments(p, q):
    if (p.name != q.name) or not compare_exec_model(p.exec_model, q.exec_model) \
            or not compare_canvas(p.canvas, q.canvas) \
            or not compare_contexts(p._local_context, q._local_context):
        return False
    else:
        return True

def compare_exec_model(a, b):
    # FIXME: add deep compares of statements and blocks; right now they just
    # revert to simple id comparison, which is uselsss.
    #self.assert_(a.statements == b.statements)
    #self.assert_(a.block == b.block)
    #self.assert_(a.body == b.body)
    return (a.code == b.code)

def compare_canvas(c, d):
    for node in c.graph_controller._nodes.keys():
        if d.graph_controller.saved_node_positions[node.uuid] != \
                c.graph_controller.saved_node_positions[node.uuid]:
            return False
    return True

def compare_projects(p, q):
    if len(p.contexts) != len(q.contexts):
        return False
    for i, ctx in enumerate(p.contexts):
        if not compare_contexts(ctx, q.contexts[i]):
            return False

    if len(p.experiments) != len(q.experiments):
        return False
    for j, exp in enumerate(p.experiments):
        if not compare_experiments(exp, q.experiments[j]):
            return False

    if p.active_experiment is not None:
        if q.active_experiment is None:
            return False
        elif not compare_experiments(p.active_experiment, q.active_experiment):
            return False

    for attr in ("CONFIG_SPEC", "PROJECT_FILE_NAME"):
        if getattr(p, attr) != getattr(q, attr):
            return False

    return True



#-------------------------------------------------------------------------------
# Factory functions
#-------------------------------------------------------------------------------

SAMPLE_CODE_1 = \
"""
def foo(x,y):
    return x+y
d = foo(a,b)
"""

SAMPLE_CODE_2 = \
"""
def bar(p, q, r):
    return p + q - r / 2.0
d = bar(a,b,c)
"""

def create_simple_experiment():
    """ Returns a simple experiment with a basic context in it """

    ctx = DataContext(name="main")
    ctx["b"] = 3
    ctx["c"] = 5
    return Experiment(code=SAMPLE_CODE_1, shared_context=ctx)

def create_simple_project():
    """ Returns a simple project with a single experiment and a single context """

    ctx = DataContext(name="main")
    ctx["a"] = 5
    ctx["b"] = 7
    ctx["c"] = 11
    proj = Project(contexts = [ctx])

    exp = Experiment(code=SAMPLE_CODE_1, shared_context=ctx)
    proj.add_experiment(exp)

    return proj

def create_multi_experiment_proj():
    """ Returns a project with two contexts and two experiments.
    """

    ctx = DataContext(name="main")
    ctx["a"] = 5
    ctx["b"] = 7
    ctx["c"] = 11

    ctx2 = DataContext(name="secondary")
    ctx2["a"] = 4
    ctx2["b"] = 16
    ctx2["c"] = 32
    ctx2["m"] = 64
    ctx2["n"] = 128
    proj = Project(contexts = [ctx, ctx2])

    e1 = Experiment(code=SAMPLE_CODE_1, shared_context=ctx)
    e2 = Experiment(code=SAMPLE_CODE_2, shared_context=ctx)
    proj.experiments = [e1, e2]

    return proj


