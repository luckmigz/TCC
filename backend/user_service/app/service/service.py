import asyncio
import json
from models.models import User
from shared.messaging.publisher import publish_event
from shared.messaging.subscriber import subscribe_to_event, purge_queue

TIMEOUT = 5  # segundos

# Função base reutilizável
async def _request_response(request_queue: str, response_queue: str, payload: dict):
    try:
        await publish_event(request_queue, json.dumps(payload))
        response = await asyncio.wait_for(subscribe_to_event(response_queue), timeout=TIMEOUT)
        
        if response is None or not isinstance(response, dict):
            raise ValueError("Resposta inválida do serviço")

        return response

    except asyncio.TimeoutError:
        raise TimeoutError("Tempo limite excedido aguardando resposta")
    except Exception as e:
        raise ValueError(f"Erro no fluxo request-response: {str(e)}")
    finally:
        try:
            await purge_queue(response_queue)
        except Exception as e:
            print(f"Erro ao limpar fila: {e}")


async def create_user(user: User) -> User:
    response = await _request_response("request_user_create", "response_user_create", user.dict())

    if response.get("cpf") == user.cpf:
        raise ValueError("Usuário com este CPF já existe")

    return User(**response)

async def get_user_email(email: str) -> User:
    payload = {"email": email}
    response = await _request_response("request_user_get_email", "response_user_get_email", payload)

    if "email" not in response:
        raise ValueError("Usuário não encontrado")

    return User(**response)
async def get_user_cpf(cpf: str) -> User:
    payload = {"cpf": cpf}
    response = await _request_response("request_user_get_cpf", "response_user_get_cpf", payload)

    if "cpf" not in response:
        raise ValueError("Usuário não encontrado")

    return User(**response)


async def update_user(user: User) -> User:
    response = await _request_response("request_user_update", "response_user_update", user.dict())

    if "error" in response:
        raise ValueError("Erro ao atualizar usuário")

    return User(**response)

async def delete_user(email: str) -> dict:
    payload = {"email": email}
    response = await _request_response("request_user_delete", "response_user_delete", payload)

    if not response.get("success", False):
        raise ValueError("Erro ao deletar usuário")

    return response
