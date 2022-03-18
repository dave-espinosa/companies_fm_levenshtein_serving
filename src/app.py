import os
import pandas as pd
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from typing import Optional
from typing import List
from src import classes, functions

# -----------------------------------------------------------------------------
# COMPANIES NAMES - REQUIREMENTS FOR SERVER
# -----------------------------------------------------------------------------

PATH_DATA = os.path.join(os.getcwd(), 'data', 'processed', 'company_names_cleaned_v1.0.csv')
company_df = pd.read_csv(PATH_DATA)
company_df.rename(columns={'title':'realName'}, inplace=True)

# -----------------------------------------------------------------------------
# COMPANIES NAMES - SERVER FUNCTIONS
# -----------------------------------------------------------------------------

app = FastAPI()
# Run with: 'uvicorn src.app:app --reload'

@app.get("/")
def health_checker():
    """Health Checker

    Returns:
        dict: Message to check the health of the api
    """
    return {"message": "Server ready to predict!"}



    # Args:
    #     topk (int): top k best results per company
    #
    # Returns:
    #     dict: a list of objets with the original name

@app.post("/matcher")
def fuzzy_companies(companies: List[classes.CompanyRequest], topk: Optional[int]):
    """
    Finds the parent company for a batch of companies name
    """
    response = []

    companies_ids = [company.id for company in companies]
    companies_names = [company.name for company in companies]
    
    results = functions.apply_fuzzy_matching_levenshtein(company_df, companies_names, topk)

    for j in range(len(results)):
        results[j]['id'] = companies_ids[j]
        response.append(results[j])

    return {"companies": response}


# -----------------------------------------------------------------------------
# ENDPOINT DOCUMENTATION
# -----------------------------------------------------------------------------

