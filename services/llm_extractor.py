from typing import Optional

from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI()

class FundingExtraction(BaseModel):
    is_funding_round: bool
    event_evidence: Optional[str] = None

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
                    "Determine whether the PRIMARY NEW EVENT reported by this article is a newly "
                    "announced venture-capital financing round for a company. "

                    "Set is_funding_round to true ONLY when the article itself is announcing or "
                    "reporting a new financing transaction as a principal event. "

                    "Do NOT set it to true merely because the article mentions historical funding, "
                    "previously announced rounds, existing investors, valuation changes, past "
                    "capital raised, or financing background. "

                    "If is_funding_round is true, provide event_evidence as a short paraphrase of "
                    "the article evidence showing that a new round is being announced. "

                    "If the article is not primarily reporting a new funding round, set "
                    "is_funding_round to false, set event_evidence to null, and do not extract "
                    "historical funding information as though it were the current event. "

                    "For investors, include only specifically named investment firms, funds, "
                    "corporations, or named individual investors that participated in the current "
                    "round. Do not include generic groups such as founders, advisers, employees, "
                    "or existing shareholders unless individually named. "

                    "Use only facts supported by the supplied article. Do not guess missing "
                    "information. Use null or an empty list when information is unavailable. "

                    "For amount, return the full numeric value, for example 6.3 million as 6300000."
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