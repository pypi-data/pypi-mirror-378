# Idosell Python API - Usage examples

This guide shows **real-world usage examples** for the Idosell Python API across all modules: PIM, CRM, OMS, CMS, System and WMS.

> **Note**: See [README.md](README.md) for basic setup. This file focuses on practical examples.

## Client Setup

```python
from idosell.api_request import ApiRequest

api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/",
    api_key="YOUR_API_KEY"
)
```

## Product Information Management (PIM)

### 1. Product Categories Management

```python
from idosell.pim.products._common import CategoriesModel, OperationEnum
from idosell.pim.products.categories import Get, Put, PutPimProductsCategoriesParamsModel, SearchIdosell, SearchIdosellPimProductsCategoriesParamsModel
from idosell.api_request import ApiRequest

api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/",
    api_key="YOUR_API_KEY"
)

# Get categories
categories_data = Get(
    languages=["pol"],
    resultsPage=1,
    resultsLimit=20
)
res = api.request(categories_data)

# Add new category
new_category_params = PutPimProductsCategoriesParamsModel(
    categories = [CategoriesModel(
        id=101,
        parent_id=1,
        priority=10,
        operation=OperationEnum.ADD,
    )])

new_category = Put(params=new_category_params)
res = api.request(new_category)

# Search IdoSell categories
search_dto = SearchIdosell(
    params = SearchIdosellPimProductsCategoriesParamsModel(
        # ...
    )
)
res = api.request(search_dto)
```

### 2. Product Operations

```python
from idosell.pim.products.product._common import SettingModificationTypeEnum, SettingCalculateBasePriceSizesEnum, SettingsPutModel, ProductDateSearchModel, ProductDateModeSearchEnum
from idosell.pim.products.product.product import PutPimProductsProductProductParamsModel, Search, Put, SearchPimProductsProductProductParamsModel
from idosell.api_request import ApiRequest

api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/",
    api_key="YOUR_API_KEY"
)

# Get products with complex filters
products_dto = Search(
    params = SearchPimProductsProductProductParamsModel(
        productDate = [ProductDateSearchModel(
            productDateMode = ProductDateModeSearchEnum.ADDED,
            productDateBegin = "2024-01-01",
            productDateEnd = "2024-12-31"
        )],
        returnElements = "lang_data"
    ),
    resultsPage = 1,
    resultsLimit = 50,
)
res = api.request(products_dto)

# Bulk product update
bulk_update = Put(
    params=PutPimProductsProductProductParamsModel(
        settings = SettingsPutModel(
            settingModificationType = SettingModificationTypeEnum.ALL,
            settingCalculateBasePriceSizes = SettingCalculateBasePriceSizesEnum.ALL
        ),
        picturesSettings = None,
        products = []  # Note: requires at least one product model, but left empty for now
    )
)
res = api.request(bulk_update)
```

### 3. Brands Management

```python
from idosell.pim.products.brands import Post, PostPimProductsBrandsParamsModel
from idosell.pim.products._common import ProducerPostModel, ImagesSettingsModel, SourceTypeEnum
from idosell.api_request import ApiRequest

api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/",
    api_key="YOUR_API_KEY"
)

brand_params = PostPimProductsBrandsParamsModel(
    producers=[
        ProducerPostModel(
            nameInPanel="Example Brand",
            imagesSettings=ImagesSettingsModel(sourceType=SourceTypeEnum.BASE64),
            languagesConfigurations=[]
        )
    ]
)

brand_dto = Post(params=brand_params)
res = api.request(brand_dto)
```

### 4. Collections Management

```python
from idosell.pim.products._common import ProductsCollectionsPostModel, ProductSizesPostModel
from idosell.pim.products.collections import Post, PostPimProductsCollectionsParamsModel
from idosell.api_request import ApiRequest

api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/",
    api_key="YOUR_API_KEY"
)

# Add a new collections
collections_dto = Post(
    params = PostPimProductsCollectionsParamsModel(
        products=[
            ProductsCollectionsPostModel(
                productId=1,
                productSizes=[
                    ProductSizesPostModel(size="M")
                ],
                quantity=1
            )
        ]
    )
)
res = api.request(collections_dto)
print(res)
```

## Customer Relationship Management (CRM)

### 1. Client Management

