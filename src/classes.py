from pydantic import BaseModel


class CompanyRequest(BaseModel):
    id: str
    name: str

    # The following code helps to "build" a quick example
    # for the docs / redoc documentation, IT DOES NOT DO
    # ANYTHING (!)
    class Config:
        schema_extra = {
            "example": {
                "id": "any_string_identifier_of_your_choice",
                "name": "IBM Latin America"
            }
        }
