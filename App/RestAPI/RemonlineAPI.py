import requests
import json

class BaseRemonline:

    def __init__(self, api_key):
        self.api_key = api_key
        self.domain = "https://api.remonline.app/"
        self.token = self.get_user_token()

    def _url_builder(self, api_path: str) -> str:
        return f"{self.domain}{api_path}"

    def get(self, url, params, **kwargs):
        response = requests.get(url=url, params=params, **kwargs)

        if response.status_code == 101:
            self.token = self.get_user_token()
            response = requests.get(url=url, params=params, **kwargs)

        if response.status_code == 200:
            return response

        if response.status_code == 500:
            return {"data": None, 'success': False}

    def post(self, url, data, **kwargs):
        response = requests.post(url=url, data=data, **kwargs)

        if response.status_code == 101:
            self.token = self.get_user_token()
            response = requests.post(url=url, data=data, **kwargs)

        if response.status_code == 200:
            return response

        if response.status_code == 500:
            return {"data": None, 'success': False}

    def get_user_token(self) -> str:
        data = {"api_key": self.api_key}
        api_path = "token/new"
        request_url = self._url_builder(api_path)
        response = requests.post(url=request_url, data=data)
        return response.json()["token"]

    def set_params(self, required: dict, optional: dict, **kwargs):
        """
        Сравнивает ключи kwargs с доступными опциональными ключами
        Если такой параметр существует в доступных параметрах вызывает метод params_builder
        который возвращает параметр в нужном виде
        """

        params = required
        for key in kwargs:
            if key in optional:
                new_param = self.params_builder(optional[key], key, kwargs[key])
                params.update(new_param)
        return params

    def get_objects(self, api_path, request_url: str, accepted_params_path: str = None, **kwargs):
        optional = None
        required = {"token": self.token}
        if accepted_params_path:
            with open(accepted_params_path) as file:
                optional = json.load(file)
        data = self.set_params(required, optional, **kwargs)
        response = self.get(url=request_url, params=data)
        return response.json()

    def required_builder(self, required):
        if required:
            return required.update({"token": self.token})
        return {"token": self.token}

    def post_objects(self, api_path, request_url: str, accepted_params_path: str = None, **kwargs):
        optional = None
        required = {"token": self.token}
        if accepted_params_path:
            with open(accepted_params_path) as file:
                optional = json.load(file)
        data = self.set_params(required, optional, **kwargs)
        response = self.post(url=request_url, data=data)
        return response.json()

    @staticmethod
    def params_builder(value_type, key, value):
        """
        Сравнивает значение из value_type из доступных параметров.
        В зависимости от значение добавляет нужную приставку, например:
        параметр names с value_type == "array", тогда на выходе будет {"names[]":value}
        Данные о value_type можно взять из файлов ..._params.json
        """
        if value_type == "array":
            key = f"{key}[]"
        return {key: value}


class RemonlineAPI(BaseRemonline):
    def get_branches(self, **kwargs):
        api_path = "branches/"
        request_url = self._url_builder(api_path)
        return self.get_objects(api_path=api_path,
                                request_url=request_url)

    def get_clients(self, **kwargs) -> dict:
        """
        Возвращает список клиентов.
        **kwargs принимает параметры для фильтрации key=value
        """
        api_path = "clients/"
        request_url = self._url_builder(api_path)
        return self.get_objects(api_path=api_path, accepted_params_path="RestAPI/params/clients_params.json", request_url=request_url,
                                **kwargs)

    def get_categories(self, **kwargs) -> dict:
        """
        Возвращает список категорий
        """
        api_path = "warehouse/categories/"
        request_url = self._url_builder(api_path)
        return self.get_objects(api_path=api_path, request_url=request_url, **kwargs)

    def get_goods(self, warehouse, **kwargs) -> dict:
        api_path = f"warehouse/goods/{warehouse}"
        request_url = f"{self.domain}{api_path}"
        return self.get_objects(api_path=api_path, accepted_params_path="RestAPI/params/goods_params.json", request_url=request_url,
                                **kwargs)

    def get_warehouse(self, **kwargs):
        api_path = "warehouse/"
        request_url = f"{self.domain}{api_path}"
        return self.get_objects(api_path=api_path, request_url=request_url, **kwargs)

    def get_main_warehouse_id(self):
        return self.get_warehouse().get("data")[0].get('id')

    def new_client(self, **kwargs):
        api_path = "clients/"
        request_url = f"{self.domain}{api_path}"
        return self.post_objects(api_path=api_path, accepted_params_path="RestAPI/params/new_client.json", request_url=request_url,
                                 **kwargs)

    def new_order(self, **kwargs):
        """

        :param branch_id:
        :param order_type:
        :param client_id:
        :param model:
        :return:
        """
        api_path = "order/"
        request_url = f"{self.domain}{api_path}"
        return self.post_objects(api_path=api_path,
                                 accepted_params_path="RestAPI/params/new_order.json",
                                 request_url=request_url,
                                 **kwargs)



