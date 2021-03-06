""" #todo if this file stays anemic (say, under 30 lines) for like six
months from #born, consider just adding this one method to parent
"""


def func(listener, port):
    from contextlib import contextmanager as cm

    from microservice_lib.tcp_ip_client import \
        open_dictionary_based_tcp_ip_client_via as func
    opened = func(listener, port)

    @cm  # idk
    def cm():
        with opened as impl:
            yield _Client(impl)
    return cm()


class _Client:

    def __init__(self, impl):
        self._impl = impl

    def file_changed(
            self, agnostic_change_type, watched_dir, path_that_changed=None):
        cmd_args = {
            'agnostic_change_type': agnostic_change_type,
            'watched_dir': watched_dir,
            'path_that_changed': path_that_changed,
        }
        return self.send_API_call('filesystem_changed', cmd_args)

    def ping(self, args):
        return self.send_API_call('ping', {'args': args})

    def send_API_call(self, command_name, cmd_args):
        dct = {'command_name': command_name, 'command_args': cmd_args}
        return self.send_dictionary(dct)

    def send_dictionary(self, *rest):
        return self._impl.send_dictionary(*rest)

# #born
