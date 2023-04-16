from functools import wraps

from stxsdk import StxClient, Selection, StxChannelClient
from stxsdk.exceptions import AuthenticationFailedException

from .exceptions import MarketsNotFoundException, OrderCreationFailure

# globally initiated StxClient object
CLIENT = StxClient()

# globally initiated StxChannelClient object
CHANNEL_CLIENT = StxChannelClient()

class TradingBotBase():
    def __requires_auth(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.authenticated:
                raise AuthenticationFailedException("Not authenticated!")
            return func(self, *args, **kwargs)
        return wrapper


    def __init__(self):
        self.authenticated = False


    def __init__(self, email, password):
        self.authenticate(email, password)


    def authenticate(self, email, password):
        print("Authenticating...")
        login_response = CLIENT.login(params={"email": email, "password": password})
        if 'success' not in login_response:
            print(f'Authentication failed! {login_response}')
            raise AuthenticationFailedException(login_response['message'])
        
        print('Authentication successful!')
        self.authenticated = True


    @__requires_auth
    def get_market_data(self, *args, **kwargs):
        """
        This function is populating the bot markets by executing the marketInfos API
        """
        print("Initiating to populate the market data")
        
        # Allow user to specify the selection fields or use the default ones
        selections = Selection(args, kwargs) if args or kwargs else Selection(
            "title",
            "shortTitle",
            "marketId",
            "eventType",
            "status",
            "maxPrice",
            "probability",
            "question",
            "eventStatus",
            "position",
            "price",
            bids=Selection("price", "quantity"),
            offers=Selection("price", "quantity"),
        )

        print("Executing the marketinfos API.")
        market_data = CLIENT.marketInfos(selections=selections)
        print("Received the market data.")
        if not market_data["success"]:
            msg = f"Failed to get markets with error: {market_data['errors']}"
            print(msg)
            raise MarketsNotFoundException(msg)

        market_data = market_data["data"]["marketInfos"]
        print(f"Received {len(market_data)} markets.")
        return {market["marketId"]: market for market in market_data}


    @__requires_auth
    def create_limit_order(self, market_id, quantity, price, action="BUY", order_type="LIMIT"):
            print(f"[{market_id}] Creating {order_type} order : {action} {quantity} @ {price}")
            # generate the request params for order creation
            params = {
                "userOrder": {
                    "marketId": market_id,
                    "orderType": order_type,
                    "action": action,
                    "quantity": quantity,
                    "price": price,
                }
            }
            order_response = CLIENT.confirmOrder(params=params)

            if not order_response["success"]:
                msg = f"Failed to create order! {order_response['message']}"
                print(msg)
                raise OrderCreationFailure(msg)
            
            order = order_response["data"]["confirmOrder"]['order']
            order_total = order['quantity'] * order["price"]
            print(f"Successfully created order {order['id']} (Total Price: {order_total})")
            
            return order


    @__requires_auth
    def cancel_order(self, order_id) -> bool:
        if not order_id:
            print("Invalid order id!")
            return False
    
        print(f"Cancelling order {order_id}")
    
        params = {"orderId": order_id}
        cancel_response = CLIENT.cancelOrder(params=params)
        if not cancel_response["success"]:
            print(f"Failed to cancel order! {cancel_response['message']}")
            return False

        print(f"Order succesfully cancelled")
        return True