```python
from idosell.crm.clients import (
    Get, Post, PostCrmClientsClientsModel, PostCrmClientsParamsModel, Put, PutCrmClientsClientsModel,
    PutCrmClientsParamsModel, SettingsPostModel, SettingsPostPutModel
)
from idosell.api_request import ApiRequest

api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/",
    api_key="YOUR_API_KEY"
)

# Get clients with filters
clients_dto = Get(
    resultsPage=1,
    resultsLimit=50
)
res = api.request(clients_dto)

# Create new client
new_client = Post(
    params = PostCrmClientsParamsModel(
        clients = [PostCrmClientsClientsModel(
            login="testuser",
            code_extern="12345",
            # ...
        )],
    ),
    settings = SettingsPostModel(
        send_mail = False,
        send_sms = False
    )
)
res = api.request(new_client)

# Update client information
update_client = Put(
    params = PutCrmClientsParamsModel(
        clients = [PutCrmClientsClientsModel(
            clientLogin="updateduser",
            clientEmail="updated@example.com",
            # ...
        )]
    ),
    clientsSettings = SettingsPostPutModel(
        clientSettingSendMail = False,
        clientSettingSendSms = False
    )
)
res = api.request(update_client)

```

### 2. Client Balance Operations

```python
from idosell.crm.clients import PostBalance, PostBalanceCrmClientsParamsModel, SettingsPostPutModel, OperationClientsEnum
from idosell.api_request import ApiRequest

api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/",
    api_key="YOUR_API_KEY"
)

# Add credit to client balance
add_balance = PostBalance(
    params = PostBalanceCrmClientsParamsModel(
        clientId=1,
        operation=OperationClientsEnum.ADD,
        balance=100.0,
        currency="PLN",
        note="Adding credit to client balance",
        prepaidId=1
    ),
    settings = SettingsPostPutModel(
        clientSettingSendMail = False,
        clientSettingSendSms = False
    )
)
res = api.request(add_balance)
```

### 3. Pricelists Management

```python
from idosell._common import BooleanStrLongEnum
from idosell.crm.pricelists import Post, PostCrmPricelistsParamsModel, PutClients, PutClientsCrmPricelistsParamsModel
from idosell.api_request import ApiRequest

api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/",
    api_key="YOUR_API_KEY"
)

# Create new pricelist
pricelist_create = Post(
    params = PostCrmPricelistsParamsModel(
        priceListName="Test Pricelist",
        onlyOrderProductsWithManuallySetPrices=BooleanStrLongEnum.NO,
        onlySeeProductsWithManuallySetPrices=BooleanStrLongEnum.NO
    )
)
res = api.request(pricelist_create)

# Assign clients to pricelist
assign_clients = PutClients(
    params = PutClientsCrmPricelistsParamsModel(
        priceListId=1,
        clientsIds=[123]
    )
)
res_assign = api.request(assign_clients)
```

### 4. Giftcards Management

```python
from idosell.crm.giftcards import Post, PostCrmGiftcardsParamsModel, Put, PutCrmGiftcardsParamsModel
from idosell.api_request import ApiRequest

api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/",
    api_key="YOUR_API_KEY"
)

# Create giftcard
giftcard_create = Post(
    params=PostCrmGiftcardsParamsModel(
        giftCards=[
            GiftCardPostModel(
                number="000000001",
                pin="1234",
                name="Test Gift Card",
                expirationDate="2025-12-31",
                balanceOperationType=BalanceOperationTypeEnum.ADD,
                balance=BalanceModel(amount=100.0, currency="PLN"),
                shops=[1],
                note="Test note",
                typeId=1
            )
        ]
    )
)
res = api.request(giftcard_create)

# Update giftcard balance
giftcard_update = Put(
    params=PutCrmGiftcardsParamsModel(
        giftCards=[
            GiftCardPutModel(
                id=1,
                number="000000001",
                pin="1234",
                name="Updated Gift Card",
                expirationDate="2025-12-31",
                balanceOperationType=BalanceOperationTypeEnum.SET,
                balance=BalanceModel(amount=50.0, currency="PLN"),
                shops=[1],
                note="Updated note"
            )
        ]
    )
)
res = api.request(giftcard_update)
```

### 5. Newsletter Subscriptions

