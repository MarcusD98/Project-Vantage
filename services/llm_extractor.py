from functools import lru_cache
from typing import Optional

from openai import OpenAI
from pydantic import BaseModel, Field

from services.compound_evidence_service import (
    is_compound_funding_evidence,
)


EXTRACTION_MODEL = "gpt-5.6-luna"

FUNDING_EXTRACTOR_VERSION = "funding-v1"
FUND_CLOSE_EXTRACTOR_VERSION = "fund-close-v1"


@lru_cache(maxsize=1)
def _get_openai_client():
    """
    Create the OpenAI client only when an extraction
    actually requires it.

    Importing Project Vantage must not require live
    OpenAI credentials.
    """
    return OpenAI()


def _parse_response(**kwargs):
    """
    Thin boundary around the OpenAI structured-response API.

    Keeping this boundary explicit makes extraction tests
    independent of live credentials and SDK internals.
    """
    return (
        _get_openai_client()
        .responses
        .parse(**kwargs)
    )


class FundingExtraction(BaseModel):
    is_funding_round: bool

    event_evidence: Optional[str] = None

    company_name: Optional[str] = None

    amount: Optional[float] = None
    currency: Optional[str] = None
    round_type: Optional[str] = None

    investors: list[str] = Field(
        default_factory=list
    )

    lead_investors: list[str] = Field(
        default_factory=list
    )

    company_city: Optional[str] = None
    company_country: Optional[str] = None
    founded_year: Optional[int] = None
    sector: Optional[str] = None


class FundCloseExtraction(BaseModel):
    is_fund_close: bool

    event_evidence: Optional[str] = None

    investor_name: Optional[str] = None
    fund_name: Optional[str] = None

    amount: Optional[float] = None
    currency: Optional[str] = None

    close_type: Optional[str] = None

    strategy: Optional[str] = None
    geography: Optional[str] = None
    vintage_year: Optional[int] = None


def extract_funding_with_llm(article):
    """
    Extract one focal company financing event from one evidence
    document.

    Obvious multi-company collections are rejected before an LLM
    call. Single-company articles may mention historical rounds;
    the model must isolate the focal/new event and never blend
    facts across different financings.

    First-party investor evidence is source-aware so references
    such as "we", "our", and "us" can be attributed to the
    publishing investment firm when the article clearly describes
    that firm's participation in the focal event.
    """

    if is_compound_funding_evidence(
        article
    ):
        return FundingExtraction(
            is_funding_round=False
        )

    source_name = (
        getattr(
            article,
            "source",
            None,
        )
        or "Unknown"
    )

    source_type = (
        getattr(
            article,
            "source_type",
            None,
        )
        or "unknown"
    )

    response = _parse_response(
        model=EXTRACTION_MODEL,
        input=[
            {
                "role": "developer",
                "content": (
                    "Extract structured information about ONE FOCAL "
                    "COMPANY FINANCING EVENT from the supplied article. "

                    "A company financing event means that a startup, "
                    "scale-up, or operating company has raised capital "
                    "from investors. "

                    "Do NOT classify an article as a company financing "
                    "event merely because a venture-capital firm has "
                    "raised money for one of its own investment funds. "

                    "IMPORTANT MULTI-ROUND RULE: venture articles often "
                    "mention older financing rounds as historical context. "
                    "If the article clearly centers on ONE newly announced, "
                    "current, or focal financing event, extract ONLY that "
                    "event and ignore facts belonging to older or separate "
                    "rounds. Never combine the amount from one round, the "
                    "stage from another round, or investor / lead roles from "
                    "different rounds. "

                    "Examples: if an article announces a new Series C but "
                    "mentions that the company previously raised a Series B, "
                    "extract the Series C only. If it announces a new round "
                    "and says an investor led the old seed round, do not mark "
                    "that investor as lead unless the article says it leads "
                    "the new focal round. "

                    "If the document genuinely describes multiple financing "
                    "events as co-primary facts and no single focal financing "
                    "event can be isolated with confidence, set "
                    "is_funding_round to false. "

                    "Set is_funding_round to true only when one specific "
                    "focal financing event can be represented consistently. "

                    "IMPORTANT SOURCE-PERSPECTIVE RULE: the supplied SOURCE "
                    "NAME identifies the publisher of this evidence. When "
                    "SOURCE TYPE is investor, first-person firm language such "
                    "as 'we', 'our', 'us', 'we backed', 'our investment', "
                    "'we partnered', 'we led', or 'we co-led' may refer to "
                    "SOURCE NAME. If the article clearly establishes that "
                    "the publishing investment firm participates in the "
                    "FOCAL event, include SOURCE NAME in investors. If it "
                    "clearly establishes that the publishing firm leads or "
                    "co-leads the FOCAL event, include SOURCE NAME in both "
                    "investors and lead_investors. "

                    "If the publishing firm led an EARLIER round but merely "
                    "joins, supports, doubles down, participates in, or "
                    "partners again in the focal later round, include the "
                    "source firm as an investor in the focal round only when "
                    "that participation is supported, and do NOT mark it as "
                    "a lead investor unless focal-round leadership is stated. "

                    "Do not treat article authors, byline names, employees, "
                    "partners of the publishing investment firm, or other "
                    "people mentioned because they work for the publisher as "
                    "investor entities unless the article explicitly says "
                    "that they invested personally in the focal round. Do not "
                    "replace an organizational investment by SOURCE NAME with "
                    "the name of an author or employee. "

                    "For event_evidence, provide one short factual sentence "
                    "about that focal event only. "

                    "Extract the canonical company name rather than "
                    "descriptive wording from the headline. "

                    "Investor lists must contain only identifiable investors "
                    "or investment organizations participating in the focal "
                    "event. Do not carry investor names forward from a prior "
                    "historical round. "

                    "Lead investors must be lead investors in the focal event "
                    "only. A firm that led an earlier seed round is not a lead "
                    "investor in a later Series A unless the article explicitly "
                    "says so. "

                    "Do not treat generic descriptions such as company "
                    "founders, advisers, strategic angels, employees, "
                    "government support, or scientific advisers as investor "
                    "entities unless a specific named investor or organization "
                    "is provided. "

                    "Use only facts supported by the article. Do not guess "
                    "missing information. Use null or an empty list when "
                    "information is unavailable. "

                    "For amount, return the full numeric value. For example, "
                    "6.3 million must be returned as 6300000. "

                    "For currency, return the standard three-letter currency "
                    "code where identifiable, such as USD, EUR, or GBP."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"SOURCE NAME:\n{source_name}\n\n"
                    f"SOURCE TYPE:\n{source_type}\n\n"
                    f"TITLE:\n{article.title}\n\n"
                    f"ARTICLE:\n{article.content}"
                ),
            },
        ],
        text_format=FundingExtraction,
    )

    return response.output_parsed


