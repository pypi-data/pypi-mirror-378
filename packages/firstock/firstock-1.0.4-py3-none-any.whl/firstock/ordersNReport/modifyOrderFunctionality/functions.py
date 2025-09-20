from firstock.Variables.common_imports import *
from firstock.ordersNReport.modifyOrderFunctionality.base import *


class ApiRequests(FirstockAPI):
    def firstockModifyOrder(self, qty, product, mkt_protection, orderNumber, trgprc, prc, tradingSymbol, priceType, userId, retention):
        """
        :return:
        """
        try:
            url = MODIFYORDER

            with open(CONFIG_PATH) as file:
                config_data = json.load(file)

            if userId in config_data:
                payload = {
                    "userId": userId,
                    "orderNumber": orderNumber,
                    "quantity": qty,
                    "price": prc,
                    "triggerPrice": trgprc,
                    "tradingSymbol": tradingSymbol,
                    "priceType": priceType,
                    "jKey": config_data[userId]['jKey'],
                    "retention":retention,
                    "mkt_protection": mkt_protection,
                    "product": product

                }

                result = requests.post(url, json=payload)
                jsonString = result.content.decode("utf-8")

                finalResult = ast.literal_eval(jsonString)

                return finalResult
            return not_logged_in_user()
        except Exception as e:
            print(e)
