import requests
from fastapi import FastAPI, BackgroundTasks, HTTPException, Response
from pydantic import BaseModel
from extract import *
import os
import json

cart = ""
cookies = {}

#
app = FastAPI()

class Account(BaseModel):
    email: str
    password: str

@app.get("/")
async def root():
    return {"message": "Hello World. Welcome to FastAPI!"}

@app.get("/updateCookie")
async def updateCookie():
    global cart, cookies

    cookie_str = ""
    for cookie in cookies:
        cookie_str += f"{cookie['name']}={cookie['value']}; "

    if not cart:
        return {"status": "fail", "msg": "No cookie stored. Plz login first."}

    url = "https://www.uhs-hardware.com/cart/update.js"
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": cookie_str
    }
    data = {"note": ""}

    try:
        response = requests.post(url, headers=headers, data=data)

        cookies = response.cookies

        for cookie in response.cookies:
            cookies[cookie.name] = cookie.value

        return Response(content=json.dumps({"status": "success", "cookie": cart, "cookies": cookies}), media_type="application/json")
    
    except Exception as e:
        return Response(content=json.dumps({"status": "fail", "msg": str(e)}), media_type="application/json")

@app.post("/getCookie")
async def getCookie(account: Account):
    global cart, cookies

    shopify = ShopifyLogin(headless=False)

    STORE_URL = "https://www.uhs-hardware.com"  # Replace with actual store URL

    if shopify.login(STORE_URL, account.email, account.password):
        cookies = shopify.get_cookies()
        for cookie in cookies:
            if cookie["name"] == "cart":
                cart = cookie["value"]
        shopify.close()
        del shopify
        return Response(content=json.dumps({"status": "success", "cookie": cart, "cookies": cookies}), media_type="application/json")

    shopify.close()
    del shopify
    return Response(content=json.dumps({"status": "fail"}), media_type="application/json")
    


