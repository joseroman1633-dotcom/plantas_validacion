from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = "registration/login.html"

    def get_success_url(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return "/admin/"
        return "/home2/"
