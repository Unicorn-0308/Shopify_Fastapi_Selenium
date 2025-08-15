import requests
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from extract import *
import os

cart = ""

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
    global cart

    if not cart:
        return {"status": "fail", "msg": "No cookie stored. Plz login first."}

    url = "https://www.uhs-hardware.com/cart/update.js"
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": f"cart={cart}; localization=US; cart_currency=USD;"
    }
    data = {"note": ""}

    try:
        response = requests.post(url, headers=headers, data=data)

        for cookie in response.cookies:
            if cookie.name == "cart":
                cart = cookie.value
        return {"status": "success", "cookie": cart}
    except Exception as e:
        return {"status": "fail", "msg": str(e)}

@app.post("/getCookie")
async def getCookie(account: Account):
    global cart

    shopify = ShopifyLogin(headless=True)

    STORE_URL = "https://www.uhs-hardware.com"  # Replace with actual store URL

    if shopify.login(STORE_URL, account.email, account.password):
        cookies = shopify.get_cookies()
        for cookie in cookies:
            if cookie["name"] == "cart":
                cart = cookie["value"]
        shopify.close()
        del shopify
        return {"status": "success", "cookie": cart}

    shopify.close()
    del shopify
    return {"status": "fail"}
    


