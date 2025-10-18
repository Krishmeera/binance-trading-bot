
import tkinter as tk
from tkinter import messagebox
from bot import BasicBot
import logging
import threading
import time

logging.basicConfig(filename='logs/bot.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

class TradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Binance Futures Testnet Bot")
        self.build_ui()

    def build_ui(self):
        tk.Label(root, text="API Key").grid(row=0, column=0)
        self.entry_api = tk.Entry(root, width=40)
        self.entry_api.grid(row=0, column=1)

        tk.Label(root, text="API Secret").grid(row=1, column=0)
        self.entry_secret = tk.Entry(root, width=40)
        self.entry_secret.grid(row=1, column=1)

        tk.Label(root, text="Symbol").grid(row=2, column=0)
        self.entry_symbol = tk.Entry(root)
        self.entry_symbol.grid(row=2, column=1)

        tk.Label(root, text="Side").grid(row=3, column=0)
        self.side_var = tk.StringVar(root)
        self.side_var.set("BUY")
        tk.OptionMenu(root, self.side_var, "BUY", "SELL").grid(row=3, column=1)

        tk.Label(root, text="Order Type").grid(row=4, column=0)
        self.type_var = tk.StringVar(root)
        self.type_var.set("MARKET")
        tk.OptionMenu(root, self.type_var, "MARKET", "LIMIT", "STOP_MARKET").grid(row=4, column=1)

        tk.Label(root, text="Quantity").grid(row=5, column=0)
        self.entry_quantity = tk.Entry(root)
        self.entry_quantity.grid(row=5, column=1)

        tk.Label(root, text="Price (LIMIT)").grid(row=6, column=0)
        self.entry_price = tk.Entry(root)
        self.entry_price.grid(row=6, column=1)

        tk.Label(root, text="Stop Price (STOP_MARKET)").grid(row=7, column=0)
        self.entry_stop_price = tk.Entry(root)
        self.entry_stop_price.grid(row=7, column=1)

        tk.Button(root, text="Place Order", command=self.place_order).grid(row=8, column=1)
        tk.Button(root, text="Check Position", command=self.check_position).grid(row=9, column=0)
        tk.Button(root, text="Check Order Status", command=self.check_order_status).grid(row=9, column=1)

        self.status_label = tk.Label(root, text="", fg="blue")
        self.status_label.grid(row=10, column=0, columnspan=2)

        self.auto_refresh()

    def get_bot(self):
        api_key = self.entry_api.get()
        api_secret = self.entry_secret.get()
        return BasicBot(api_key, api_secret)

    def place_order(self):
        bot = self.get_bot()
        symbol = self.entry_symbol.get()
        side = self.side_var.get()
        order_type = self.type_var.get()
        quantity = float(self.entry_quantity.get())
        price = self.entry_price.get()
        stop_price = self.entry_stop_price.get()

        if order_type == "LIMIT" and price:
            response = bot.place_order(symbol, side, order_type, quantity, price=price)
        elif order_type == "STOP_MARKET" and stop_price:
            response = bot.place_order(symbol, side, order_type, quantity, stop_price=stop_price)
        else:
            response = bot.place_order(symbol, side, order_type, quantity)

        self.latest_order_id = response.get("orderId", None)
        messagebox.showinfo("Response", str(response))

    def check_position(self):
        bot = self.get_bot()
        symbol = self.entry_symbol.get()
        try:
            position = bot.client.futures_position_information(symbol=symbol)
            messagebox.showinfo("Position Info", str(position))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def check_order_status(self):
        if not hasattr(self, 'latest_order_id') or self.latest_order_id is None:
            messagebox.showwarning("No Order", "No recent order to check.")
            return
        bot = self.get_bot()
        symbol = self.entry_symbol.get()
        try:
            order = bot.client.futures_get_order(symbol=symbol, orderId=self.latest_order_id)
            messagebox.showinfo("Order Status", str(order))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def auto_refresh(self):
        def refresh():
            while True:
                try:
                    if hasattr(self, 'latest_order_id') and self.latest_order_id is not None:
                        bot = self.get_bot()
                        symbol = self.entry_symbol.get()
                        order = bot.client.futures_get_order(symbol=symbol, orderId=self.latest_order_id)
                        self.status_label.config(text=f"Status: {order['status']}")
                except Exception as e:
                    self.status_label.config(text="Auto-refresh error")
                time.sleep(5)

        threading.Thread(target=refresh, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = TradingApp(root)
    root.mainloop()
