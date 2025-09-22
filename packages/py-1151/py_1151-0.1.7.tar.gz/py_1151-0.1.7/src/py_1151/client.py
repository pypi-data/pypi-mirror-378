from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, Dict, Optional, Tuple, List, Union
import requests


DEFAULT_BASE_URL = "https://api.1151.to"


def _prepare_metadata(metadata: Optional[Mapping[str, Any]]) -> Optional[Dict[str, Any]]:
    if metadata is None:
        return None
    if not isinstance(metadata, Mapping):
        raise TypeError("metadata must be a mapping representing a JSON object")

    metadata_dict = dict(metadata)
    if not all(isinstance(key, str) for key in metadata_dict.keys()):
        raise ValueError("metadata keys must all be strings")

    try:
        json.dumps(metadata_dict)
    except (TypeError, ValueError) as exc:
        raise ValueError("metadata must be JSON serializable") from exc

    return metadata_dict


class UTXO:
    """Represents a single UTXO entry."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def txid(self) -> str:
        return str(self._data.get("txid", ""))

    @property
    def vout(self) -> int:
        return int(self._data.get("vout", 0))

    @property
    def address(self) -> str:
        return str(self._data.get("address", ""))

    @property
    def amount_btc(self) -> float:
        return float(self._data.get("amount_btc", 0.0))

    @property
    def confirmations(self) -> int:
        return int(self._data.get("confirmations", 0))

    @property
    def script(self) -> str:
        return str(self._data.get("script", ""))

    @property
    def raw_data(self) -> Dict[str, Any]:
        return self._data.copy()

    def __repr__(self) -> str:
        return (
            f"UTXO(txid='{self.txid}', vout={self.vout}, "
            f"amount_btc={self.amount_btc}, confirmations={self.confirmations})"
        )


class Transaction:
    """Represents a single transaction entry."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data.get("transaction", data)

    @property
    def id(self) -> str:
        return str(self._data.get("id", ""))

    @property
    def created_at(self) -> Optional[int]:
        return self._data.get("created_at")

    @property
    def associated_wallet(self) -> str:
        return str(self._data.get("associated_wallet", ""))

    @property
    def direction(self) -> str:
        return str(self._data.get("direction", ""))

    @property
    def amount(self) -> str:
        return str(self._data.get("amount", ""))

    @property
    def asset(self) -> str:
        return str(self._data.get("asset", ""))

    @property
    def destination(self) -> str:
        return str(self._data.get("destination", ""))

    @property
    def testnet(self) -> bool:
        return bool(self._data.get("testnet", False))

    @property
    def content(self) -> str:
        return str(self._data.get("content", ""))

    @property
    def metadata(self) -> Optional[Dict[str, Any]]:
        metadata = self._data.get("metadata")
        if isinstance(metadata, dict):
            return metadata.copy()
        return None

    @property
    def success(self) -> bool:
        return bool(self._data.get("success", False))

    @property
    def raw_data(self) -> Dict[str, Any]:
        return self._data.copy()

    def __repr__(self) -> str:
        return (
            f"Transaction(id='{self.id}', asset='{self.asset}', "
            f"amount='{self.amount}', success={self.success})"
        )


class Wallet:
    """Represents a wallet object returned by the API."""

    def __init__(self, data: Dict[str, Any], client: Client) -> None:
        # The API nests wallet data inside {"wallet": {...}}
        self._data = data.get("wallet", data)
        self._client = client

    @property
    def id(self) -> str:
        return str(self._data.get("id", ""))

    @property
    def created_at(self) -> Optional[int]:
        return self._data.get("created_at")

    @property
    def wallet_name(self) -> str:
        return str(self._data.get("wallet_name", ""))

    @property
    def owned_by(self) -> str:
        return str(self._data.get("owned_by", ""))

    @property
    def address(self) -> str:
        return str(self._data.get("address", ""))

    @property
    def network(self) -> str:
        return str(self._data.get("network", ""))

    @property
    def testnet(self) -> bool:
        return bool(self._data.get("testnet", False))

    @property
    def last_used(self) -> Optional[int]:
        return self._data.get("last_used")

    @property
    def metadata(self) -> Optional[Dict[str, Any]]:
        metadata = self._data.get("metadata")
        if isinstance(metadata, dict):
            return metadata.copy()
        return None

    @property
    def raw_data(self) -> Dict[str, Any]:
        return self._data.copy()

    def send(
        self,
        destination: Union[str, Mapping[str, float]],
        asset: str,
        amount: Optional[float] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        btc_fee: Optional[Union[str, float]] = None,
        eth_fee: Optional[float] = None,
        eth_max_priority_fee_per_gas: Optional[float] = None,
        eth_max_fee_per_gas: Optional[float] = None,
    ) -> Tuple[bool, str]:
        """Send funds from this wallet.

        Supports both single-output and BTC multi-output transactions.
        - Single-output: provide `destination` as a string address and `amount`.
        - BTC multi-output: provide `destination` as a mapping of address->amount
          and omit `amount`.
        """
        return self._client.send_from_wallet(
            wallet_id=self.id,
            destination=destination,
            asset=asset,
            amount=amount,
            metadata=metadata,
            btc_fee=btc_fee,
            eth_fee=eth_fee,
            eth_max_priority_fee_per_gas=eth_max_priority_fee_per_gas,
            eth_max_fee_per_gas=eth_max_fee_per_gas,
        )

    def get_utxos(self) -> List[UTXO]:
        """Fetch UTXOs for this wallet. Wrapper around Client.get_utxos."""
        return self._client.get_utxos(wallet_id=self.id)

    def transactions(self) -> List[Transaction]:
        """Fetch transactions for this wallet."""
        return self._client.get_wallet_transactions(wallet_id=self.id)

    def __repr__(self) -> str:
        return (
            f"Wallet(id='{self.id}', wallet_name='{self.wallet_name}', "
            f"address='{self.address}', network='{self.network}', testnet={self.testnet})"
        )


