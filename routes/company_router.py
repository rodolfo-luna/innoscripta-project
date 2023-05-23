from fastapi import Query
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status
from fastapi import Depends
from dependency import has_access
import openai
import re
from typing import Optional
import requests


router = APIRouter()

openai.api_key = "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"

prompt = ("Given the name of the company: [COMPANY NAME], country they are coming from: [COUNTRY], their Website URL: [WEBSITE], extract entities like the Products/services they offer, some Keywords about them,  year founded, current employee estimate, linkedin url, the company sic code and naics code from the description")

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
    products_match = re.search(r"Products/Services(?: offered)?: (.+)\n", generated_text, re.IGNORECASE)
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


def get_photos(query):
    '''Get image related to the products/services.
    '''
    access_key = 'UCZGHt7b9kTWxufUGIpLDENwD9su2Mwm9tlvYSoXqJc'
    url = 'https://api.unsplash.com/search/photos'

    params = {
        'query': query,
        'client_id': access_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()

        if len(data['results']) > 1:
            list_of_images_url = []
            list_of_images_url.append(data['results'][0]['urls']['regular'])  
            list_of_images_url.append(data['results'][1]['urls']['regular']) 
            return list_of_images_url
        else: 
            return data['urls']['regular']


def get_other(generated_text):
    '''Get other information from the generated text.'''
    patterns = [
        (r"Year founded: (\d{4})", "Year founded:"),
        (r"current employee estimate: (.+)\n", "current employee estimate:"),
        (r"linkedin url: (.+)\n", "linkedin url:")
    ]

    matches = [re.search(pattern, generated_text, re.IGNORECASE) for pattern, _ in patterns]
    results = [match.group(1) for match in matches if match]

    info = ". ".join([f"{prefix} {result}" for (_, prefix), result in zip(patterns, results)])

    return info


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

@router.get("/company")
async def company(company_name: str = Query(default=None), 
                  country: str = Query(default=None), 
                  website: Optional[str] = "",
                  authenticated: bool = Depends(has_access)):
    products = ""
    attempts = 1

    try:
        while products == "" and attempts <= 3:
            response = prompt_openai(prompt, company_name, country, website)
            generated_text = extract_generated_text(response)
            products = get_products_or_services(generated_text)
            productlist = [get_products_or_services(generated_text)]
            keywords = get_keywords(generated_text)
            images = get_photos(productlist[0])
            info = get_other(generated_text)
            naics = get_naics(generated_text)
            sic = get_sic(generated_text)
            attempts +=1
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Company not found')

    response_data = {}
    response_data["Company Name"] = company_name
    response_data["Country"] = country
    response_data["Website"] = website
    response_data["Products/Services"] = products
    response_data["keywords"] = keywords
    response_data["Products/Services Images"] = images
    response_data["Other Info"] = info
    response_data["NAICS"] = naics
    response_data["SIC"] = sic

    return response_data 