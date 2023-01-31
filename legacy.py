# def get_categories(self) -> dict:
#     """
#     Возвращает список категорий
#     """
#     api_path = "warehouse/categories/"
#     required = {"token": self.token}
#     request_url = self._url_builder(api_path)
#
#     response = self.get(url=request_url, params=required)
#     return response.json()
#
# def get_goods(self, warehouse, **kwargs) -> dict:
#     api_path = f"warehouse/goods/{warehouse}"
#     required = {"token": self.token}
#     request_url = f"{self.domain}{api_path}"
#     with open('goods_params.json') as f:
#         optional = json.load(f)
#
#     data = self.set_params(required, optional, **kwargs)
#     response = self.get(url=request_url, params=data)
#     return response.json()
#
# def get_warehouse(self, **kwargs):
#     api_path = "warehouse/"
#     token = self.get_user_token()
#     required = {"token": token}
#     request_url = f"{self.domain}{api_path}"
#     response = requests.get(url=request_url, params=required)
#     return response.json()
#
# def get_main_warehouse_id(self):
#     return self.get_warehouse().get("data")[0].get('id')