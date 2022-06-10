from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class MarketPage(Page):

    @staticmethod
    def live_method(player, data):
        message_type = data['message_type']
        response = {}
        if message_type == 'add_order':
            player.group.add_order(player.id_in_group, data)

        # Update page
        response = {
            'message_type': message_type,
            'data': player.group.update_order_book()
        }
        return {0: response}


page_sequence = [MarketPage]
