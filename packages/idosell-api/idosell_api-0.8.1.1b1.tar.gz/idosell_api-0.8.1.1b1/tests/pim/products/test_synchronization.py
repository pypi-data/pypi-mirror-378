import pytest
from pydantic import ValidationError

from src.idosell.pim.products.synchronization import (
    # DTOs
    PostFilePimProductsSynchronizationParamsModel,
    PutFinishUploadPimProductsSynchronizationParamsModel,
    # Endpoints
    PostFile,
    PutFinishUpload,
)


# --- Tests for DTOs
class TestPostFilePimProductsSynchronizationParamsModel:
    def test_valid(self):
        dto = PostFilePimProductsSynchronizationParamsModel(
            synchronizationId=1,
            packageId=1,
            fileType="full",
            md5Content="d41d8cd98f00b204e9800998ecf8427e",
            fileContent="base64encodeddata==",
            offerName="Test Offer"
        )
        assert dto.synchronizationId == 1
        assert dto.packageId == 1
        assert dto.fileType == "full"
        assert dto.offerName == "Test Offer"

    def test_first_package_id_none(self):
        dto = PostFilePimProductsSynchronizationParamsModel(
            synchronizationId=2,
            packageId=None,
            fileType="full",
            md5Content="d41d8cd98f00b204e9800998ecf8427e",
            fileContent="base64data==",
            offerName="First Package"
        )
        assert dto.packageId is None

    def test_light_file_type(self):
        dto = PostFilePimProductsSynchronizationParamsModel(
            synchronizationId=3,
            packageId=1,
            fileType="light",
            md5Content="d41d8cd98f00b204e9800998ecf8427e",
            fileContent="lightdata==",
            offerName="Light Offer"
        )
        assert dto.fileType == "light"

    def test_categories_file_type(self):
        dto = PostFilePimProductsSynchronizationParamsModel(
            synchronizationId=4,
            packageId=2,
            fileType="categories",
            md5Content="abcd1234567890abcdef123456789012",
            fileContent="categoriesdata==",
            offerName="Categories Offer"
        )
        assert dto.fileType == "categories"

    def test_sizes_file_type(self):
        dto = PostFilePimProductsSynchronizationParamsModel(
            synchronizationId=5,
            packageId=3,
            fileType="sizes",
            md5Content="bbbb2222567890abcdef1234567890aa",
            fileContent="sizesdata==",
            offerName="Sizes Offer"
        )
        assert dto.fileType == "sizes"

    def test_series_file_type(self):
        dto = PostFilePimProductsSynchronizationParamsModel(
            synchronizationId=6,
            packageId=4,
            fileType="series",
            md5Content="cccc3333567890abcdef1234567890bb",
            fileContent="seriesdata==",
            offerName="Series Offer"
        )
        assert dto.fileType == "series"

    def test_guarantees_file_type(self):
        dto = PostFilePimProductsSynchronizationParamsModel(
            synchronizationId=7,
            packageId=5,
            fileType="guarantees",
            md5Content="dddd4444567890abcdef1234567890cc",
            fileContent="guaranteesdata==",
            offerName="Guarantees Offer"
        )
        assert dto.fileType == "guarantees"

    def test_parameters_file_type(self):
        dto = PostFilePimProductsSynchronizationParamsModel(
            synchronizationId=8,
            packageId=6,
            fileType="parameters",
            md5Content="eeee5555567890abcdef1234567890dd",
            fileContent="parametersdata==",
            offerName="Parameters Offer"
        )
        assert dto.fileType == "parameters"

    def test_invalid_synchronization_id_zero(self):
        with pytest.raises(ValidationError):
            PostFilePimProductsSynchronizationParamsModel(
                synchronizationId=0,
                packageId=1,
                fileType="full",
                md5Content="d41d8cd98f00b204e9800998ecf8427e",
                fileContent="data==",
                offerName="Test"
            )

    def test_invalid_package_id_zero(self):
        with pytest.raises(ValidationError):
            PostFilePimProductsSynchronizationParamsModel(
                synchronizationId=1,
                packageId=0,
                fileType="full",
                md5Content="d41d8cd98f00b204e9800998ecf8427e",
                fileContent="data==",
                offerName="Test"
            )

    def test_invalid_file_type(self):
        with pytest.raises(ValidationError):
            PostFilePimProductsSynchronizationParamsModel(
                synchronizationId=1,
                packageId=1,
                fileType="invalid",
                md5Content="d41d8cd98f00b204e9800998ecf8427e",
                fileContent="data==",
                offerName="Test"
            )

    def test_invalid_md5_length_short(self):
        with pytest.raises(ValidationError):
            PostFilePimProductsSynchronizationParamsModel(
                synchronizationId=1,
                packageId=1,
                fileType="full",
                md5Content="short",
                fileContent="data==",
                offerName="Test"
            )

    def test_invalid_md5_length_long(self):
        with pytest.raises(ValidationError):
            PostFilePimProductsSynchronizationParamsModel(
                synchronizationId=1,
                packageId=1,
                fileType="full",
                md5Content="toolongmd5hashthatislongerthan32characters",
                fileContent="data==",
                offerName="Test"
            )

    def test_invalid_md5_non_hex(self):
        with pytest.raises(ValidationError):
            PostFilePimProductsSynchronizationParamsModel(
                synchronizationId=1,
                packageId=1,
                fileType="full",
                md5Content="gggggggggggggggggggggggggggggggg",
                fileContent="data==",
                offerName="Test"
            )

    def test_empty_file_content(self):
        with pytest.raises(ValidationError):
            PostFilePimProductsSynchronizationParamsModel(
                synchronizationId=1,
                packageId=1,
                fileType="full",
                md5Content="d41d8cd98f00b204e9800998ecf8427e",
                fileContent="",
                offerName="Test"
            )

    def test_empty_offer_name(self):
        with pytest.raises(ValidationError):
            PostFilePimProductsSynchronizationParamsModel(
                synchronizationId=1,
                packageId=1,
                fileType="full",
                md5Content="d41d8cd98f00b204e9800998ecf8427e",
                fileContent="data==",
                offerName=""
            )


