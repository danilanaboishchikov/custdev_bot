import random
import string
import config

from yoomoney import Quickpay, Client, History

client = Client(config.PAY_TOKEN) if config.PAY_TOKEN else None

def create_payment(price):
    if config.DEMO_MODE:
        label = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f'https://example.com/demo-payment/{label}', label
    if not config.PAY_TOKEN or not config.YOOMONEY_RECEIVER:
        raise RuntimeError('Set YOOMONEY_TOKEN and YOOMONEY_RECEIVER for real payments, or DEMO_MODE=1 for demo payments.')
    label = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    quickpay = Quickpay(
        receiver=config.YOOMONEY_RECEIVER,
        quickpay_form="shop",
        targets="Пополнение кошелька",
        paymentType="SB",
        label=label,
        sum=int(price),
    )

    print(quickpay.redirected_url)
    return quickpay.redirected_url, label


def check_payment(label, price):
    if config.DEMO_MODE:
        return True
    if client is None:
        return False
    history = client.operation_history(label=label)
    # Проверяем операции
    for operation in history.operations:
        print(operation.label, operation.amount)
        if operation.status == 'success':
            return True

    return False
