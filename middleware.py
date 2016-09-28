from django.http import HttpResponse


class SetTestCookie(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super(SetTestCookie, self).__init__()

    def __call__(self, request):
        request.session.set_test_cookie()  # when the user add something to cart, i need to auth
        print(request.session.test_cookie_worked())
        response = self.get_response(request)
        return response


class CheckTestCookie(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super(CheckTestCookie, self).__init__()

    def __call__(self, request):
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
            print(request.session.test_cookie_worked())
            response = self.get_response(request)
            return response
        else:
            return HttpResponse("Please enable cookies and try again.")
