from typing import List, Any

from src.idosell._common import BooleanStrShortEnum
from src.idosell.cms.cpa.campaign import PostCampaignModel, PutCampaignModel
from src.idosell.cms.cpa.campaign import (
    Delete as DeleteCmsCpaCampaign,
    Get as GetCmsCpaCampaign,
    Post as PostCmsCpaCampaign, PostCmsCpaCampaignParamsModel,
    Put as PutCmsCpaCampaign, PutCmsCpaCampaignParamsModel
)
from src.idosell.cms.cpa.cpa import (
    Delete as DeleteCmsCpaCpa,
    Get as GetCmsCpaCpa,
    Post as PostCmsCpaCpa, PostCmsCpaCpaParamsModel, PostCpaModel,
    Put, PutCmsCpaCpaParamsModel, PutCpaModel
)
from src.idosell.cms.snippets.campaign import (
    Delete as DeleteCmsSnippetsCampaign,
    Get as GetCmsSnippetsCampaign,
    Post as PostCmsCpaSnippetsCampaign, PostCmsSnippetsCampaignParamsModel, PostSnippetsCampaignModel,
    Put as PutCmsSnippetsCampaign, PutCmsSnippetsCampaignParamsModel, PutSnippetsCampaignModel
)
from src.idosell.cms.snippets.cookies import (
    Delete as DeleteCmsSnippetsCookies,
    Get as GetCmsSnippetsCookies,
    Post as PostCmsCpaSnippetsCookies, PostCmsSnippetsCookiesParamsModel, PostCookiesModel,
    Put as PutCmsSnippetsCookies, PutCmsSnippetsCookiesParamsModel, PutCookiesModel
)
from src.idosell.cms.snippets.snippets import (
    Delete as DeleteCmsSnippetsSnippets,
    Get as GetCmsSnippetsSnippets,
    Post as PostCmsCpaSnippetsSnippets, PostSnippetsModel, PostCmsSnippetsSnippetsParamsModel,
    Put as PutCmsSnippetsSnippets, PutCmsSnippetsSnippetsParamsModel, PutSnippetsModel
)
from src.idosell.cms.config_variables import (
    Delete as DeleteCmsConfigVariables,
    Get as GetCmsConfigVariables,
    Put as PutCmsConfigVariables, PutCmsConfigVariablesModel, PutVariablesModel,
    TypeConfigVariablesEnum
)
from src.idosell.cms.entries import (
    Delete as DeleteCmsEntries, DeleteCmsEntriesParamsModel,
    Get as GetCmsEntries, GetPagesToDisplay as GetCmsEntriesGetPagesToDisplay, GetSources as GetCmsEntriesGetSources,
    Post as PostCmsCpaEntries, PostCmsEntriesParamsModel,
    Put as PutCmsEntries, PutCmsEntriesParamsModel
)

cms_delete: List[Any] = [ # type: ignore
    DeleteCmsCpaCampaign(id = [1]), # type: ignore
    DeleteCmsCpaCpa(id = [1]), # type: ignore
    DeleteCmsSnippetsCampaign(id = [1]), # type: ignore
    DeleteCmsSnippetsCookies(id = [1]), # type: ignore
    DeleteCmsSnippetsSnippets(id = [1]), # type: ignore
    DeleteCmsConfigVariables(
        type = TypeConfigVariablesEnum.SNIPPETS_CAMPAIGN,
        item = None,
        key = None

    ), # type: ignore
    DeleteCmsEntries(
        params = DeleteCmsEntriesParamsModel(entryId = 1)
    ),
]

cms_get: List[Any] = [ # type: ignore
    GetCmsCpaCampaign(), # type: ignore
    GetCmsCpaCpa(), # type: ignore
    GetCmsSnippetsCampaign(), # type: ignore
    GetCmsSnippetsCookies(), # type: ignore
    GetCmsSnippetsSnippets(), # type: ignore
    GetCmsConfigVariables(), # type: ignore
    GetCmsEntries(), # type: ignore
    GetCmsEntriesGetPagesToDisplay(), # type: ignore
    GetCmsEntriesGetSources(), # type: ignore
]

cms_post: List[Any] = [
    PostCmsCpaCampaign(
        params = PostCmsCpaCampaignParamsModel(campaigns = [PostCampaignModel(name = "Test Campaign")]) # type: ignore
    ),
    PostCmsCpaCpa(
        params = PostCmsCpaCpaParamsModel(cpa = [PostCpaModel(name = "Test CPA", campaign = 1)]) # type: ignore
    ),
    PostCmsCpaSnippetsCampaign(
        params = PostCmsSnippetsCampaignParamsModel(campaigns = [PostSnippetsCampaignModel(name = "Test snippet campaign name")]) # type: ignore
    ),
    PostCmsCpaSnippetsCookies(
        params = PostCmsSnippetsCookiesParamsModel(cookies = [PostCookiesModel(snippetId = 1, deliverer = 'Test deliverer')]) # type: ignore
    ),
    PostCmsCpaSnippetsSnippets(
        params = PostCmsSnippetsSnippetsParamsModel(snippets = [PostSnippetsModel(name = 'Test snippet name', campaign = 1)]) # type: ignore
    ),
    PostCmsCpaEntries(
        params = PostCmsEntriesParamsModel() # type: ignore
    )
]

cms_put: List[Any] = [
    PutCmsCpaCampaign(
        params = PutCmsCpaCampaignParamsModel(campaigns = [PutCampaignModel(id = 1)]) # type: ignore
    ),
    Put(
        params = PutCmsCpaCpaParamsModel(cpa = [PutCpaModel(id = 1)]) # type: ignore
    ),
    PutCmsSnippetsCampaign(
        params = PutCmsSnippetsCampaignParamsModel(campaigns = [PutSnippetsCampaignModel(id = 1)]) # type: ignore
    ),
    PutCmsSnippetsCookies(
        params = PutCmsSnippetsCookiesParamsModel(cookies = [PutCookiesModel(id = 1)]) # type: ignore
    ),
    PutCmsSnippetsSnippets(
        params = PutCmsSnippetsSnippetsParamsModel(snippets = [PutSnippetsModel(id = 1)]) # type: ignore
    ),
    PutCmsConfigVariables(
        params = PutCmsConfigVariablesModel(variables = [PutVariablesModel(key = "test_key", type = TypeConfigVariablesEnum.SNIPPETS_CAMPAIGN, itemId = 1)]) # type: ignore
    ),
    PutCmsEntries(
        params = PutCmsEntriesParamsModel(entryId = 1, deletePicture = BooleanStrShortEnum.NO) # type: ignore
    ),
]