class Client:
    """Client for interacting with api.1151.to"""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: float = 30,
        session: Optional[requests.Session] = None,
    ) -> None:
        if not isinstance(api_key, str) or not api_key:
            raise ValueError("api_key must be a non-empty string")
        self.api_key = api_key
        self.base_url = base_url or DEFAULT_BASE_URL
        self.timeout = timeout
        self.session = session or requests.Session()

    def _url(self, path: str) -> str:
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        payload["api_key"] = self.api_key
        resp = self.session.post(self._url(path=path), json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def create_wallet(
        self,
        name: str,
        network: str,
        testnet: bool,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Wallet:
        metadata_payload = _prepare_metadata(metadata=metadata)
        payload: Dict[str, Any] = {
            "wallet_name": name,
            "network": network,
            "testnet": testnet,
        }
        if metadata_payload is not None:
            payload["metadata"] = metadata_payload

        data = self._post(path="/wallet/create", payload=payload)
        return Wallet(data=data, client=self)

    def get_wallet(self, wallet_id: str) -> Wallet:
        try:
            data = self._post(path="/wallet/get", payload={"wallet_id": wallet_id})
            return Wallet(data=data, client=self)
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                empty_data = {
                    "wallet": {
                        "id": None,
                        "created_at": None,
                        "wallet_name": None,
                        "owned_by": None,
                        "address": None,
                        "network": None,
                        "testnet": None,
                        "last_used": None,
                        "metadata": None,
                    }
                }
                return Wallet(data=empty_data, client=self)
        raise

    def delete_wallet(self, wallet_id: str) -> None:
        self._post(path="/wallet/delete", payload={"wallet_id": wallet_id})

    def send_from_wallet(
        self,
        wallet_id: str,
        destination: Union[str, Mapping[str, float]],
        asset: str,
        amount: Optional[float] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        btc_fee: Optional[Union[str, float]] = None,
        eth_fee: Optional[float] = None,
        eth_max_priority_fee_per_gas: Optional[float] = None,
        eth_max_fee_per_gas: Optional[float] = None,
    ) -> Tuple[bool, str]:
        """Send funds from a wallet.

        - Single-output: `destination` is a string and `amount` is provided.
        - BTC multi-output: `destination` is a mapping {address: amount} and
          `amount` must be None.
        """
        metadata_payload = _prepare_metadata(metadata=metadata)

        payload: Dict[str, Any] = {
            "wallet_id": wallet_id,
            "asset": asset,
        }

        # Determine single vs multi-output
        if isinstance(destination, str):
            if amount is None:
                raise ValueError("amount is required when destination is a string")
            payload["destination"] = destination
            payload["amount"] = float(amount)
        elif isinstance(destination, Mapping):
            if amount is not None:
                raise ValueError(
                    "amount must not be used for multi-output (mapping) destination"
                )
            if asset.lower() != "btc":
                raise ValueError(
                    "multi-output destination is currently supported only for BTC"
                )

            # Validate and normalize mapping: keys as str, values as float
            dest_map: Dict[str, float] = {}
            for addr, amt in destination.items():
                if not isinstance(addr, str) or not addr:
                    raise TypeError(
                        "destination mapping keys must be non-empty strings"
                    )
                try:
                    amt_f = float(amt)  # type: ignore[arg-type]
                except (TypeError, ValueError) as exc:
                    raise TypeError(
                        "destination mapping values must be numeric"
                    ) from exc
                if amt_f <= 0:
                    raise ValueError("destination amounts must be greater than 0")
                dest_map[addr] = amt_f
            if not dest_map:
                raise ValueError("destination mapping must not be empty")
            payload["destination"] = dest_map
        else:
            raise TypeError(
                "destination must be a string or a mapping of address to amount"
            )

        if metadata_payload is not None:
            payload["metadata"] = metadata_payload
        if btc_fee is not None:
            # Accept string presets like "low" or numeric custom fees
            payload["btc_fee"] = btc_fee
        if eth_fee is not None:
            payload["eth_fee"] = float(eth_fee)
        if eth_max_priority_fee_per_gas is not None:
            payload["eth_max_priority_fee_per_gas"] = float(
                eth_max_priority_fee_per_gas
            )
        if eth_max_fee_per_gas is not None:
            payload["eth_max_fee_per_gas"] = float(eth_max_fee_per_gas)

        data = self._post(path="/wallet/send", payload=payload)
        success = data.get("result") == "ok"
        tx_id = str(data.get("tx_id", ""))
        return success, tx_id

    def get_utxos(self, wallet_id: str) -> List[UTXO]:
        """Get the list of UTXOs for a wallet."""
        data = self._post(path="/wallet/utxos", payload={"wallet_id": wallet_id})
        utxo_list = data.get("utxos", [])
        return [UTXO(data=utxo) for utxo in utxo_list]

    def get_transaction(self, tx_id: str) -> Transaction:
        data = self._post(path="/transaction/get", payload={"tx_id": tx_id})
        return Transaction(data=data)

    def get_wallet_transactions(self, wallet_id: str) -> List[Transaction]:
        data = self._post(
            path="/wallet/transactions", payload={"wallet_id": wallet_id}
        )
        transactions = data.get("transactions", [])
        return [Transaction(data=tx) for tx in transactions]
