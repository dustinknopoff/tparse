from tparse.CallbackURL import CallbackURL


class TestCallbackURLS:
    def test_add_param(self):
        cbu = CallbackURL()
        cbu.add_parameter('change', '3')
        assert cbu.parameters.pop('change') is '3'
