def dont_return_me_I_am_a_function(arg, arg2='string', arg3=1):
    """ A docstring
    """

    return True

def dont_return_me_either():
    pass

class GetTheOldStyleClass:
    def do_not_return_me_I_am_a_class_method(self):
        pass

class GetTheNewStyleClass(object):
    def do_not_return_me_I_am_also_a_class_method(self):
        pass

if __name__ == '__main__':
    def do_not_return_me_I_am_a_method_nested_in_main(self):
        pass

    class DoNotGetMeIamAClassInMain:
        pass
