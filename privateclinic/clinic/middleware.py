import json
import requests
from django.http import JsonResponse


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/user/login/':
            body = request.body.decode('utf-8')
            jsondata = json.loads(body)
            data = {
                'client_id': 'tdBEzfTaLmHuVhjYG1GrufOpe3wU5e3tzpZT1UZl',
                'client_secret': 'OrxshyKZIFWR366hHu6BdwCmwBSCCqzIGNVpoPagT3miVab2yw3MpX2kZaTWEDqbKcLZUa8ydBES1jTAK0SXx9yyekIxU1yOz39vshuY5E0n8hRVj4G2BBUHBRHVpYGZ',
                'username': jsondata.get('username'),
                'password': jsondata.get('password'),
                'grant_type': jsondata.get('grant_type')
            }

            headers = {'Content-Type': 'application/json'}
            response = requests.post('http://127.0.0.1:8000/o/token/', data=json.dumps(data), headers=headers)
            content = response.json()
            return JsonResponse(content, status=response.status_code)

        response = self.get_response(request)

        return response