def extract_fund_close_with_llm(article):
    response = _parse_response(
        model=EXTRACTION_MODEL,
        input=[
            {
                "role": "developer",
                "content": (
                    "Extract structured information about a VC FUND "
                    "CLOSE from the supplied article. "

                    "A fund close is an event where a venture-capital, "
                    "growth-equity, private-equity, or similar investment "
                    "firm announces that an investment fund has reached "
                    "a first close, interim close, final close, or "
                    "otherwise reports capital committed to a specific "
                    "fund vehicle. "

                    "This is NOT the same as a startup or operating "
                    "company raising a funding round. "

                    "Set is_fund_close to true only when the article "
                    "reports capital being raised or closed for an "
                    "investment fund or investment vehicle. "

                    "For investor_name, extract the canonical name of "
                    "the investment firm or fund manager responsible "
                    "for the fund. "

                    "For fund_name, extract the specific fund or vehicle "
                    "name when stated. Examples could include Fund III, "
                    "Growth Fund II, Opportunity Fund, or another "
                    "explicitly named vehicle. "

                    "If the article reports a fund close but does not "
                    "provide a specific fund name, use null rather than "
                    "inventing one. "

                    "For close_type, use one of the following values "
                    "when supported by the article: "
                    "first_close, interim_close, final_close, or unknown. "

                    "Use final_close only when the article explicitly "
                    "states or clearly establishes that the fund has "
                    "reached its final close. "

                    "For event_evidence, provide one short factual "
                    "sentence explaining the fund-close event using "
                    "only information supported by the article. "

                    "For strategy, capture the stated investment "
                    "strategy or focus of the fund when available. "

                    "For geography, capture the stated geographic "
                    "investment focus when available. "

                    "For vintage_year, return the year associated with "
                    "the fund or its launch when clearly supported. "
                    "Do not infer it merely from the article publication "
                    "date unless the article explicitly establishes that "
                    "relationship. "

                    "Use only facts supported by the article. "
                    "Do not guess missing information. "
                    "Use null when information is unavailable. "

                    "For amount, return the full numeric value. "
                    "For example, 400 million must be returned as "
                    "400000000. "

                    "For currency, return the standard three-letter "
                    "currency code where identifiable, such as USD, "
                    "EUR, or GBP."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"TITLE:\n{article.title}\n\n"
                    f"ARTICLE:\n{article.content}"
                ),
            },
        ],
        text_format=FundCloseExtraction,
    )

    return response.output_parsed