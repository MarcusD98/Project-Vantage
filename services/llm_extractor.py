from typing import Optional

from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI()

class FundingExtraction(BaseModel):
    is_funding_round: bool

    company_name: Optional[str] = None

    amount: Optional[float] = None
    currency: Optional[str] = None
    round_type: Optional[str] = None

    investors: list[str] = Field(default_factory=list)
    lead_investors: list[str] = Field(default_factory=list)

    company_city: Optional[str] = None
    company_country: Optional[str] = None
    founded_year: Optional[int] = None
    sector: Optional[str] = None

def extract_funding_with_llm(article):
    response = client.responses.parse(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "developer",
                "content": (
                    "Determine whether the article's primary reported event is a new venture "
                    "funding round. Do not treat historical funding rounds, previously announced "
                    "investments, valuation references, or background financing information as "
                    "the current event. "
                    "If the article is not primarily reporting a new funding round, set "
                    "is_funding_round to false and do not infer funding details from historical "
                    "background information. "
                    "Use only facts supported by the supplied article. "
                    "Do not guess missing information. "
                    "Use null or an empty list when information is unavailable. "
                    "For amount, return the full numeric value, for example "
                    "6.3 million as 6300000."
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