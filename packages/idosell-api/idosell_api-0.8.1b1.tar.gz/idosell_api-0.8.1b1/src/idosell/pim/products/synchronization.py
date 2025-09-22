from pydantic import BaseModel, Field, PrivateAttr, StrictInt

from src.idosell._common import Gateway


# --- DTOs
class PostFilePimProductsSynchronizationParamsModel(BaseModel):
    synchronizationId: StrictInt = Field(..., ge=1, description="Synchronization ID")
    packageId: StrictInt | None = Field(None, ge=1, description="File package number. Leave blank for the first file in the package, and the API will return a generated number, which should then be transmitted and by which the API will recognize subsequent files for this package")
    fileType: str = Field(..., pattern=r'^(full|light|categories|sizes|series|guarantees|parameters)$', description="File Type IOF30 (full/light/categories/sizes/series/guarantees/parameters)") # type: ignore
    md5Content: str = Field(..., pattern=r'^[A-Fa-f0-9]{32}$', description="MD5 from the file avarage before base64 encoding") # type: ignore
    fileContent: str = Field(..., min_length=1, description="Offer file encoded with base64 algorithm")
    offerName: str = Field(..., min_length=1, description="Unique offer name")

class PutFinishUploadPimProductsSynchronizationParamsModel(BaseModel):
    synchronizationId: StrictInt = Field(..., ge=1, description="Synchronization ID")
    packageId: StrictInt = Field(..., ge=1, description="File package number")
    filesInPackage: StrictInt = Field(..., ge=1, description="Total number of files in the parcel")
    verifyFiles: bool = Field(..., description="Whether to verify the package by sparsifying files and preparing requests. It may take a few minutes to answer")


# --- ENDPOINTS
class PostFile(Gateway):
    """
    The method allows you to upload to the goods synchronization module, the offer in a file in IOF 3.0 format.
    DOCS_URL: https://idosell.readme.io/reference/productssynchronizationfilepost
    """

    _method: str = PrivateAttr(default='POST')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/synchronization/file')

    params: PostFilePimProductsSynchronizationParamsModel = Field(..., description="Parameters transmitted to method")

class PutFinishUpload(Gateway):
    """
    Method informs commodity synchronization module that uploading of files is complete.
    DOCS_URL: https://idosell.readme.io/reference/productssynchronizationfinishuploadput
    """

    _method: str = PrivateAttr(default='PUT')
    _endpoint: str = PrivateAttr(default='/api/admin/v6/products/synchronization/finishUpload')

    params: PutFinishUploadPimProductsSynchronizationParamsModel = Field(..., description="Parameters transmitted to method")