```python
from idosell.crm.newsletter import SearchEmail, Get
from idosell.crm._common import BooleanStrShortEnum
from idosell.api_request import ApiRequest

api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/",
    api_key="YOUR_API_KEY"
)

# Search newsletter subscribers by email
newsletter_dto = SearchEmail(
    results_page=0,
    results_limit=10,
    params=SearchEmailCrmNewsletterParamsModel(
        # ...
    )
)
res = api.request(newsletter_dto)  # type: ignore
```

## 📦 Order Management System (OMS)

### 1. Order Processing

```python
from idosell.oms.orders import Get, Search, SearchOmsOrdersParamsModel
from idosell.api_request import ApiRequest

api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/",
    api_key="YOUR_API_KEY"
)

# Get orders with filters
orders_dto = Get(
    ordersIds = ['1']
)
res = api.request(orders_dto)

# Search orders by serial numbers
order_search = Search(
    params = SearchOmsOrdersParamsModel()
)
res = api.request(order_search)
```

### 2. Package Management

```python
from idosell.oms.packages import (
    Post, PostOmsPackagesParamsModel, Search, SearchOmsPackagesParamsModel,
    OrderPackagesPackagesPostModel, EventOrderTypeEnum
)
from idosell.api_request import ApiRequest

api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/",
    api_key="YOUR_API_KEY"
)

# Create shipment package
package_dto = Post(
    params = PostOmsPackagesParamsModel(
        orderPackages=[
            OrderPackagesPackagesPostModel(
                eventId=1,
                eventType=EventOrderTypeEnum.ORDER,
                parcelParameters=[],
                parcelParametersByPackages=[]
            )
        ]
    )
)
res = api.request(package_dto)

# Get packages with status
packages_dto = Search(
    params = SearchOmsPackagesParamsModel(
        deliveryPackageNumbers=None,
        events=None,
        returnLabels=None
    )
)
res = api.request(packages_dto)
```

### 3. Returns & Refunds

```python
from idosell.oms.returns import Get, Post, PostOmsReturnsParamsModel, ProductsReturnsPostModel
from idosell.oms.refunds import PutCancelRefund, PutCancelRefundOmsRefundsParamsModel, SourceTypeWithOrderEnum
from idosell.api_request import ApiRequest

api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/",
    api_key="YOUR_API_KEY"
)

# Create return request
params = PostOmsReturnsParamsModel(
    order_sn=12345,
    stock_id=1,
    products=[
        ProductsReturnsPostModel(
            id=67890,
            size="M",
            quantity=1.0,
            price=10.99,
            serialNumbers=[],
            productOrderAdditional="Example additional info"
        )
    ],
    status=1,
    client_received=False,
    change_status=False,
    courier_id=1,
    return_operator="Example operator",
    tryCorrectInvoice=False,
    include_shipping_cost="no",
    additional_payment_cost="0.00",
    emptyReturn="false"
)
return_request = Post(params=params)
res = api.request(return_request)

# Get returns list
returns_dto = Get(
    order_sn = 1
)
res = api.request(returns_dto)

# Process refund
refund_params = PutCancelRefundOmsRefundsParamsModel(
    sourceType=SourceTypeWithOrderEnum.RETURN,
    sourceId=12345,
    paymentId="1"
)
refund_dto = PutCancelRefund(params=refund_params)
res = api.request(refund_dto)
```

## 📝 Content Management System (CMS)

### 1. Content Entries

```python
from idosell._common import BooleanStrShortEnum
from idosell.cms.entries import Get, Post, Put, PostCmsEntriesParamsModel, PutCmsEntriesParamsModel
from idosell.api_request import ApiRequest

api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/",
    api_key="YOUR_API_KEY"
)

# Get CMS entries
entries_dto = Get(
    entryId=1,
    # ...
)
res = api.request(entries_dto)

# Create new blog entry
blog_post = Post(
    params=PostCmsEntriesParamsModel(
        shopId=1,
        # ....
    )
)
res = api.request(blog_post)

# Update content
update_entry = Put(
    params=PutCmsEntriesParamsModel(
        entryId=1,
        deletePicture=BooleanStrShortEnum.NO,
        # ...
    )
)
res = api.request(update_entry)
```

### 2. Snippets & Config

