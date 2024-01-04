from fastapi import FastAPI
import json
import requests
import os

app = FastAPI()

my_secret = os.environ['refresh_token']
acces_token = ""


def schedule_call(id_value, name_value, descrip):
  url = "https://anagram-call-schedule.onrender.com/items/"

  payload = json.dumps({
      "id": id_value,
      "name": name_value,
      "desc": descrip,
      "source": "'WhatsApp - triumph'"
  })
  headers = {'Content-Type': 'application/json'}

  response = requests.request("POST", url, headers=headers, data=payload)
  return


def convert_lead(id):
  url = "https://www.zohoapis.in/crm/v5/Leads/" + id + "/actions/convert"
  payload = json.dumps({
      "data": [{
          "overwrite": True,
          "notify_lead_owner": False,
          "notify_new_entity_owner": False
      }]
  })
  headers = {
      'Content-Type':
      'application/json',
      'Authorization':
      'Bearer ' + acces_token,
      'Cookie':
      '34561a6e49=05e68ae6a7c2f7d782946ef8f4a221ad; _zcsr_tmp=90ec0566-e656-408a-9766-8b920f8f9f89; crmcsr=90ec0566-e656-408a-9766-8b920f8f9f89'
  }
  response = requests.request("POST", url, headers=headers, data=payload)
  data2 = json.loads(response.text)
  print(data2)
  id_value = data2['data'][0]['details']['Contacts']['id']
  name_value = data2['data'][0]['details']['Contacts']['name']
  value = [id_value, name_value]
  return value


def update_lead(element, query):
  id_value = element['id']
  description_value = element['Description']
  description_value = description_value if isinstance(description_value,
                                                      str) else ""
  element['Description'] = description_value + "\n " + query
  url = "https://www.zohoapis.in/crm/v5/Leads/" + id_value
  data = {"data": []}
  data["data"].append(element)
  payload = json.dumps(data)
  headers = {
      'Authorization':
      'Bearer ' + acces_token,
      'Content-Type':
      'application/json',
      'Cookie':
      '34561a6e49=e281fadb2969b66b5522dd2b50f2cf9f; JSESSIONID=8C6B00D8FB9A1359D122AADD973AD0F0; _zcsr_tmp=f5a2cd02-cd3c-42da-87be-54a0699b9229; crmcsr=f5a2cd02-cd3c-42da-87be-54a0699b9229'
  }

  response = requests.request("PUT", url, headers=headers, data=payload)

  print(response.text)
  return element['Description']


def get_acces_token():
  url = "https://accounts.zoho.in/oauth/v2/token?refresh_token=" + my_secret
  response = requests.request("POST", url)

  response = json.loads(response.text)
  global acces_token
  acces_token = (response["access_token"])
  return acces_token


def get_lead_id(no):
  url = "https://www.zohoapis.in/crm/v5/Leads/search?criteria=((Mobile:equals:" + no + ")and(Lead_Source:starts_with:WhatsApp - triumph))"

  headers = {'Authorization': 'Zoho-oauthtoken ' + acces_token}

  response = requests.request("GET", url, headers=headers)

  data = json.loads(response.text)

  # Extract id and description of the first element in the data array
  element = data['data'][0]
  # id_value = first_element['id']
  # description_value = first_element['Description']
  # value={"id":id_value,"description":description_value}
  return element


def create_lead(lastname, firstname, number):
  url = "https://www.zohoapis.in/crm/v5/Leads"

  payload = json.dumps({
      "data": [{
          "Lead_Source": "WhatsApp - triumph",
          "Last_Name": lastname if (len(lastname) > 0) else ". ",
          "First_Name": firstname,
          "Mobile": number,
          "Description": ""
      }],
      "trigger": ["approval", "workflow", "blueprint"]
  })
  headers = {
      'Authorization':
      'Zoho-oauthtoken ' + acces_token,
      'Content-Type':
      'application/json',
      'Cookie':
      '34561a6e49=e281fadb2969b66b5522dd2b50f2cf9f; 941ef25d4b=00ba5752c799bdaa8d1313ffff13d1f0; _zcsr_tmp=80d1c723-bb90-471b-89ce-79b04787fdd9; crmcsr=80d1c723-bb90-471b-89ce-79b04787fdd9'
  }

  response = requests.request("POST", url, headers=headers, data=payload)
  print(response.text)
  return


# Default root endpoint
@app.get("/")
async def root():
  return {"message": "Hello world"}


# Example path parameter
@app.post("/items/")
async def create_item(item: dict):
  number = item["originalDetectIntentRequest"]["payload"][
      "AiSensyMobileNumber"]
  get_acces_token()
  fulfillment_text = item['queryResult']['fulfillmentText']
  if (fulfillment_text ==
      "Thank you for your interest in Triumph - the perfect ride.\n\nWhich model are you interested in?"
      ):
    print("hi")
    name = item["originalDetectIntentRequest"]["payload"]["AiSensyName"]
    name = name.split(" ")
    firstname = name[0]
    lastname = ""
    if (len(name) == 2):
      lastname = name[1]
    create_lead(lastname, firstname, number)
    return item
  query_text = item["queryResult"]["queryText"]
  element = get_lead_id(number)
  id_value = element['id']
  desc = update_lead(element, query_text)
  if (fulfillment_text.startswith("Superb!")):

    value = convert_lead(id_value)
    schedule_call(value[0], value[1], desc)
    return item
  return item
