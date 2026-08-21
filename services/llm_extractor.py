from typing import Optional

from openai import OpenAI
from pydantic import BaseModel, Field

from services.compound_evidence_service import (
    is_compound_funding_evidence,
)


client = OpenAI()


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
    """

    if is_compound_funding_evidence(
        article
    ):
        return FundingExtraction(
            is_funding_round=False
        )

    response = client.responses.parse(
        model="gpt-5.6-luna",
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
                    f"TITLE:\n{article.title}\n\n"
                    f"ARTICLE:\n{article.content}"
                ),
            },
        ],
        text_format=FundingExtraction,
    )

    return response.output_parsed


def extract_fund_close_with_llm(article):
    response = client.responses.parse(
        model="gpt-5.6-luna",
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