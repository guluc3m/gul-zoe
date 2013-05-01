
import zoe

class BankDepositCmd:
    def __init__(self, withdrawal = False):
        self._listener = zoe.Listener(None, None, self, "localhost", 30000, True)
        self._withdrawal = withdrawal

    def execute(self, objects):
        money = objects["money"]
        concepts = objects["strings"]
        dates = objects["dates"]
       
        if len(money) != len(concepts):
            print("I can only handle as many amounts as concepts")
            return

        if len(dates) != 1 and len(dates) != len(money):
            print("I can only handle 1 date or as many as amounts")
            return

        for i in range(len(money)):
            amount, currency = money[i]
            what = concepts[i]

            if len(dates) == 1:
                date = dates[0]
            else:
                date = dates[i]

            if self._withdrawal:
                amount = str(0 - float(amount))

            print("bank entry on " + date + ": " + amount + " " + currency + " as " + what)
            params = {"dst":"banking", "tag":"entry", "date":date, "amount":amount, "what":what}
            msg = zoe.MessageBuilder(params).msg()
            self._listener.sendbus(msg)