```python
from idosell.cms.snippets.snippets import Get, Post, PostCmsSnippetsSnippetsParamsModel, PostSnippetsModel
from idosell.cms.config_variables import Get as GetConfig, Put as PutConfig, PutCmsConfigVariablesModel, PutVariablesModel, TypeConfigVariablesEnum
from idosell.api_request import ApiRequest

api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/",
    api_key="YOUR_API_KEY"
)

# Get active snippets
snippets_dto = Get(
    # ...
)
res = api.request(snippets_dto)

# Create custom footer snippet
footer_snippet = Post(
    params=PostCmsSnippetsSnippetsParamsModel(
        snippets=[
            PostSnippetsModel(
                name="Custom Footer Snippet",
                campaign=1
            )
        ]
    )
)
res = api.request(footer_snippet)

# Get configuration variables
config_dto = GetConfig(
    type = TypeConfigVariablesEnum.SNIPPETS_CAMPAIGN,
)
res = api.request(config_dto)

# Update configuration
update_config = PutConfig(
    params=PutCmsConfigVariablesModel(
        variables=[
            PutVariablesModel(
                key="example_key",
                value=None,
                type="snippets_campaign",
                itemId=1
            )
        ]
    )
)
res = api.request(update_config)
```

## 🛠️ System Management

### 1. Shops Configuration

```python
from idosell.system.shops import GetCurrencies
from idosell.api_request import ApiRequest

api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/",
    api_key="YOUR_API_KEY"
)

# Get shops currencies
shops_dto = GetCurrencies()
res = api.request(shops_dto)
```

### 2. Couriers Management

```python
from idosell.system.couriers import Get
from idosell.api_request import ApiRequest

api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/",
    api_key="YOUR_API_KEY"
)

# Get available couriers
couriers_dto = Get(
    countryCode = 'PL'
)
res = api.request(couriers_dto)
```

### 3. Delivery Methods

```python
from idosell.system.deliveries import GetProfiles
from idosell.api_request import ApiRequest

api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/",
    api_key="YOUR_API_KEY"
)

# Get profiles
dto = GetProfiles()
res = api.request(dto)

```

## 📊 Warehouse Management System (WMS)

### 1. Stock Management

```python
from idosell.wms.stocks import GetProducts, PutProducts
from idosell.api_request import ApiRequest

api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/",
    api_key="YOUR_API_KEY"
)

# Get stock levels
stocks_dto = GetProducts(
    # ...
)
res = api.request(stocks_dto)

# Update stock quantities
stock_update = PutProducts(
    params=PutProductsWmsStocksParamsModel(
        products=[
            ProductsPostPutModel(
                product=1,  # Example product ID
                size="M",  # Example size
                quantity=10,  # Example quantity to update
                productPurchasePrice=15.50,  # Example purchase price
                locationId=1,  # Example location ID
                locationCode="LOC001",  # Example location code
                locationTextId="Warehouse1\\SectionA\\Shelf01"  # Example location text ID
            )
        ],
        type=DocumentTypeEnum.PW,
        id=1
    )
)
res = api.request(stock_update)
```

### 2. Warehouse Locations

```python
from idosell.wms.locations import GetLocations
from idosell.api_request import ApiRequest

api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/",
    api_key="YOUR_API_KEY"
)

# Get warehouse locations
locations_dto = GetLocations(
    # ...
)
res = api.request(locations_dto)
```

### 3. Supplier Stock Tracking

```python
from idosell.wms._common import SuppliersModel, AverageDeliveryTimeModel, OrderCompletionTimeModel, WorkDaysModel
from idosell.wms.suppliers import Get, Put, PutWmsSuppliersParamsModel
from idosell.api_request import ApiRequest

api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/",
    api_key="YOUR_API_KEY"
)

# Get supplier information
suppliers_dto = Get(
    # ...
)
res = api.request(suppliers_dto)

# Update supplier product codes
supplier_update = Put(
    params = PutWmsSuppliersParamsModel(
        suppliers = [SuppliersModel(
            id=1,
            name="Supplier Name",
            email="email@example.com",
            phone="123456789",
            fax="987654321",
            street="Street Address",
            zipCode="12345",
            city="City Name",
            country=1,
            taxCode="123456789",
            averageDeliveryTime=AverageDeliveryTimeModel(value=1, unit="days"),
            description="Supplier description",
            orderCompletionTime=OrderCompletionTimeModel(value=1, unit="days"),
            workDays=[WorkDaysModel.model_validate({"day": 1, "type": "weekday", "from": "08:00", "to": "17:00"})]
        )]
    )
)
res = api.request(supplier_update)
```
