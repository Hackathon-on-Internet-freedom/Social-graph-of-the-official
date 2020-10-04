from aiohttp import request

from social_graph.schemas.responses import (
    VKProcedureResponse, VKProcedureResponseSchema, VKProcedureResponsePayload
)


class VK_API:
    def __init__(
        self, api_token: str, api_version: str = '5.120',
        base_url: str = 'https://api.vk.com'
    ):
        self.base_url = base_url
        self.api_token = api_token
        self.api_version = api_version

    async def request(
        self, *, method: str = None, params: dict = None,
        api_token: str = None, return_json: bool = True
    ) -> dict:
        params = {} if not params else params
        params['access_token'] = api_token or self.api_token
        params['v'] = self.api_version

        async with request(
            'post',
            self.base_url + '/method/' + method,
            params=params,
            raise_for_status=True,
        ) as response:
            return await (response.json() if return_json else response.text())

    async def request_procedure_call(
        self, procedure_name: str, params: dict = None
    ) -> VKProcedureResponsePayload:
        raw_response = await self.request(
            method=f'execute.{procedure_name}',
            params=params,
            return_json=False
        )
        api_response: VKProcedureResponse = \
            VKProcedureResponseSchema().loads(raw_response)
        if not api_response.error and not api_response.execute_errors:
            return api_response.response
        error = Exception(api_response.error or api_response.execute_errors)
        raise error
