"""
Database Schemas for ViralCoin Mini App

Each Pydantic model represents a collection in MongoDB.
Collection name is the lowercase of the class name.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional


class Miniapp(BaseModel):
    """
    Mini apps submitted to the store
    Collection name: "miniapp"
    """
    name: str = Field(..., min_length=2, max_length=80, description="App name")
    description: str = Field(..., min_length=10, max_length=300, description="Short description")
    url: HttpUrl = Field(..., description="Public URL to open the mini app")
    icon: Optional[HttpUrl] = Field(None, description="Optional app icon URL")
    author: Optional[str] = Field(None, description="Wallet address or name of the author")
    tags: Optional[list[str]] = Field(default_factory=list, description="Tags for discovery")


class Transferlog(BaseModel):
    """
    Logs of transfers initiated via the ViralCoin mini app
    Collection name: "transferlog"
    """
    from_pubkey: str = Field(..., description="Sender wallet address (base58)")
    to_pubkey: str = Field(..., description="Recipient wallet address (base58)")
    amount_sol: float = Field(..., gt=0, description="Amount in SOL")
    signature: Optional[str] = Field(None, description="Transaction signature if available")
    network: str = Field("mainnet-beta", description="Solana cluster: devnet/testnet/mainnet-beta")
    note: Optional[str] = Field(None, description="Optional memo or note")
