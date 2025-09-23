"""Account-related models for API"""

from typing import List, Optional

from pydantic import BaseModel, Field


class Account(BaseModel):
    """Account information"""

    accountId: str
    accountName: Optional[str] = None
    productTypeCd: Optional[str] = None
    productTypeName: Optional[str] = None
    currency: Optional[str] = None
    accountType: Optional[str] = None


class StockAccount(BaseModel):
    """Stock account information"""

    accountId: Optional[str] = None
    accountName: Optional[str] = None
    currency: Optional[str] = None
    productTypeCd: Optional[str] = None
    productTypeName: Optional[str] = None
    afAcctNoExt: Optional[str] = None
    enafAcctNoext: Optional[str] = None
    accountType: Optional[str] = None
    isFcbond: Optional[str] = None
    proInvestor: Optional[str] = None
    commandType: Optional[str] = None
    vsdStatus: Optional[str] = None


class DerAccount(BaseModel):
    """Derivatives account information"""

    accountId: Optional[str] = None
    accountName: Optional[str] = None
    productTypeCd: Optional[str] = None
    productTypeName: Optional[str] = None
    custId: Optional[str] = None
    dmaType: Optional[str] = None
    status: Optional[str] = None
    vsdStatus: Optional[str] = None
    careBy: Optional[str] = None
    isNet: Optional[str] = None
    isBank: Optional[str] = None
    dmaStatus: Optional[str] = None
    isAutoDeposit: Optional[str] = None
    isAutoWithdraw: Optional[str] = None
    dtaType: Optional[str] = None
    custType: Optional[str] = None
    proInvestor: Optional[str] = None
    afAcctNoExt: Optional[str] = None
    enafAcctNoext: Optional[str] = None


class AccountsListResponse(BaseModel):
    """Account list response"""

    custodyCd: Optional[str] = None
    stockAccount: List[StockAccount] = None
    derAccount: List[DerAccount] = None
    accountType: Optional[str] = None
    idType: Optional[str] = None
    careBy: Optional[str] = None
    brokerNo: Optional[str] = None
    fatca: Optional[str] = None
    online: Optional[str] = None
    margin: Optional[str] = None
    bond: Optional[str] = None
    advance: Optional[str] = None
    sms: Optional[str] = None
    taxCode: Optional[str] = None
    nationality: Optional[str] = None
    investorType: Optional[str] = None


class AvailableTradeResponse(BaseModel):
    """Available trading capacity response"""

    pp0: Optional[int] = Field(None, description="Sức mua")
    ppse: Optional[int] = Field(None, description="Sức mua cơ bản")
    maxBuyQty: Optional[int] = Field(None, description="Khối lượng mua tối đa")
    maxSellQty: Optional[int] = Field(None, description="Khối lượng bán tối đa")
    mrRatioLoan: Optional[float] = Field(None, description="Tỷ lệ vay")
