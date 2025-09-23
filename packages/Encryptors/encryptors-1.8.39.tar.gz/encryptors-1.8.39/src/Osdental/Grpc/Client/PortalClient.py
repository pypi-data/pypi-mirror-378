import grpc
from Osdental.Models.Response import Response
from Osdental.Decorators.Retry import grpc_retry
from Osdental.Grpc.Generated import Common_pb2
from Osdental.Grpc.Generated import Portal_pb2_grpc
from Osdental.Shared.Config import Config

class PortalClient:

    def __init__(self, host=Config.SECURITY_GRPC_HOST, port=Config.SECURITY_GRPC_PORT):
        url = f'{host}:{port}' if port else host
        self.channel = grpc.aio.insecure_channel(url)
        self.stub = Portal_pb2_grpc.PortalStub(self.channel)

    @grpc_retry
    async def get_legacy(self) -> Response:
        request = Common_pb2.Empty()
        return await self.stub.GetLegacy(request)
    

    @grpc_retry
    async def validate_auth_token(self, request, metadata) -> Response:
        request = Common_pb2.Request(data=request)
        return await self.stub.ValidateAuthToken(request, metadata=metadata)
