from rest_framework import views, response, permissions


class HealthCheckView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, _):
        return response.Response("OK")
