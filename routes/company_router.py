from fastapi import Query
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status
import openai
import re
from typing import Optional

router = APIRouter()

# Set up OpenAI API key
openai.api_key = "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"

prompt = ("Given the name of the company: [COMPANY NAME], country they are coming from: [COUNTRY], their Website URL: [WEBSITE], extract entities like the Products/services they offer, some Keywords about them, their Product/service images, the company sic code and naics code from the description")

def prompt_openai(prompt, company_name, country, website):
    '''Send the prompt to openai.
    '''
    response = openai.Completion.create(
                                    engine="text-davinci-002",
                                    prompt=prompt.replace("[COMPANY NAME]", company_name).replace("[COUNTRY]", country).replace("[WEBSITE]", website),
                                    max_tokens=1048,
                                    n=1,
                                    stop=None,
                                    temperature=0.5,
                                    )

    return response

def extract_generated_text(response):
    '''Extract generated text from response.
    '''
    generated_text = response.choices[0].text.strip()
    return generated_text


def get_products_or_services(generated_text):
    '''Extract products/services from the generated text.
    '''
    products_match = re.search(r"Products/Services: (.+)\n", generated_text, re.IGNORECASE)
    if products_match:
        products = products_match.group(1)
    else:
        products = ""
    return products

def get_keywords(generated_text):
    '''Get the keywords form the generated text.
    '''
    keywords_match = re.search(r"Keywords: (.+)\n", generated_text, re.IGNORECASE)
    if keywords_match:
        keywords = keywords_match.group(1)
    else:
        keywords = ""
    return keywords

def get_naics(generated_text):
    '''Get naics from the generated text.
    '''
    naics_matches = re.findall(r"NAICS? Code: (\d+)", generated_text, re.IGNORECASE)
    naics = ", ".join(naics_matches) if naics_matches else ""
    return naics

def get_sic(generated_text):
    '''Get the sic from generated text.
    '''
    sic_matches = re.findall(r"SIC? Code: (\d+)", generated_text, re.IGNORECASE)
    sic = ", ".join(sic_matches) if sic_matches else ""
    return sic

def query_database(company_name, country, website):
    '''Query for the company in the database.
    '''
    products = "INFO"
    return products

@router.get("/company")
async def company(company_name: str = Query(default=None), 
                  country: str = Query(default=None), 
                  website: Optional[str] = ""):
    products = ""
    attempts = 1

    try:
        while products == "" and attempts <= 3:
            response = prompt_openai(prompt, company_name, country, website)
            generated_text = extract_generated_text(response)
            products = get_products_or_services(generated_text)
            keywords = get_keywords(generated_text)
            naics = get_naics(generated_text)
            sic = get_sic(generated_text)
            attempts +=1
            if attempts == 4 and products == "":
                products = query_database(company_name, country, website)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Company not found')


    # Render HTML response with company information
    response_data = {}
    response_data["Company Name"] = company_name
    response_data["Country"] = country
    response_data["Website"] = website
    response_data["Products/Services"] = products
    response_data["keywords"] = keywords
    response_data["NAICS"] = naics
    response_data["SIC"] = sic

    return response_data
    