class TestPutFinishUploadPimProductsSynchronizationParamsModel:
    def test_valid(self):
        dto = PutFinishUploadPimProductsSynchronizationParamsModel(
            synchronizationId=1,
            packageId=1,
            filesInPackage=5,
            verifyFiles=True
        )
        assert dto.synchronizationId == 1
        assert dto.packageId == 1
        assert dto.filesInPackage == 5
        assert dto.verifyFiles

    def test_verify_files_false(self):
        dto = PutFinishUploadPimProductsSynchronizationParamsModel(
            synchronizationId=2,
            packageId=2,
            filesInPackage=10,
            verifyFiles=False
        )
        assert not dto.verifyFiles

    def test_invalid_synchronization_id_zero(self):
        with pytest.raises(ValidationError):
            PutFinishUploadPimProductsSynchronizationParamsModel(
                synchronizationId=0,
                packageId=1,
                filesInPackage=5,
                verifyFiles=True
            )

    def test_invalid_package_id_zero(self):
        with pytest.raises(ValidationError):
            PutFinishUploadPimProductsSynchronizationParamsModel(
                synchronizationId=1,
                packageId=0,
                filesInPackage=5,
                verifyFiles=True
            )

    def test_invalid_files_in_package_zero(self):
        with pytest.raises(ValidationError):
            PutFinishUploadPimProductsSynchronizationParamsModel(
                synchronizationId=1,
                packageId=1,
                filesInPackage=0,
                verifyFiles=True
            )


# --- Tests for Endpoints
class TestPostFile:
    def test_instantiate_minimal(self):
        dto = PostFile(
            params=PostFilePimProductsSynchronizationParamsModel(
                synchronizationId=1,
                packageId=1,
                fileType="full",
                md5Content="d41d8cd98f00b204e9800998ecf8427e",
                fileContent="data==",
                offerName="Test Offer"
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'POST'
        assert dto._endpoint == '/api/admin/v6/products/synchronization/file'

    def test_instantiate_with_first_package(self):
        dto = PostFile(
            params=PostFilePimProductsSynchronizationParamsModel(
                synchronizationId=2,
                packageId=None,
                fileType="categories",
                md5Content="ffff6666567890abcdef1234567890ee",
                fileContent="catsdata==",
                offerName="Categories Upload"
            )
        )
        assert dto.params.packageId is None

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            PostFile()


class TestPutFinishUpload:
    def test_instantiate_minimal(self):
        dto = PutFinishUpload(
            params=PutFinishUploadPimProductsSynchronizationParamsModel(
                synchronizationId=1,
                packageId=1,
                filesInPackage=5,
                verifyFiles=True
            )
        )
        assert hasattr(dto, '_method')
        assert hasattr(dto, '_endpoint')
        assert dto._method == 'PUT'
        assert dto._endpoint == '/api/admin/v6/products/synchronization/finishUpload'

    def test_instantiate_verify_false(self):
        dto = PutFinishUpload(
            params=PutFinishUploadPimProductsSynchronizationParamsModel(
                synchronizationId=2,
                packageId=2,
                filesInPackage=10,
                verifyFiles=False
            )
        )
        assert not dto.params.verifyFiles

    def test_invalid_params_missing(self):
        with pytest.raises(ValidationError):
            PutFinishUpload()
