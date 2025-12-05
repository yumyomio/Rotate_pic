from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from PIL import Image
from io import BytesIO

import os
import httpx

from starlette.staticfiles import StaticFiles

import numpy as np
import matplotlib.pyplot as plt

app = FastAPI()
RECAPTCHA_SECRET="6Lc4WiIsAAAAAHAnI7NyxpUVyHyP0QN9XKXC3udl"
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/process", response_class=HTMLResponse)
async def process(request: Request, file: UploadFile = File(...), angle: int = Form(...)):
    form=await request.form()
    recaptcha_response = form.get("g-recaptcha-response")

    data={
        "secret": RECAPTCHA_SECRET,
        "response": recaptcha_response,
    }
    async with httpx.AsyncClient() as client:
        result = await client.post("https://www.google.com/recaptcha/api/siteverify",data=data)
        verification=result.json()
    if not verification.get("success"):
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Подтвердите что вы не робот"
        })
    content = await file.read()
    img = Image.open(BytesIO(content))

    rotated_img = img.rotate(angle=angle, expand=True)

    img.save("static/images/original.png")
    rotated_img.save("static/images/rotated.png")

    #Создаем массивы изображений
    imx=np.array(img)
    rotated_imx=np.array(rotated_img)

    r_imx,g_imx,b_imx=imx[:,:,0], imx[:,:,1], imx[:,:,2]
    r_rot, g_rot, b_rot = rotated_imx[:,:,0], rotated_imx[:,:,1], rotated_imx[:,:,2]

    plt.hist(r_imx.flatten(), bins=256)
    plt.savefig("static/hist/r_histogram.png")
    plt.close()

    plt.hist(g_imx.flatten(), bins=256)
    plt.savefig("static/hist/g_histogram.png")
    plt.close()

    plt.hist(b_imx.flatten(), bins=256)
    plt.savefig("static/hist/b_histogram.png")
    plt.close()

    plt.hist(r_rot.flatten(), bins=256)
    plt.savefig("static/hist/r_histogram_rot.png")
    plt.close()

    plt.hist(g_rot.flatten(), bins=256)
    plt.savefig("static/hist/g_histogram_rot.png")
    plt.close()

    plt.hist(b_rot.flatten(), bins=256)
    plt.savefig("static/hist/b_histogram_rot.png")
    plt.close()

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "original": "/static/Images/original.png",
            "rotated": "/static/Images/rotated.png",
            "r_imx": "/static/hist/r_histogram.png",
            "g_imx": "/static/hist/g_histogram.png",
            "b_imx": "/static/hist/b_histogram.png",
            "r_rot": "/static/hist/r_histogram_rot.png",
            "g_rot": "/static/hist/g_histogram_rot.png",
            "b_rot": "/static/hist/b_histogram_rot.png",
        }
    )
