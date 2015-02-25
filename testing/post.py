import requests
import json

url = "https://api.bland.is/me/messageboard/"

params = {"api_key" : "97c92bb0-350f-41df-b37f-788ca6ebda93", "access_token" : "bAkAIoYqNrIWiDZzz%2fKGrn80GwBpVdnSGhUdVxc9%2byXCWboKlHZaEnwd5SD2JRM%2bNttdAQJ1tD7RGrJsyaR3fNDOjQL9h2SE", "parent_id" : "29311357", "message" : "this is a test from AURtip"}
r = requests.post(url, data=params)
print r.content

