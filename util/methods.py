import aiohttp
from config import util_logger, logging
from urllib.parse import urljoin


def log_request(func):
    """Декоратор для логирования ответа от Утилы."""
    async def wrapper(*args, **kwargs):
        util_logger.info(f"Будет выполнен {func.__doc__}")
        message, lvl = await func(*args, **kwargs)
        if lvl == logging.ERROR:
            message = f"Утила вернула неуспешный статус и несмогла обработать задачу. {message}"
        elif lvl == logging.WARNING:
            message = f"Неуспешный ответ от сервиса: {message}"
        util_logger.log(msg=message, level=lvl)
        return message
    return wrapper


class Method(object):

    GET_EMAIL_ROUTE = '/support/api/{stand}/getProductEmail/{product_guid}'
    PUBLISH_INFO_ROUTE = '/support/api/{stand}/publishProductInfo/{product_guid}'
    RESET_REQUEST_ROUTE = '/support/api/{stand}/resetRequestStatus/{request_guid}'
    UPDATE_REQUEST_ROUTE = '/support/api/{stand}/updateRequest/{request_guid}'
    UPDATE_ABONENTS_ROUTE = '/support/api/{stand}/updateAbonents'

    def __init__(self, base_url: str, stand: str = 'prod'):
        self.base_url = base_url
        self.stand = stand

    @log_request
    async def get_email(self, product_guid: str) -> str:
        """запрос на получение email учетной записи по product guid."""
        url = urljoin(
            self.base_url, 
            self.GET_EMAIL_ROUTE.format(stand=self.stand, product_guid=product_guid))

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return await response.text(), logging.ERROR
                else:
                    response_dict = await response.json()
                    if response_dict['success']:
                        return response_dict['message']['email'], logging.INFO
                    else:
                        return response_dict['message'], logging.WARNING

    @log_request
    async def publish_info(self, product_guid: str) -> str:
        """запрос на публикацию информации об абоненте."""
        url = urljoin(
            self.base_url, 
            self.PUBLISH_INFO_ROUTE.format(stand=self.stand, product_guid=product_guid))

        async with aiohttp.ClientSession() as session:
            async with session.post(url) as response:
                if response.status != 200:
                    return await response.text(), logging.ERROR
                else:
                    response_dict = await response.json()
                    if response_dict['success']:
                        return response_dict['message'], logging.INFO
                    else:
                        return response_dict['message']['errorMessage'], logging.WARNING

    @log_request
    async def reset_request_status(self, request_guid: str) -> str:
        """запрос на сброс заявки в черновик."""
        url = urljoin(
            self.base_url, 
            self.RESET_REQUEST_ROUTE.format(stand=self.stand, request_guid=request_guid))

        async with aiohttp.ClientSession() as session:
            async with session.post(url) as response:
                if response.status != 200:
                    return await response.text(), logging.ERROR
                else:
                    return (await response.json())['message'], logging.INFO

    @log_request
    async def update_request_status(self, request_guid: str) -> str:
        """запрос на обновение статуса заявки."""
        url = urljoin(
            self.base_url, 
            self.UPDATE_REQUEST_ROUTE.format(stand=self.stand, request_guid=request_guid))

        async with aiohttp.ClientSession() as session:
            async with session.post(url) as response:
                if response.status != 200:
                    return await response.text(), logging.ERROR
                else:
                    response_dict = await response.json()
                    if response_dict['success']:
                        return response_dict['message'], logging.INFO
                    else:
                        return response_dict['message']['errorMessage'], logging.WARNING

    @log_request
    async def update_abonents(self, product_guid: str) -> str:
        """запрос на обновление абонента."""
        url = urljoin(self.base_url, self.UPDATE_ABONENTS_ROUTE.format(stand=self.stand))
        data = {'products': [f"{product_guid}"]}

        async with aiohttp.ClientSession() as session:
            async with session.put(url, json=data) as response:
                if response.status != 200:
                    return await response.text(), logging.ERROR
                else:
                    response_dict = await response.json()
                    if response_dict['success']:
                        message = ''
                        for key, value in response_dict['message'].items():
                            if value:
                                message += f'{key.capitalize()}: {value[0]}'

                        # Если обновления были, отдаем пользователю.
                        return message if message else 'Обновления не произошли.', logging.INFO
                    else:
                        return response_dict['message']['errors'], logging.WARNING
