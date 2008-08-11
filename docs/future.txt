Overview of work phases
=======================

Phase 1
-------
One week -- June 4-June 10 (with potential demo on Friday, June 8)
This phase should be a sprint to functionality.  We can miss on features, but
not on having the end-to-end app working by the milestone date.

There is no need to make it an envisage app unless that speeds things up.
I would prefer not to.

The big effort here is the solidifying the underlying workflow model, the
"shadow context" (or whatever it is called), and canvas controller.

* Several use-case workflows created.
DONE * Basic workflow model/persistence in place.
DONE * Basic to Good workflow editing through canvas and code.
DONE * Ability to search/add functions from library to canvas.
[Jaya] * Creation of new functions on the fly for a workflow.
[Eric] * Display of Context (tree) with Workflow
* Updating plot display of context. [ Not necessarily a geoplot]
* Interaction with some variables on context in a "dependent" or "shadow"
  context through a simple dialog that is built from the workflow and user
  specification.
* Real-time display of original and modified values on a plot.

Phase 2
--------
One week -- June 10-17

* Refactor based on what we learn and what is needed in Phase 3.
* *Always* keep the app working!!

Phase 3
---------
One week -- June 17-24

Once the basics are in place, we should explore the interations we want to be
able to have with a workflow once it is created:

* Stochastic runs
* Inversion -- will the converge tools and UIs work?
* Parametric studies
* Unit handling adapters and units UIs


Phase 4
---------
* Masking
* Auto-units
* Grouping of functions
* Workflow Debugging tools.
* Plot templates re-work.

Phase 5
--------
?

Phase 1 in Detail
-----------------

Basic workflow model/persistence in place
=========================================

What is the basic model of the ExecutionGraph?  Is it Blocks?  The problem is
that blocks currently hold dependency information, but they do not hold
information about what functions are part of the execution (unless they are
imported at the top of the script).  This makes some sense, but we want to be
able to match function names to functions.  In a

    * Workflow Graph Model (Blocks or otherwise)
        * What is the representation of a workflow graph?
          * Do Blocks hold enough information for us to synchronize edits
            between text and graph views?

          * How do we handle comments and formatting in text representation of
            graphs?

          * How do we store modifications to graphs?
            We'll need to be able to keep "deltas" to graphs for undo/redo
            capabilities and to re-construct the audit trail of changes to
            a graph as it evolves.

          * Deconstructing blocks based on dependence.
            Currently our graphs can have a variable that is both an input
            and output, and it will execute fine.  So the following is
            currently handled fine.

                vp = foo(vs)
                vp = bar(rhob)

            However, if a user puts a function down on the canvas and says its
            input is 'vp', where does it go?  After foo or after bar?  We need
            a way to allow either.

            This capability is important and will exist in our workflows
            because of masking even if we limit user ability to name variables
            the same.

            Dave P and Eric discussed some ideas of deconstructing workflows to
            deal with multiple output variables with the same names.

            +++ Dealing with this is one of my major worries in phase 1. +++



