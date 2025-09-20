from firstock.ordersNReport.modifyOrderFunctionality.execution import *


def modifyOrder(quantity, orderNumber, product, mkt_protection, triggerPrice, price, tradingSymbol, priceType, userId, retention):
    try:

        modifyOrder = FirstockModifyOrder(
            qty=quantity,
            orderNumber=orderNumber,
            trgprc=triggerPrice,
            prc=price,
            tradingSymbol=tradingSymbol,
            priceType=priceType,
            userId=userId,
            retention= retention,
            product= product,
            mkt_protection= mkt_protection
        ).firstockModifyOrder()

        return modifyOrder

    except Exception as e:
        print(e)
