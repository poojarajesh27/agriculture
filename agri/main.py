from fastapi import FastAPI,Form,Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import psycopg2
import time
from psycopg2.extras import RealDictCursor

app=FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")

while True:
    try:
        conn=psycopg2.connect(host='localhost',database='agri',user='postgres',password='gunapooja27',cursor_factory=RealDictCursor)
        cursor=conn.cursor()
        print("database connected successfully")
        break
    except Exception as error:
        print("database connection failed",error)
        time.sleep(3)

#Template setup
templates=Jinja2Templates(directory="templates")

@app.get("/",response_class=HTMLResponse) 
def read_root(request:Request):
    return templates.TemplateResponse("home.html",{"request":request})

@app.get("/home",response_class=HTMLResponse) 
def home(request:Request):
    return templates.TemplateResponse("home.html",{"request":request})


@app.get("/crop-select",response_class=HTMLResponse)
def cropselect(request:Request):
    return templates.TemplateResponse("crop-select.html",{"request":request})

@app.get("/crop-details",response_class=HTMLResponse)
def cropdetail(request:Request):
    return templates.TemplateResponse("crop-details.html",{"request":request})

@app.get("/terrace",response_class=HTMLResponse)
def terrace(request:Request):
    return templates.TemplateResponse("terrace.html",{"request":request})

@app.get("/profit",response_class=HTMLResponse)
def profit(request:Request):
    return templates.TemplateResponse("profit.html",{"request":request})

@app.get("/query",response_class=HTMLResponse)
def query(request:Request):
    return templates.TemplateResponse("query.html",{"request":request})

@app.get("/feedback",response_class=HTMLResponse)
def feedback(request:Request):
    return templates.TemplateResponse("feedback.html",{"request":request})

@app.get("/admin",response_class=HTMLResponse)
def admin(request:Request):
    return templates.TemplateResponse("admin.html",{"request":request})

@app.post("/crop-select", response_class=HTMLResponse)
def crops(request: Request, soil: str = Form(...)):
    cursor.execute("""SELECT "soil-type",crop,demand,"amount(per acre)" FROM "crop-select" WHERE "soil-type" = %s""", (soil,))
    rows = cursor.fetchall()
    columns=[desc[0] for desc in cursor.description]
    return templates.TemplateResponse("crop-select.html", {"request": request, "rows":rows,"columns":columns})

@app.post("/crop-details", response_class=HTMLResponse)
def cropd(request: Request, crops: str = Form(...)):
    cursor.execute("""SELECT crop,"crop-type",season,"health-benefit",fertilizer,"height(cm)","grow-time(days)" FROM "crop-detail" WHERE crop = %s""", (crops,))
    rows = cursor.fetchall()
    columns=[desc[0] for desc in cursor.description]
    return templates.TemplateResponse("crop-details.html", {"request": request, "rows":rows,"columns":columns})


@app.post("/terrace", response_class=HTMLResponse)
def cropt(request: Request, crop: str = Form(...)):
    cursor.execute("""SELECT "crop-type",crop,"sunlight(hrs/day)",water,"area(sq ft)","container-size","grow-time(days)",others FROM terrace WHERE "crop-type" = %s""", (crop,))
    rows = cursor.fetchall()
    columns=[desc[0] for desc in cursor.description]
    return templates.TemplateResponse("terrace.html", {"request": request, "rows":rows,"columns":columns})


@app.post("/profit", response_class=HTMLResponse)
def cprofit(request: Request, plcrop: str = Form(...)):
    cursor.execute("""SELECT cname,"soil-type",crop,"profit-loss",amount,"area(sq ft)" FROM customer WHERE crop = %s""", (plcrop,))
    rows = cursor.fetchall()
    columns=[desc[0] for desc in cursor.description]
    return templates.TemplateResponse("profit.html", {"request": request, "rows":rows,"columns":columns})


@app.post("/query", response_class=HTMLResponse)
def cropt(request: Request, name: str = Form(...),phno: str=Form(...),doubt:str=Form(...)):
    cursor.execute("""insert into query(name,phno,doubt) values (%s,%s,%s)""",(name,phno,doubt))
    conn.commit()
    return templates.TemplateResponse("success.html", {"request": request,"message":"✔️query submitted successfully✔️","name":name,"phno":phno,"doubt":doubt})

@app.post("/feedback", response_class=HTMLResponse)
def feed(request: Request, name: str = Form(...),phno: str=Form(...), mail: str = Form(...), address: str = Form(...), soil: str = Form(...), crops: str = Form(...), pl: str = Form(...), amount: str = Form(...), area: str = Form(...)):
    cursor.execute("""insert into customer(cname,phno,mail,address,"soil-type",crop,"profit-loss",amount,"area(sq ft)") values (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(name,phno,mail,address,soil,crops,pl,amount,area))
    conn.commit()
    return templates.TemplateResponse("success1.html", {"request": request,"message":"📝feeback submitted successfully📝"})

@app.post("/admin",response_class=HTMLResponse)
def ad(request:Request,name:str=Form(...),password:str=Form(...)):
    if name=="pooja" and password=="gunapooja27":
        return templates.TemplateResponse("admin1.html",{"request":request})
    return templates.TemplateResponse("admin.html",{"request":request,"message":"‼️sorry invalid username or password‼️"})



@app.post("/admin1",response_class=HTMLResponse)
def cadmin(request:Request,table:str=Form(...),type:str=Form(...),write:str=Form(...)):
    try:
        if type.lower()=="select":
            cursor.execute(write)
            rows = cursor.fetchall()
            columns=[desc[0] for desc in cursor.description]
            return templates.TemplateResponse("show.html", {"request": request, "rows":rows,"columns":columns})
        cursor.execute(write)
        conn.commit()
        return templates.TemplateResponse("show.html",{"request":request,"message":"query executed successfulllly..."})
    except Exception as e:
        print("error",e)
        conn.rollback()
        return templates.TemplateResponse("show.html",{"request":request,"message":str(e)})
        