Primary Tasks/Questions
-----------------------

    * Use Cases Workflows
      We need to get several of these scripts (workflow graphs) written from
      the beginning to help drive the direction of our effort.
        * ProAVA (several of these)
        * Converge
            * Modified Hill
            * TSD
            * etc.

    * Workflow Graph Model (Blocks or otherwise)
        * What is the representation of a workflow graph?
          * Do Blocks hold enough information for us to synchronize edits
            between text and graph views?

          * How do we handle comments and formatting in text representation of
            graphs?

          * How do we store modifications to graphs?
            We'll need to be able to keep "deltas" to graphs for undo/redo
            capabilities and to re-construct the audit trail of changes to
            a graph as it evolves.

          * Deconstructing blocks based on dependence.
            Currently our graphs can have a variable that is both an input
            and output, and it will execute fine.  So the following is
            currently handled fine.

                vp = foo(vs)
                vp = bar(rhob)

            However, if a user puts a function down on the canvas and says its
            input is 'vp', where does it go?  After foo or after bar?  We need
            a way to allow either.

            This capability is important and will exist in our workflows
            because of masking even if we limit user ability to name variables
            the same.

            Dave P and Eric discussed some ideas of deconstructing workflows to
            deal with multiple output variables with the same names.

            +++ Dealing with this is one of my major worries in phase 1. +++

    * Units
        * Defining a standard way to put unit adapters between UIs
          (plots and dialogs for function entry etc) and underlying models
          across the entire app.

        * UIs for unit families and systems.

        * Grouping
            * How is grouping implemented?
              I think Blocks handle this pretty well -- it is just another
              Block.
            * We don't have the UI tools for grouping yet, although
              multi-selection is working pretty well.  So, adding this probably
              isn't hard once the underlying model is figured out.

        * Masking
            * How do we turn on a masks from a graph?
              We've discussed using the "with" statement, and that might be
              nice.
            * How do we visualize an area of a graph that is masked?
              Seems like a group box drawn around it might work fine with the
              text of the mask in a corner.
            * How does this coordinate with the underlying context?

        * Auto Units
            * Like masking, we may want to turn on auto-units in a Block so that
              users can type 'vp = 1.2' instead of /vp = UnitScalar(1.2, m/s)'.
              I think the implementation may be essentially the same as
              masking.

        * How is function lookup/storage handled in graphs?
          What function does the string 'foo' actually represent?  Where is this
          infromation stored?  In import statements "somewhere" in the graph or
          explicitly with each sub_block in a graph?

          Are import statements left as part of the graph or are they used to
          fill a "function lookup" dictionary that is carried around with the
          graph?

          How does this choice impact various aspects of workflows?
              * Re-usability?
              * Persistence?
              * Editing?
              * Refactoring by end users?
              * Robustness to user error? (Is the 'foo' function the user expects
                to execute actually going to execute?  Any chance the wrong foo
                will?)

        * Persistence
          How do we persist all this graph stuff for posterity?
          I think graphs should just be persisted as python code.  If we have
          UI layout, UI dialogs, default values, etc., these should be
          persisted separately in neighboring files to the python code.  That
          way, if something corrupts them, or re-factors break part of this
          code, it is always possible to read the simple execution model back
          in from the python code.  Simpler and safer.

    * Graph layout.
      * How do we persist graph layout information?  This should be separate
        from the actual execution function.
      * Can we incorporate user specified layout with our current layout
        scheme without significant effort?
      * Can we use our current layout algorithm to layout only portions of
        the (selected) nodes on a canvas?
      * Augment current algorithm to minimize crossover.
      * Augment current algorithm to have functions report their size (based
        on their name length, display state, or other factors) instead of
        having a one size fits all setting.

    * Workflow UI
        * Beautification of function display
            * Rounded corners with title bar and close buttons.
              Generally better looking function display.
            * expand to see code/inputs/outputs on canvas.
            * Dialogs for editing/creating/modifying functions.
                * How are units handled?  Can users just enter text like:
                    1.2 m/s and we'll parse them?  That would be nice.  How
                    is this then represented in the generated python code?
                * More error checking on variable bindings (ensure they are
                  a float, None, a quoted string, or a variable binding.
                  Is this right???

        * Controller/Selection design.
          On a canvas where users can only select a single item, the individual
          items on the canvas can handle many of the actions such as delete,
          move, etc.  On our canvas, users can select multiple function boxes on
          the canvas at a single time.  So instead of the canvas items
          implementing function like delete and move, they need to inform the
          canvas controller when users request such actions through them and let
          it handle the actual action.

          So, how do items on the canvas find the controller?  Is it a attribute
          that is set on them?  Do they ask their parent?  Currently,
          EnableFunctionBox has a controller property on it that looks for the
          controller by chaining up through its parent container.  Is this the
          best design?  (Even if it is, the method should move somewhere
          else...)  How about mutliple controllers being found?  Should we name
          this something besides "controller" (canvas_controller?).

          In a related issue, the selection manager is separate from the
          controller.  I am not sure if the selection management should be left
          to the controller instead of in the container.  Seems like it might be
          nicer.

        * Fixes of enable.
            * There is some strange hitch in drag operations that occasionally
              occurs.  Get rid of it.
            * Event handling order for enable containers needs a little work
              to mak
        * Unbound variables indicators on functions.
            * function displays should have an icon that indicates if there
              are unsatisfied inputs on a function -- if it has an active
              Context.  If the workflow is being edited without an active
              context (which should be possible), then these should not be
              active.

        * Dependency help.
          There should be a mode where, when a user clicks on a block, either
          all of the functions it depends on are highlighted, or all the
          functions it feeds are highlighted.

        * Gridlines on the canvas
        * Scroll bars on canvas
        * Zoomed out view of the canvas that shows the entire canvas -- not
          just the part being edited.  This should be a separate widget that
          can be viewed or hidden like the Variable View, Code View, etc.

        * Significant Debugging feedback
            * Usesrs can click on a graph edge to plot the values on it.

            * If users click on a value in the "Variable explorer UI", the
              functions on the canvas should temporarily "flash".  Also, the
              lines in the text display of the workflow should get a "highlight"
              color.

        * Expand Functions
          Users can see an expanded view of widgets showing input output ports
          and or code of function.  If a function is "expanded", an entire
          canvas relayout so that other functions move to make room.  It'd
          be really nice if this were animated.

        * Get rid of function dialogs
          I'd love for us to get rid of dialogs all together and have the
          function displays become the dialogs.  Users could expand multiple
          functions to see their code or input/output mappings at the same time.
          Some of the widgets we need would be easily implemented as Enable
          components if it proves to hard to embed native controls.

        * "Scissor" Tool
          Named for OpenGL Scissors which allow you to make a view port that
          displays different information in it as you move it around the
          canvas.  For example, a "code" scissors would show you the code
          for any function under the scissor box.  As the box moved away from
          the function, it would snap back to the standard view for the
          canvas.

        * Progress meter for long running workflows.
          This shouldn't prevent the user from viewing already calculated
          values.

    * Function Library
        * There are going to be several types of functions.  One approach would
          be to have:
            * Standard library functions.
            * User library functions.
            * Perhaps project or even graph specific functions that users
              may create.

          Other possbilities are to have groups of libraries for different
          regions (Gulf of Mexico, North Sea, Alaska, etc.)

        * Editing
          Users can't directly edit standard library functions, but they are
          likely to want to use a standard function as a template that they
          modify.  This should be simple.  They can edit the function, but
          the UI warns that the function is actually a new one in their user
          library.

          There are all sorts of re-factorings someone may want to do.  They
          find a bug in a standard function and want their user function to
          override it in all of their workflows (even existing ones that they
          pull up).

        * Searching
          All of these libraries are searchable.  Users should be able to add
          new modules or new directories to be searched for user functions.

          We already have a simple search mechanism, but it could be improved.
          The first step is to improve where it looks for functions and allowing
          the user to modify this through a UI.  The 2nd step is to have
          a full index search of the function docs.


        * Sharing workflows with others
          When sending a workflow to another person, we'll have to be careful
          to check for functions from the user's library that may need to
          ship along with the workflow.

        * Repositories.
          Users will want to upload/download functions fro

    * Contexts
        * Implementations on all of this should start light so that we can
          try things out fast.  Keep in mind that most of the work we need
          to do here only has to implement a small interface.  Working with
          this small interface and light weight implementations as we try
          things out will allow us to move quickly.  If we decide to use
          an existing implementation as we evolve, we can make that decision
          then.

        * How do we ensure Contexts can be as fast as possible?
          Ability to disable notification completely or queue notifications is
          critical.

          Note: We should never have the requirement that a Workflow operates
          only on one of our Contexts.  It should also work on a bare dictionary
          (or anything else with a dictionary interface) to provide maximum
          flexibility to the end user.  If we break this contract, we need a
          very very good reason to do it.

        * "Multi-contexts"
          In the original implementation of contexts, there was the ability
          to put two contexts next to each other and "chain together" lookup
          and control how assignments into the multi-context where parceled out
          into the various underlying contexts.  I believe this will be
          important again to control graph execution (default value context,
          data context, function lookup context for example) and probably
          other places.

        * "Dependent" or "Shadow" contexts.
          One version of a multi-context would be a "foreground" context
          that is "dependent" on a "background" context for some of its
          variables.  However, any new assignments that overwrite a variable
          that is in the "background" context is instead written into the
          "foreground" context.  Subsequent reads of this variable from the
          context would produce the value from the foreground instead of the
          background context.

          You can continue this process so that the foreground becomes the
          background context of another context, and so on.  I believe this
          is a handy way to deal with "trial" data scenarios, parametric
          studies, stochastic studies, as well as keeping historic data
          recoverable as a workflow evolves during user edits or whatever.

        * Index Grouping.
          Geophysics needs the concept of groups of variables that are
          associated with a particular index.  This is important for
          visualization

          Dan B. has implemented some code that should

        * Masking Adapters
          Get masks implemented.  These were partially implemented in the
          previous version of NumericContext, and getting them working again
          shouldn't be difficult.  I am more concerned about how they will
          be applied in the workflow graph than I am in their implementation
          here.

          For now, lets not worry about the complexity of a mask on one group
          applying to another.  Just get masks on a specific group working.
          A further step improvment might be to allow different masks for
          different groups active at the same time.

        * Auto-unit Adapters
          In a shell or interpreter prompt environment, and auto-uniting
          system can be helpful to a user.  If they type 'vs = 1.2' the
          system automatically assumes a set of units based on the name
          'vs'.  This is easy to do, and we should explore whether users
          like it.  Also, it may work its way into the way we write blocks.

        * Numeric Pipeline ideas
          All the notions of Numeric pipelines should be layered on top
          of contexts.  This will be very important to flexible/interactive
          graphics as we progress.  We'll leave this to a later phase of
          effort.

    * Context UI
        * Display a context in a simple treee UI.
          All the code from the original numeric context demo "should" work for
          this.  Just get a simple tree up and working.
        * Tie this to canvas so selecting items on tree will light up or
          temporarily flash the functions or ports that they are related to.

    * How do we couple tie a workflow and a context together for:

        * UI Display?
        * Persistence?

      And, how tightly coupled are these things anyway?  The looser the better
      I believe.

    * Plotting
        * Templates
        * Plotting the same data "ghosted" from different contexts for trial
          data.

    * ExecutionManagers
        * Interactor
        * Stochastic
        * Parametric
        * Inversion
        * Interpreter?

        * Storage mechanism for stochastic and parametric studies.

    * How can a user build/save a custom UI for:
        * Functions?
        * Workflows?



The Goal
--------

Phase I
-------


Building Models
---------------

Easy Exploration
================

Comparing Models
----------------

Auditing Results
----------------

Block Model
-----------

A function block needs to carry around the following information:

    1. The name and location of its underlying python function.
       The function provides the following:
           * The names of its input variables which are available by
             interogating the function.
           * The names of its output variables on the function.  This is a little
             trickier, but it is possible to do a "good job" by parsing the
             function and looking for its return argument.  Many many times this
             will be somthing like ``return (vp, vs)``, so you know that ``vp``
             and ``vs`` are the return variables.
             For functions that are decorated with has_units, it is even easier
             because the outputs are explicitly defined.
           * What is the import statement needed to get the function?
    2. The name of the function on the canvas (may differ from the actual name).

    3. The variables hooked up to (passed into) the function inputs.
    4. The variables hooked up to the function outputs.

