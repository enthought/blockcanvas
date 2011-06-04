""" Profiling an empty application to find the number of import calls
"""

def main():
    """ Method for running an empty application.

        Customize the builtin __import__ module to get the number of calls.
    """
    import __builtin__,sys
    import time

    global count
    global import_time, last_time, import_times

    count = 0
    import_time = 0

    last_time = time.time()
    start_time = last_time
    import_times = {}

    # Customize builtin __import__ module
    base_import = __builtin__.__import__
    def my_import(name, *args):
        global count
        global import_time, last_time, import_times
        count += 1
        module = base_import(name, *args)

        this_time = time.time()
        if import_times.has_key(name):
            import_times[name] += this_time-last_time
        else:
            import_times[name] = this_time-last_time
        import_time += this_time-last_time
        last_time = time.time()

        return module

    __builtin__.__import__ = my_import

    # Use a non-modal UI to make opening and closing the UI, non-interactive.
    # I have to import 'enthought' to get the namespace loaded. Not sure why,
    #    probably setuptools related
    import enthought
    from blockcanvas.app.block_application import BlockApplication
    d = BlockApplication(code = '')
    d.edit_traits(kind='nonmodal')

    print 'Number of import calls for an empty application = %d' % count
    print 'Unique modules imported = %d' % len(import_times)
    print 'Total time importing = %fs (%f%%)' % (import_time, import_time/(time.time() - start_time))

    def sort_times(left, right):
        return cmp(right[1], left[1])
    items = import_times.items()
    items.sort(sort_times)

    print 'top 10 imports in total time'
    for item in items[0:10]:
        print '   %s = %f' % (item[0], item[1])

    sys.exit(0)


if __name__ == '__main__':
    main()

