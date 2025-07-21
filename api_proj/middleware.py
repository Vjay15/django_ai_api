from api_proj.models import Keys
from user_agents import parse
from django.http import JsonResponse
import hashlib
import logging
logger = logging.getLogger(__name__)

class LoggingMiddleware:
    """
    Middleware to log requests and responses.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get IP address
        ip_address = self.get_client_ip(request)
        
        # Parse user agent for device and browser info
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        user_agent = parse(user_agent_string)
        
        # Extract device and browser information
        device = f"{user_agent.device.family} {user_agent.device.brand} {user_agent.device.model}".strip()
        browser = f"{user_agent.browser.family} {user_agent.browser.version_string}".strip()
        os_info = f"{user_agent.os.family} {user_agent.os.version_string}".strip()
        
        # Log comprehensive request information
        logger.info(
            f"Request: {request.method} {request.get_full_path()} | "
            f"IP: {ip_address} | "
            f"Browser: {browser} | "
            f"OS: {os_info} | "
            f"Device: {device} | "
            f"User-Agent: {user_agent_string}"
        )
        
        response = self.get_response(request)
        logger.info(f"Response: {response.status_code}")
        return response
    
    def get_client_ip(self, request):
        """
        Get the client's IP address from the request.
        Handles cases where the request is behind a proxy or load balancer.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Take the first IP if there are multiple (in case of multiple proxies)
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class SubdomMiddleware:
    """
    Middleware to handle subdomain routing.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split('.')
        if len(host) >= 2:
            if host[0] == 'opai':
                request.subdomain = 'openai'
            elif host[0] == 'op':
                if host[1] == 'soc':
                    request.subdomain = 'soc'
                elif host[1] == 'sci':
                    request.subdomain = 'sci'
                else:
                    print(request.get_host(),"3")
                    return JsonResponse(
                        {"error": "API does not exist"},
                        status=404
                    )
            else:
                print(request.get_host(),"2")
                return JsonResponse(
                    {"error": "API does not exist"},
                    status=404
                )
        else:
            print(request.get_host(),"1")
            return JsonResponse(
                {"error": "API does not exist"},
                status=404
            )

        response = self.get_response(request)
        return response

class APIKeyAuthMiddleware:
    """
    Middleware to authenticate API requests using API keys.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        api_key = request.headers.get('X-API-KEY')
        if api_key:
            try:
                key = Keys.objects.using(request.subdomain).get(key=api_key)
                if key:
                    request.is_authenticated = True
                    request.key = key
                else:
                    request.is_authenticated = False
                    logger.warning(f"Invalid API key used from IP: {request.META.get('REMOTE_ADDR')}")
            except Keys.DoesNotExist:
                logger.warning(f"Invalid API key used from IP: {request.META.get('REMOTE_ADDR')}")
                return JsonResponse(
                    {"error": "Invalid API key"},
                    status=401
                )
            
        else:
            logger.warning("API key required but not provided from IP: {}".format(request.META.get('REMOTE_ADDR')))
            return JsonResponse(
                {"error": "API key required"},
                status=401
            )
        
        response = self.get_response(request)
        return response

class HashedMiddleware:
    def __init__(self,get_response):
        self.get_response = get_response
    def __call__(self, request):
        # Get the API key from the request headers
        hash = request.headers.get('X-Content-Hash')
        if request.method == 'GET':
            response = self.get_response(request)
            return response
        if not hash:
            return JsonResponse(
                {"error": "X-Content-Hash header is required"},
                status=400
            )
        else:
            # Validate the hash
            computed_hash = hashlib.sha256(request.body).hexdigest()
            if hash != computed_hash:
                logger.warning(f"Invalid X-Content-Hash from IP: {request.META.get('REMOTE_ADDR')}")
                return JsonResponse(
                    {"error": "Invalid X-Content-Hash","hash": computed_hash, "content": request.body.decode('utf-8')},
                    status=400
                )
            else:
                return self.get_response(request)
