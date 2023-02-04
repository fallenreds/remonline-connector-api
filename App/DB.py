import sqlite3
import json


class DBConnection:
    def __init__(self, dbpath):
        self.connection = sqlite3.connect(dbpath)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def list_shopping_cart(self, telegram_id=None):
        telegram_filter = ""
        if telegram_id:
            telegram_filter = "where telegram_id = {0}".format(telegram_id)

        self.cursor.execute("select * from shopping_cart {0} ".format(telegram_filter))
        data = [dict(ix) for ix in self.cursor.fetchall()]
        return data

    def update_shopping_cart_count(self, cart_id, count):
        self.cursor.execute("""
            update shopping_cart
            set 'count' = {0}
            where id = {1} 
            """.format(count, cart_id))
        self.connection.commit()

    def delete_shopping_cart(self, cart_id):
        self.cursor.execute(f"""
            delete from shopping_cart
            where id=(?); """, (cart_id,))
        self.connection.commit()

    def post_shopping_cart(self, telegram_id: int, good_id: int, count: int = 1):
        self.cursor.execute(f""" 
            insert into shopping_cart ('telegram_id', 'good_id', 'count')
            values(?,?,?)""", (telegram_id, good_id, count))
        self.connection.commit()

    def get_all_orders(self, telegram_id=None):
        filter = ''
        if telegram_id:
            filter = "where telegram_id = {0}".format(telegram_id)
        self.cursor.execute("select * from orders {0}".format(filter))
        return [dict(ix) for ix in self.cursor.fetchall()]

    def post_orders(self,
                    telegram_id: int,
                    goods_list: str,
                    name: str,
                    last_name: str,
                    prepayment: bool,
                    phone: str,
                    nova_post_address: str,
                    is_paid: bool,
                    description: str = None,
                    ttn: str = None
                    ):

        self.cursor.execute(f"""
            insert into orders 
                (telegram_id, 
                goods_list, 
                'name', 
                last_name, 
                prepayment, 
                phone, 
                nova_post_address, 
                is_paid, 
                description, 
                ttn )
                
            values (?,?,?,?,?,?,?,?,?,?)""", (
            telegram_id,
            goods_list,
            name,
            last_name,
            prepayment,
            phone,
            nova_post_address,
            is_paid,
            description,
            ttn
        )
                            )
        self.connection.commit()
