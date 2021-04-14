# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
from typing import Any, Text, Dict, List
import json
from pathlib import Path

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.events import SlotSet, AllSlotsReset

class GetMenu(Action):
    knowledge = Path("data/menu.json").read_text()

    def name(self) -> Text:
        return "action_get_menu"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        menu = json.loads(self.knowledge)

        dispatcher.utter_message(response="utter_menu")

        dishes = "\n"
        for dish in menu['main_dish']:
            dishes += (f"{dish['name']} \t\t\t\t ${dish['price']}\n")
        dispatcher.utter_message(text=f"Main Dishes: {dishes}\n\n")
        
        dishes = "\n"
        for dish in menu['soups_and_stews']:
            dishes += (f"{dish['name']} \t\t\t\t ${dish['price']}\n")
        dispatcher.utter_message(text=f"Soups & Stews: {dishes}\n\n")

        dishes = "\n"
        for dish in menu['protein']:
            dishes += (f"{dish['name']} \t\t\t\t ${dish['price']}\n")
        dispatcher.utter_message(text=f"Proteins: {dishes} \n\n")
        
        dishes = "\n"
        for dish in menu['side_dish']:
            dishes += (f"{dish['name']} \t\t\t\t ${dish['price']}\n")
        dispatcher.utter_message(text=f"Side Dishes: {dishes}\n\n")

        dispatcher.utter_message(text="Please let me know when you're ready to order. If you are not interested in any dish, please respond with 'none'")

        return []

class ActionCheckExistence(Action):
    knowledge = Path("data/food_names.txt").read_text().split("\n")

    def name(self) -> Text:
        return "action_check_existence"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        for blob in tracker.latest_message['entities']:
            if blob['entity'] == 'food_name':
                name = blob['value'].lower()
                if name in self.knowledge:
                    dispatcher.utter_message(text=f"Yes, we have {name} on the menu.")
                else:
                    dispatcher.utter_message(
                        text=f"Sorry, I do not recognize {name}. It's not on the menu today.")
        return []

class ValidateOrderForm(FormValidationAction):

    knowledge = Path("data/menu.json").read_text()
    menu = json.loads(knowledge)

    def name(self) -> Text:
        return "validate_order_form"

    @staticmethod
    def main_dishes(menu) -> List[Text]:
        mainDishNames = []
        for item in menu['main_dish']:
            mainDishNames.append(item['name'].lower())
        return mainDishNames

    @staticmethod
    def soups(menu) -> List[Text]:
        soupsAndStews = []
        for item in menu['soups_and_stews']:
            soupsAndStews.append(item['name'].lower())

        return soupsAndStews

    @staticmethod
    def proteins(menu) -> List[Text]:
        proteins = []
        for item in menu['protein']:
            proteins.append(item['name'].lower())

        return proteins

    @staticmethod
    def sides(menu) -> List[Text]:
        sideDishes = []
        for item in menu['side_dish']:
            sideDishes.append(item['name'].lower())

        return sideDishes

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer."""

        try:
            int(string)
            return True
        except ValueError:
            return False

    def validate_main_dish(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        if value.lower() in self.main_dishes(self.menu):
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"main_dish": value}
        elif value.lower() == 'none':
            return {"main_dish": "none"}
        else:
            dispatcher.utter_message(response="utter_wrong_main_dish")
            return {"main_dish": None}

    def validate_soups_and_stew(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        if value.lower() in self.soups(self.menu):
            return {"soups_and_stew": value}
        elif value.lower() == 'none':
            return {"soups_and_stew": "None"}
        else:
            dispatcher.utter_message(response="utter_wrong_soups")
            return {"soups_and_stew": None}

    def validate_protein(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        if value.lower() in self.proteins(self.menu):
            return {"protein": value}
        elif value.lower() == 'none':
            return {"protein": "None"}
        else:
            dispatcher.utter_message(response="utter_wrong_protein")
            return {"protein": None}

    def validate_side_dish(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        if value.lower() in self.sides(self.menu):
            return {"side_dish": value}
        elif value.lower() == 'none':
            return {"side_dish": "None"}
        else:
            dispatcher.utter_message(response="utter_wrong_side")
            return {"side_dish": None}

class AddOrder(Action):
    def name(self) -> Text:
        return "action_update_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        orders = tracker.get_slot('orders')
        if not orders:
            orders = []
    
        order = {}

        order['main_dish'] = tracker.get_slot('main_dish')
        order['soups'] = tracker.get_slot('soups_and_stew')
        order['protein'] = tracker.get_slot('protein')
        order['side_dish'] = tracker.get_slot('side_dish')

        orders.append(order)
        
        return [AllSlotsReset(), SlotSet("orders", orders)]

class CancelOrder(Action):
    def name(self) -> Text:
        return "action_cancel_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [AllSlotsReset()]

class RestartOrder(Action):
    def name(self) -> Text:
        return "action_restart_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [AllSlotsReset()]

class CalculateBill(Action):
    knowledge = Path("data/menu.json").read_text()

    def name(self) -> Text:
        return "action_calculate_bill"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        menu = json.loads(self.knowledge)

        totalAmount = 0

        cart = ""
        orders = tracker.get_slot('orders')
        for order in orders:
            for k,v in order.items():
                if k == "main_dish":
                    for dish in menu['main_dish']:
                        value = dish['name']
                        if value.lower() == v.lower():
                            cart += (f"{dish['name']} \t\t\t\t ${dish['price']}\n")
                            totalAmount += dish['price']

                if k == "soups":
                    for dish in menu['soups_and_stews']:
                        value = dish['name']
                        if value.lower() == v.lower():
                            cart += (f"{dish['name']} \t\t\t\t ${dish['price']}\n")
                            totalAmount += dish['price']

                if k == "protein":
                    for dish in menu['protein']:
                        value = dish['name']
                        if value.lower() == v.lower():
                            cart += (f"{dish['name']} \t\t\t\t ${dish['price']}\n")
                            totalAmount += dish['price']
                
                if k == "side_dish":
                    for dish in menu['side_dish']:
                        value = dish['name']
                        if value.lower() == v.lower():
                            cart += (f"{dish['name']} \t\t\t\t ${dish['price']}\n")
                            totalAmount += dish['price']

        dispatcher.utter_message(text=f"Thanks! Your order is:\n {cart}")
        return [SlotSet("total_amount", totalAmount)]

        