"""
endpoints.py
Defines the endpoints used by the Qubic RPC.
This facilitates the centralization of routes and their possible future update.
"""

LATEST_TICK = '/latestTick'

BROADCAST_TRANSACTION = '/broadcast-transaction'

APPROVED_TRANSACTIONS_FOR_TICK = '/ticks/{tick}/approved-transactions'

TICK_DATA = '/ticks/{tick}/tick-data'

WALLET_BALANCE = '/balances/{id}'

STATUS = '/status'

CHAIN_HASH = '/ticks/{tick}/chain-hash'

QUORUM_TICK_DATA = '/ticks/{tick}/quorum-tick-data'

STORE_HASH = '/ticks/{tick}/store-hash'

TRANSACTION = '/transactions/{tx_id}'

TRANSACTION_STATUS = '/tx-status/{tx_id}'

TRANSFER_TRANSACTIONS_PER_TICK = '/identities/{id}/transfer-transactions'

HEALTH_CHECK = '/healthcheck'

COMPUTORS = '/epochs/{epoch}/computors'

QUERY_SC = '/querySmartContract'

TICK_INFO = '/tick-info'

ISSUED_ASSETS = '/assets/{identity}/issued'

OWNED_ASSETS = '/assets/{identity}/owned'

POSSESSED_ASSETS = '/assets/{identity}/possessed'

BLOCK_HEIGHT = '/block-height'

LATEST_STATS = '/latest-stats'

RICH_LIST = '/rich-list'

# ASSETS

ASSETS_ISSUANCE = '/assets/issuances'

ASSETS_ISSUANCE_INDEX = '/assets/issuances/{index}'

ASSETS_OWNERSHIPS = '/assets/ownerships'

ASSETS_OWNERSHIPS_INDEX = '/assets/ownerships/{index}'

ASSETS_POSSESSIONS = '/assets/possessions'

ASSETS_POSSESSIONS_INDEX = '/assets/possessions/{index}'

ASSETS_OWNERS = '/issuers/{issuer_identity}/assets/{asset_name}/owners'