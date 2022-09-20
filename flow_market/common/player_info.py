class Inventory:
    def __init__(self, quantity, price):
        self.quantity = quantity
        self.price = price


class PlayerInfo:
    def __init__(self):
        self.inventories = []
        self.cash = 0
        self.profit_from_trading = 0
        self.profit_from_contract = 0
        # The trading rate of the player
        self.rate = 0

    def update(self, direction, quantity, price, is_trade):
        self.rate = quantity
        remaining_quantity = quantity
        if direction == "buy":
            while (
                remaining_quantity
                and self.inventories
                and self.inventories[-1].quantity < 0
            ):
                # Fill short positions. Inventories are sorted by price in
                # a ascending order so the highest sold price inventory get
                # filled first.
                inv = self.inventories.pop()
                fill_quantity = min(-inv.quantity, remaining_quantity)
                remaining_quantity -= fill_quantity
                self.cash -= fill_quantity * price
                profit = fill_quantity * (inv.price - price)
                if is_trade:
                    self.profit_from_trading += profit
                else:
                    self.profit_from_contract += profit
                if -inv.quantity > fill_quantity:
                    self.inventories.append(
                        Inventory(inv.quantity + fill_quantity, inv.price)
                    )
            if remaining_quantity > 0:
                self.inventories.append(Inventory(remaining_quantity, price))
                self.cash -= remaining_quantity * price
                self.inventories.sort(reverse=True, key=lambda inv: inv.price)
        else:
            while (
                remaining_quantity
                and self.inventories
                and self.inventories[-1].quantity > 0
            ):
                # Fill long positions. Inventories are sorted by price in
                # a descending order so the lowest bought price inventory get
                # filled first.
                inv = self.inventories.pop()
                fill_quantity = min(inv.quantity, remaining_quantity)
                remaining_quantity -= fill_quantity
                self.cash += fill_quantity * price
                profit = fill_quantity * (price - inv.price)
                if is_trade:
                    self.profit_from_trading += profit
                else:
                    self.profit_from_contract += profit
                if inv.quantity > fill_quantity:
                    self.inventories.append(
                        Inventory(inv.quantity - fill_quantity, inv.price)
                    )
            if remaining_quantity > 0:
                self.inventories.append(Inventory(-remaining_quantity, price))
                self.cash += remaining_quantity * price
                self.inventories.sort(reverse=False, key=lambda inv: inv.price)

    def cover_position(self):
        # Cover any open positions at the end of the round
        if self.get_inventory() > 0:
            # If the player has any inventories left, sell them at price 0
            self.update("sell", self.get_inventory(), 0, is_trade=True)
        else:
            # If the player has any unfilled inventories, fill them at price 20
            self.update("buy", -self.get_inventory(), 20, is_trade=True)

    def get_inventory(self):
        inventory = 0
        for inv in self.inventories:
            inventory += inv.quantity
        return round(inventory, 2)

    def get_cash(self):
        return round(self.cash, 2)

    def get_rate(self):
        rate = self.rate
        # Reset the rate
        self.rate = 0
        return rate
