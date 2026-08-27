from yoomoney import Authorize

Authorize(
      client_id="5FBB484019FB11D42459533C04A78238E042529A5489100B2F371E580B4FF83C",
      redirect_uri="https://t.me/custdevybot",
    client_secret='2A3A8420261D3D96361F7FD1AAD650AB760354009918EE9ADAF507555263A332D270A7787D7EAF700FEC02FE8F31042864DD2685A03F7745F9EACF255CAB883C',
      scope=["account-info",
             "operation-history",
             "operation-details",
             "incoming-transfers",
             "payment-p2p",
             "payment-shop",
             ]
      )