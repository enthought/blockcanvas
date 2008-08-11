Design Philosophies
===================

  **Create Usable Functionality Quickly.  Iterate.**
      Plan your work so that progress is visible quickly.  Try and get features
      out and visible to customers (even internal ones) as quickly as possible.
      We (and others) have found that the UI always needs re-work once it
      sees actual use.  APIs are similar.  It is critical to get feedback
      quickly and iterate.

      Strive for obvious and measurable progress on a daily or weekly basis.
      Monthly breaks between demonstrable progress just will not work.

  **Stay focused**
      Work on a single feature at a time, and get it working.  Check it in.
      Move on.

      Of course if you get stuck mentally or because of other issues, by all
      means, work on something else for a while.  Just don't get in a pattern
      of juggling six unfinished tasks at once.

  **Checkin Often**
      Check-in new functionality often.  This should usually be multiple
      (even many) times a day and at least once a day.  If you find it hard
      to do this, try dividing your work into smaller tasks.  If you repeat
      this process and keep your focus, you'll be able to do this.

      Checking in often allows others to see if your changes integrate well
      with what they are doing.  It also allows others to gage to completeness
      of features.

  **Keep a diary**
      Keep a diary of design decisions and thoughts during development.  This
      doesn't need to be a polished thesis.  Stream of concious is fine.  But
      it is important to explain why you've made certain decisions and
      whether you've rejected others.  This can be guidance to other developers
      using your code, and it also can serve as the beginnings of
      documentation.

  **Copious "Fixme" comments**
      If you take a short-cut, tell people about it.  If you aren't sure if
      something is the best design.  Leave a note for others.  It is very
      useful to know which code segements have been thoroughly thought through
      and which ones just "make it work."

  **Small functions**
      Try to keep functions in the 5-20 line range.  Martin always says
      something like "one thought per function", and I like this idea.  If you
      have more than one for loop, or several serial if statements, it is a
      candidate for splitting up.  This makes it easier for others to read your
      code, and helps you see opportunities for refactoring and re-use.

  **Minimize code**
      Try to use as little code as possible to accomplish your task.  Elegant
      design helps with this.  It is also helpful to learn the features of
      traits like @on_trait_change, mapped traits, and other tricks.
      Make sure you know why every function is in your code/class is there.  If
      you don't, stop and document it or delete it.  Don't leave superfluous
      functions/methods that others will assume are important when they read
      your code.  Everything should have a purpose.

  **Doc Strings**
      Write Docstrings for your functions, classes, and methods.  It is almost
      always useful, even for one line functions.  There are cases where they
      actually distract from readability (a bunch of one-line state transition
      functions for handling mouse events comes to mind), but the case is rare.
      Examples using doctest are great as well.  They serve as documentation
      as well as test your code.

  **Simple Examples**
      Make short examples that will run your algorithms or test your UIs at the
      end their modules in the __main__ or in utility functions.  This makes
      it possible to test/debug them outside of the main application quickly,
      and it provides an example to others on how to use your code. It also
      provides some enforcment of simplicity and minimal coupling on your
      design.  You just can't make a 10 line example that will run as a test
      if your object(s) can only operate within some huge infrastructure.

  **Write for other to read**
      Someone else is going to read your code.  Write it to make their job
      as easy as possible.  Beyond simple design, documentation, etc., also
      use common idioms that are common to the language or to Enthought.
      Don't use idioms that are only common to you.  If you find a new idiom
      useful, discuss it with others before using it a lot.
      Organize your methods by interface.  Follow the coding standard.

  **Unit Tests**
        Write unit tests and run them often -- every checkin.  It forces you to
        think about the interface to your API.  Writing your application to
        maximize testability generally helps its design and it helps you focus
        on minimizing superflous "clutter" in your code.
        Test driven development is good in the long run because it can help
        quickly find errors and problems during refactors.  Writing
        tests does take some time, but my experience has been that you can
        do a reasonable testing job simply in the course of your development.
        You are testing when you develop already.  Simply take the extra
        few minutes to put these in a unit test or a doctest so that it
        is available to posterity.

        BUT Don't get carried away here and fool yourself into believing the
        quality of your code is completely determined by the code coverage.
        Tests are important, but they are not the end application.  Spending
        huge amounts of time to ensure full coverage is often less valuable
        than getting

        ALSO I have found that tests are sometimes a burden.  It is a code
        base that has to be maintained, and if you change your design
        completely, then your tests may have to be re-implemented completely.
        Sometimes this investment can prevent you from making design changes
        that you should.  Stive to strike a balance that maximizes the speed
        you get features out to the customer and also ensure the application
        is robust.

        By the way, most UI code can be unit tested.  Strive to design your
        code so that the majority of it can be tested automatically.

  **Don't Repeat Yourself (DRY)**
      If you find yourself having to repeat the same information in multiple
      places, its a signal of trouble down the line.  It is confusing to
      others who read your code, and you have to remember to make changes in
      multiple places as the code evolves.  See if you can rethink your design
      to minimize the repeated code.  I mention this pitfall specifically,
      because it has bitten us in the past.

      The one possible exception to this is the definition of interface files.
      These files help document the code and codify what is required of
      implementors for their code to work.


  **Generalize when you can, but don't get bogged down**
      Try and abstract the problem you are solving up a level or two.  What
      "class" of problems is it in?  Can you write your code to solve the
      general class instead of just the specific problem without significantly
      more effort?  If so, do it.

      BUT... Don't get bogged down.  We want to deliver functionality quickly
      so that it can be user tested.  Working hard on abstractions that slow
      this process down is not always a good idea.  There are no hard and fast
      rules here.  Learning how to strike this balance is a real art, and you
      should work at it every day.

  **Watch code metrics**
      * How big is your code base?
      * What are the ratios:
              * code to comments?
              * code to test code?
              * UI code to library code?
      * What kind of coverage do you have?
      * How much memory does your app use on start up?
          Why so much?
      * How long does it take for your application to start up?
        Why so long?
      I don't have strong rule of thumbs for these, but you'd like to keep
      your coverage high and your code base small while getting the
      functionality of your application covered.
