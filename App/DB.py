import sqlite3


class DBConnection:
    def __init__(self, dbpath):
        self.connection = sqlite3.connect(dbpath)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def post_client(self,
                    id_remonline,
                    telegram_id,
                    name,
                    last_name,
                    login,
                    password,
                    phone
                    ):
        self.cursor.execute(f"""
                    insert into client 
                        (id_remonline,
                        telegram_id,
                        'name',
                        last_name,
                        login,
                        password,
                        phone
                         )

                    values (?,?,?,?,?,?,?)""", (
            id_remonline,
            telegram_id,
            name,
            last_name,
            login,
            password,
            phone)

                            )

        self.connection.commit()

        return self.cursor.lastrowid

    def list_shopping_cart(self, telegram_id=None):
        telegram_filter = ""
        if telegram_id:
            telegram_filter = "where telegram_id = {0}".format(telegram_id)

        self.cursor.execute("select * from shopping_cart {0} ".format(telegram_filter))
        data = [dict(ix) for ix in self.cursor.fetchall()]
        return data

    def get_client_by_telegram_id(self, telegram_id):
        self.cursor.execute("""
            select * from client
            where telegram_id = {0}
        """.format(telegram_id))
        return self.cursor.fetchone()

    def get_client_by_id(self, client_id):
        self.cursor.execute("""
            select * from client
            where id= {0}
        """.format(client_id))
        return self.cursor.fetchone()

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

    def get_all_orders(self, telegram_id=None, order_id=None):
        filter = ''
        if telegram_id:
            filter = "where telegram_id = {0}".format(telegram_id)

        if order_id:
            filter = "where id = {0}".format(order_id)
        self.cursor.execute("select * from orders {0}".format(filter))
        return [dict(ix) for ix in self.cursor.fetchall()]

    def get_client_by_login(self, login: str):
        self.cursor.execute(f"""
        select * from client where login=?
        """, (login,))
        return self.cursor.fetchone()

    def update_client_telegram_id(self, client_id, new_id):

        self.cursor.execute(
            """
            update client
            set telegram_id = {0}
            where id = {1} 
            """.format(new_id, client_id)

        )

        self.connection.commit()

    def get_active_orders(self):
        self.cursor.execute(f"""
            select * from orders where is_completed=0
        """)
        return self.cursor.fetchall()

    def get_monthly_finished_orders(self, client_id):
        self.cursor.execute("""
                select * from orders where client_id={0} and is_completed=1
                and datetime(date) > datetime('now','-1 month')
                """.format(client_id))

        return self.cursor.fetchall()


    def deactivate_order(self, order_id):
        success = None
        try:
            self.cursor.execute(
                """
                update orders
                set 'is_completed' = 1
                where id = {0} 
                """.format(order_id,))
            success = True
            self.connection.commit()
        except Exception as error:
            print(error)
            success = False
        finally:
            return {"success": success}

    def delete_order(self, order_id):
        success = None
        try:
            self.cursor.execute(
                """
                delete from orders
                where id = {0} 
                """.format(order_id,))
            success = True
            self.connection.commit()
        except Exception as error:
            print(error)
            success = False
        finally:
            return {"success": success}

    def get_all_discounts(self):
        self.cursor.execute("""
            select * from discounts
        """)
        return self.cursor.fetchall()

    def no_paid_along_time(self):
        self.cursor.execute("""
                    select * from orders
                    where is_completed = 0 and is_paid=0 and prepayment=1 and datetime(date, '+1 hour') < datetime('now')
                """)
        return self.cursor.fetchall()

    def create_discount(self, procent, month_payment):
        success = True
        try:
            self.cursor.execute(
                """
                insert into discounts ('procent', 'month_payment')
                values(?, ?)
                """, (procent, month_payment))
            self.connection.commit()
        except Exception as error:
            success = False
            print(error)
        finally:
            return {"success": success}

    def delete_discount(self, discount_id):
        success = True
        try:
            self.cursor.execute(
                """
                delete from discounts
                where id=(?); """, (discount_id,)
            )
            self.connection.commit()
        except Exception as error:
            success = False
            print(error)
        finally:
            return {"success": success}


    def post_orders(self,
                    client_id: int,
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
                (
                client_id,
                telegram_id, 
                goods_list, 
                'name', 
                last_name, 
                prepayment, 
                phone, 
                nova_post_address, 
                is_paid, 
                description, 
                ttn,
                'date'
                 )
                
            values (?,?,?,?,?,?,?,?,?,?,?,datetime('now'))""", (
            client_id,
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

        return self.cursor.lastrowid
