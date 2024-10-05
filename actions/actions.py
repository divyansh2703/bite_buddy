from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from spellchecker import SpellChecker
import mysql.connector
import uuid

class ActionPlaceOrder(Action):
    def name(self) -> Text:
        return "action_place_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        spell = SpellChecker()
        dish_name = tracker.get_slot("dish_name")
        quantity = tracker.get_slot("quantity")

        # Correct spelling of dish_name
        corrected_dish_name = spell.correction(dish_name)

        # Generate a unique order ID
        order_id = str(uuid.uuid4())

        # Connect to MySQL database
        connection = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="1234",
            database="bitebuddy"
        )

        cursor = connection.cursor()

        # Insert order into the database
        cursor.execute(
            "INSERT INTO orders (order_id, dish_name, quantity, order_status) VALUES (%s, %s, %s, %s)",
            (order_id, corrected_dish_name, quantity, 'Pending')
        )
        connection.commit()
        cursor.close()
        connection.close()

        dispatcher.utter_message(text=f"Your order {order_id} for {quantity} {corrected_dish_name} has been placed.")

        return []

class ActionTrackOrder(Action):
    def name(self) -> Text:
        return "action_track_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        order_id = tracker.get_slot("order_id")

        # Connect to MySQL database
        connection = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="1234",
            database="bitebuddy"
        )

        cursor = connection.cursor()

        # Retrieve order status
        cursor.execute("SELECT order_status FROM orders WHERE order_id = %s", (order_id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        if result:
            dispatcher.utter_message(text=f"Your order {order_id} is {result[0]}.")
        else:
            dispatcher.utter_message(text=f"Order {order_id} not found.")

        return []

class ActionAskOffer(Action):
    def name(self) -> Text:
        return "action_ask_offer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Connect to MySQL database
        connection = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="1234",
            database="bitebuddy"
        )

        cursor = connection.cursor()

        # Retrieve current offers
        cursor.execute("SELECT description, discount_percentage FROM offers WHERE valid_until >= CURDATE()")
        offers = cursor.fetchall()
        cursor.close()
        connection.close()

        if offers:
            offers_text = "\n".join([f"{description}: {discount_percentage}% off" for description, discount_percentage in offers])
            dispatcher.utter_message(text=f"Current offers:\n{offers_text}")
        else:
            dispatcher.utter_message(text="There are no current offers.")

        return []
