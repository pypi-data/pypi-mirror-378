import base64
from typing import Union

import requests
import json

from .query import Query
from .response import Response


def headers(request: str = '', token: bytes = b'') -> dict[str, str]:
    return {
        'ixcsoft': request,
        'Authorization': 'Basic {}'.format(base64.b64encode(token).decode('utf-8')),
        'Content-Type': 'application/json'
    }

def uri(server: str, ssl: bool) -> str:
    server_host = 'https://' + server if ssl else 'http://' + server
    return server_host


class Connection:


    def __init__(self,
            server: str,
            token: bytes | str,
            table: str,
            ssl: bool = True):
        self._server: str = uri(server=server, ssl=ssl) + '/webservice/v1'
        self._token: bytes = token if isinstance(token, bytes) else token.encode('utf-8')
        self._table: str = table
        self._grid: list = []


    def where(self, query: Query) -> None:
        args: dict = query.args()
        self._grid.append({
            'TB': '{}.{}'.format(self._table, args['column']),
            'OP': args['operator'],
            'P': args['value']
        })


    def many(self,
            page: int = 1,
            rows: int = 20,
            sort_name: str = 'id',
            sort_order: str = 'asc') -> Response:

        payload: object = {
            'qtype': self._table,
            'query': '',
            'oper': '',
            'page': page,
            'rp': rows,
            'sortname': '{}.{}'.format(self._table, sort_name),
            'sortorder': sort_order,
            'grid_param': json.dumps(self._grid)
        }

        response = requests.post(
            url='{}/{}'.format(self._server, self._table),
            data=json.dumps(payload),
            headers=headers(request='listar', token=self._token)
        )

        return Response(response.text)


    def one(self, record_id: int) -> dict[str, Union[str, int, bool]] | None:
        
        connection = Connection(server=self._server, token=self._token, table=self._table)
        connection.where(query=Query(arg=f'id = "{record_id}"'))
        response = connection.many()

        if response.total() > 0:
            return response.records()[0]

        return None
