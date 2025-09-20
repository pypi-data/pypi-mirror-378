from osbot_fast_api.api.routes.Routes__Set_Cookie                      import Routes__Set_Cookie
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API           import Serverless__Fast_API
from mgraph_ai_service_cache.config                                    import FAST_API__TITLE
from mgraph_ai_service_cache.fast_api.routes.Routes__Delete            import Routes__Delete
from mgraph_ai_service_cache.fast_api.routes.Routes__Exists            import Routes__Exists
from mgraph_ai_service_cache.fast_api.routes.Routes__Info              import Routes__Info
from mgraph_ai_service_cache.fast_api.routes.Routes__Namespace         import Routes__Namespace
from mgraph_ai_service_cache.fast_api.routes.Routes__Retrieve          import Routes__Retrieve
from mgraph_ai_service_cache.fast_api.routes.Routes__Server            import Routes__Server
from mgraph_ai_service_cache.fast_api.routes.Routes__Admin__Storage    import Routes__Admin__Storage
from mgraph_ai_service_cache.fast_api.routes.Routes__Store             import Routes__Store
from mgraph_ai_service_cache.utils.Version                             import version__mgraph_ai_service_cache



class Service__Fast_API(Serverless__Fast_API):
    title   = FAST_API__TITLE
    version = version__mgraph_ai_service_cache

    def setup_routes(self):
        self.add_routes(Routes__Admin__Storage)
        self.add_routes(Routes__Store         )
        self.add_routes(Routes__Retrieve      )
        self.add_routes(Routes__Exists        )
        self.add_routes(Routes__Delete        )
        self.add_routes(Routes__Namespace     )
        self.add_routes(Routes__Server        )
        self.add_routes(Routes__Info          )
        self.add_routes(Routes__Set_Cookie    )
        #self.add_routes(Routes__Cache     )         # to remove one all methods have been refactored out

    # def setup_middlewares(self):
    #     super().setup_middlewares()
    #
    #     return self


# # todo: see if we need to refactor this into Fast_API since the current routes are working ok for this project (for string, bytes and dict)
# intercept the bytes submitted here
#self.app().add_middleware(BodyReaderMiddleware)

# from fastapi import Request
# from starlette.middleware.base import BaseHTTPMiddleware
# class BodyReaderMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         if request.method in ["POST", "PUT", "PATCH"]:                              # Only read body for certain methods
#             body = await request.body()
#             request.state.body = body                                               # Store it in request state for later sync access
#         else:
#             request.state.body = None
#
#         response = await call_next(request)
#         return response


