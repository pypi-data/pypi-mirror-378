import pytest
from pydantic import ValidationError

from src.idosell.crm import _common, vouchers


# --- Tests for Enums
class TestStatusFullEnum:
    def test_valid_values(self):
        assert vouchers.StatusFullEnum.ALL == 'all'
        assert vouchers.StatusFullEnum.USED == 'used'
        assert vouchers.StatusFullEnum.UNUSED == 'unused'
        assert vouchers.StatusFullEnum.UNVERFIED == 'unverified'

class TestStatusEnum:
    def test_valid_values(self):
        assert vouchers.StatusEnum.USED == 'used'
        assert vouchers.StatusEnum.UNUSED == 'unused'


# --- Tests for DTOs
class TestVoucherModel:
    def test_valid(self):
        dto = vouchers.VoucherModel(
            id=1,
            number="V123456"
        )
        assert dto.id == 1
        assert dto.number == "V123456"

    def test_invalid_id_zero(self):
        with pytest.raises(ValidationError):
            vouchers.VoucherModel(
                id=0,
                number="V123456"
            )

class TestVoucherPostPutBaseModel:
    def test_valid(self):
        balance = _common.BalanceModel(amount=100.0, currency="USD")
        dto = vouchers.VoucherPostPutBaseModel(
            number="V123456",
            name="Test Voucher",
            expirationDate="2025-12-31",
            balance=balance,
            shops=[1, 2],
            note="Test note"
        )
        assert dto.number == "V123456"
        assert dto.balance.amount == 100.0

class TestVoucherPostModel:
    def test_valid(self):
        balance = _common.BalanceModel(amount=100.0, currency="USD")
        dto = vouchers.VoucherPostModel(
            number="V123456",
            name="Test Voucher",
            expirationDate="2025-12-31",
            balance=balance,
            shops=[1, 2],
            note="Test note",
            typeId=1
        )
        assert dto.typeId == 1

    def test_invalid_type_id_zero(self):
        balance = _common.BalanceModel(amount=100.0, currency="USD")
        with pytest.raises(ValidationError):
            vouchers.VoucherPostModel(
                number="V123456",
                name="Test Voucher",
                expirationDate="2025-12-31",
                balance=balance,
                shops=[1, 2],
                note="Test note",
                typeId=0
            )

class TestVoucherPutModel:
    def test_valid(self):
        balance = _common.BalanceModel(amount=100.0, currency="USD")
        dto = vouchers.VoucherPutModel(
            number="V123456",
            name="Test Voucher",
            expirationDate="2025-12-31",
            balance=balance,
            shops=[1, 2],
            note="Test note",
            id=1,
            balanceOperationType=_common.BalanceOperationTypeEnum.SET,
            status=vouchers.StatusEnum.UNUSED
        )
        assert dto.id == 1

    def test_invalid_id_zero(self):
        balance = _common.BalanceModel(amount=100.0, currency="USD")
        with pytest.raises(ValidationError):
            vouchers.VoucherPutModel(
                number="V123456",
                name="Test Voucher",
                expirationDate="2025-12-31",
                balance=balance,
                shops=[1, 2],
                note="Test note",
                id=0,
                balanceOperationType=_common.BalanceOperationTypeEnum.SET,
                status=vouchers.StatusEnum.UNUSED
            )

class TestPutBlockCrmVouchersParamsModel:
    def test_valid(self):
        dto = vouchers.PutBlockCrmVouchersParamsModel(
            id=1,
            number="V123456"
        )
        assert dto.id == 1

    def test_invalid_number_empty(self):
        with pytest.raises(ValidationError):
            vouchers.PutBlockCrmVouchersParamsModel(
                id=1,
                number=""
            )

class TestPutUnblockCrmVouchersParamsModel:
    def test_valid(self):
        vouchers_list = [vouchers.VoucherModel(id=1, number="V1")]
        dto = vouchers.PutUnblockCrmVouchersParamsModel(vouchers=vouchers_list)
        assert len(dto.vouchers) == 1

    def test_empty_vouchers_invalid(self):
        with pytest.raises(ValidationError):
            vouchers.PutUnblockCrmVouchersParamsModel(vouchers=[])