description = """
Company Name Standardizer for API for 1Mentor Inc. 🚀
## Overview
This API extracts professional skills, from a list of plain, contextual
text. The current version (0.0.1), is enabled to extract skills from
English language only. No 'skill categories' are available on this
version. Future releases will include other languages, as well as skill
categories.
## 1. How to interact with this API?
In your own application, you must aim to build a list of objects, each
of which will basically contain two fields: an "id", which is a unique,
string identifier, and a "text" which contains the paragraph where you
want to extract the skills from. A basic example of a query list,
containing 3 elements, looks like this:
```
curl -X 'POST' \
  'http://127.0.0.1:8000/eng/plain/?thr=0.80' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "id": "your_custom_id_tag_1",
    "text": "Python and Java are two very relevant programming languages"
  },
  {
    "id": "another_custom_tag_2",
    "text": "If you study Civil Engineering, it is very likely you will have to deal with Mathematics and Geometry almost daily"
  },
  {
    "id": "many_more_custom_tags",
    "text": "The work as Machine Learning Engineer is awesome, but sometimes a bit complex"
  }
]'
```
You can make your query list as long as you want, however **keep
in mind that longer query lists, will involve a larger processing
time**. For comparison, the average time taken to process a single
query text, containing ~1000 words, is around 50 ms.
### 1.1. "text" Examples
In the previous structure, the "text" key can get as simple as:
* _I love Python and Java_
up to longer, fully punctuated texts such as:
* _We believe that being a kind person who elevates the rest of
the team is just as valuable as writing great code. You have
strong problem-solving skills and experience working on
important functionality for a cloud-based product. You are
humble, eager to learn, and always willing to help others
learn as well. You want to work with people who enjoy picking
up a problem and solving it, regardless of the technologies
and techniques involved._
This app however, cannot 'pull miracles' for you. Even when you might
get some results, **avoid the following cases, as the app
will NOT work properly, and NO warning will be raised:**
* Gibberish / non-sense text ⛔: _Python cars Java Brooklyn notebook three jsdgfsjhd_
* Unclean text ⛔: _Pyth0n&^i'ns a nice3465programming language_
## 2. What will I get from this API as response?
Provided you did not get any error message, you should obtain another
list of objects, which contain two elements: an "id", which should be
equal to the corresponding input data; and "skills", which internally
contains a list of the extracted skills (in future releases, please
refer to the method'src documentation for the exact keys). Remember the
query list example of 3 elements, in **Section 1** above? Well, the
output of that query, looks like this:
```
{
  "response": [
    {
      "id": "your_custom_id_tag_1",
      "skills": [
        "Python",
        "Java"
      ]
    },
    {
      "id": "another_custom_tag_2",
      "skills": [
        "Civil Engineering",
        "Mathematics",
        "Geometry"
      ]
    },
    {
      "id": "many_more_custom_tags",
      "skills": [
        "Machine Learning Engineer"
      ]
    }
  ]
}
```
Notice how the "id" labels are the same than the request: this
will make the tracing easier for you, plus stresses the caution
you must take, to avoid duplicates to begin with. **This app
does not check "id" duplicates for you**, so be wary.
### 2.1. I am getting empty lists of skills in the response... Is the app working correctly?
Quick answer: there are good odds that yes, the app is working
correctly indeed. The odds of **Section 1.1** above, not being
read so far, are high also (pun intended). Remember: this app
aims to extract professional skills, which makes completely
possible that sometimes, nothing gets extracted, depending on
the input text. For instance, check the following request:
```
curl -X 'POST' \
  'http://127.0.0.1:8000/eng/plain/?thr=0.80' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "id": "id1",
    "text": "My name is David"
  },
  {
    "id": "id2",
    "text": "123 hufyt"
  }
]'
```
The query above will produce the following response:
```
{
  "response": [
    {
      "id": "id1",
      "skills": []
    },
    {
      "id": "id2",
      "skills": []
    }
  ]
}
```
As you can see, both of them produced empty results. Let'src check
one by one:
* "id1" had a simple statement, where clearly, there are no
professional skills.
* "id2" had a non-sense statement, where of course there are no
professional skills.
Therefore, **the code that interacts with this app (a.k.a. "your
code"), must include a way to handle these scenarios, where no
skill gets detected in the input data**.
## 3. Common causes of error "422 Unprocessable Entity"
### 3.1. Typos at the input
This error is originated when a wrong structure was used in the
request, and the response usually looks like this:
```
{
  "detail": [
    {
      "loc": [
        "body",
        119
      ],
      "msg": "Expecting value: line 6 column 1 (char 119)",
      "type": "value_error.jsondecode",
      "ctx": {
        "msg": "Expecting value",
        "doc": "[\n  {\n    \"id\": \"your_custom_id_tag_1\",\n    \"text\": \"Python and Java are two very relevant programming languages\"\n  },\n]",
        "pos": 119,
        "lineno": 6,
        "colno": 1
      }
    }
  ]
}
```
If you get this error, it means the your input data has some
typo or missing character. The easiest way to troubleshoot
this problem, is to check the **_"msg": "[some error]"_**
line, as it gives you a clue about what is going on. To better
summarize the most frequent causes, the following input data
will be used as template:
```
[
  {
    "id": "any_string_identifier_of_your_choice",
    "text": "Python and C++ are important programming languages"
  }
]
```
That template will be used as reference, to insert the 'Example
that triggers this error', referred in the following table:
| "msg" | Possible cause | Example that triggers this error |
|---|---|---|
| **Invalid control character at** | There is an extra comma near some curly bracket | }**,** |
| **Invalid control character at** | Some missing **closing** double quotes in the values | "any_string_identifier_of_your_choice**[Nothing]** |
| **Expecting value** | Some missing **opening** double quotes in the values | **[Nothing]**any_string_identifier_of_your_choice" |
| **field required** | Some wrong key has been used, or some whole field is missing | "df**one**" |
| **Expecting property name enclosed in double quotes** | Some of the keys does not have any double quotes, mispelled, or non-existent | **[Nothing]**id**[Nothing]**|
| **Expecting ',' delimiter** | A missing coma between "id" and "text", or missing curly bracket | [Self explanatory] |
### 3.2. Missing or wrong value for 'thr' parameter.
The mandatory parameter 'thr' mus have a floating value, between 0 and 1. If you do not include this value, or set a value outside of the established boundaries, you will get 'ERROR 422' too.
## Documentation
"""

tags_metadata = [
    {
        "name": "API Health Status",
        "description": "Quick test of API readiness to work.",
    },
    {
        "name": "Plain English Skills Extraction",
        "description": "Extracts plain skills, from a list of objects",
    },
]


def custom_openapi():

    # cache the generated schema
    if app.openapi_schema:
        return app.openapi_schema

    # Basic custom settings
    openapi_schema = get_openapi(
        title="SkillExtrApp",
        version="0.1.0",
        description=description,
        routes=app.routes,
    )

    # --------------- BRANCH 'info' ---------------------

    # # App sample logo
    # openapi_schema["info"]["x-logo"] = {
    #     "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    # }

    # Contact Information about this app
    openapi_schema["info"]["contact"] = {
        "name": "1Mentor Inc.",
        # "url": "http://x-force.example.com/contact/",
        # "email": "dp@x-force.example.com",
    }

    # # Terms of service
    # openapi_schema["info"]["terms_of_service"]="http://example.com/terms/"

    # License information
    openapi_schema["info"]["license_info"] = {
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },

    # --------------- BRANCH 'tags' ---------------------

    # Add tag metadata (i.e., brief description of each method)
    openapi_schema["tags"] = tags_metadata

    app.openapi_schema = openapi_schema

    return app.openapi_schema


# assign the customized OpenAPI schema
app.openapi = custom_openapi