class TestDeleteCrmVouchersParamsModel:
    def test_valid(self):
        vouchers_list = [vouchers.VoucherModel(id=1, number="V1")]
        dto = vouchers.DeleteCrmVouchersParamsModel(vouchers=vouchers_list)
        assert len(dto.vouchers) == 1

class TestPostCrmVouchersParamsModel:
    def test_valid(self):
        balance = _common.BalanceModel(amount=100.0, currency="USD")
        vouchers_list = [
            vouchers.VoucherPostModel(
                number="V1",
                name="Test",
                expirationDate="2025-01-01",
                balance=balance,
                shops=[1],
                note="",
                typeId=1
            )
        ]
        dto = vouchers.PostCrmVouchersParamsModel(vouchers=vouchers_list)
        assert len(dto.vouchers) == 1

class TestPutCrmVouchersParamsModel:
    def test_valid(self):
        balance = _common.BalanceModel(amount=100.0, currency="USD")
        vouchers_list = [
            vouchers.VoucherPutModel(
                id=1,
                number="V1",
                name="Test",
                expirationDate="2025-01-01",
                balance=balance,
                shops=[1],
                note="",
                balanceOperationType=_common.BalanceOperationTypeEnum.SET,
                status=vouchers.StatusEnum.UNUSED
            )
        ]
        dto = vouchers.PutCrmVouchersParamsModel(vouchers=vouchers_list)
        assert len(dto.vouchers) == 1


# --- Tests for Endpoints
class TestPutBlock:
    def test_instantiate(self):
        params = vouchers.PutBlockCrmVouchersParamsModel(id=1, number="V1")
        endpoint = vouchers.PutBlock(params=params)
        assert endpoint.params.id == 1
        assert hasattr(endpoint, '_method')
        assert hasattr(endpoint, '_endpoint')

class TestGetTypes:
    def test_instantiate(self):
        endpoint = vouchers.GetTypes()
        assert hasattr(endpoint, '_method')
        assert hasattr(endpoint, '_endpoint')

class TestPutUnblock:
    def test_instantiate(self):
        params = vouchers.PutUnblockCrmVouchersParamsModel(vouchers=[vouchers.VoucherModel(id=1, number="V1")])
        endpoint = vouchers.PutUnblock(params=params)
        assert len(endpoint.params.vouchers) == 1

class TestDelete:
    def test_instantiate(self):
        params = vouchers.DeleteCrmVouchersParamsModel(vouchers=[vouchers.VoucherModel(id=1, number="V1")])
        endpoint = vouchers.Delete(params=params)
        assert len(endpoint.params.vouchers) == 1

class TestGet:
    def test_instantiate_without_params(self):
        endpoint = vouchers.Get()
        assert hasattr(endpoint, '_method')
        assert hasattr(endpoint, '_endpoint')

class TestPost:
    def test_instantiate(self):
        balance = _common.BalanceModel(amount=100.0, currency="USD")
        vouchers_list = [
            vouchers.VoucherPostModel(
                number="V1",
                name="Test",
                expirationDate="2025-01-01",
                balance=balance,
                shops=[1],
                note="",
                typeId=1
            )
        ]
        params = vouchers.PostCrmVouchersParamsModel(vouchers=vouchers_list)
        endpoint = vouchers.Post(params=params)
        assert len(endpoint.params.vouchers) == 1

class TestPut:
    def test_instantiate(self):
        balance = _common.BalanceModel(amount=100.0, currency="USD")
        vouchers_list = [
            vouchers.VoucherPutModel(
                id=1,
                number="V1",
                name="Test",
                expirationDate="2025-01-01",
                balance=balance,
                shops=[1],
                note="",
                balanceOperationType=_common.BalanceOperationTypeEnum.SET,
                status=vouchers.StatusEnum.UNUSED
            )
        ]
        params = vouchers.PutCrmVouchersParamsModel(vouchers=vouchers_list)
        endpoint = vouchers.Put(params=params)
        assert len(endpoint.params.vouchers) == 1
        assert len(endpoint.params.vouchers) == 1
