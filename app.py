from fastapi import FastAPI, status, HTTPException, Request
from fastapi.responses import JSONResponse,  FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import auth, user, redirect_url, links, qr_codes, redirect_qr_code, event_log
app = FastAPI()
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(links.router)
app.include_router(redirect_url.router)
app.include_router(redirect_qr_code.router)
app.include_router(event_log.router)

app.include_router(qr_codes.router)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "https://s.ppluchuli.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def index(request: Request):
    return FileResponse("./static/html/index.html", media_type="text/html")


@app.get("/signup", include_in_schema=False)
async def index(request: Request):
    return FileResponse("./static/html/signup.html", media_type="text/html")


@app.get("/signin", include_in_schema=False)
async def index(request: Request):
    return FileResponse("./static/html/signin.html", media_type="text/html")


@app.get("/links", include_in_schema=False)
async def index(request: Request):
    return FileResponse("./static/html/links.html", media_type="text/html")


@app.get("/links/create", include_in_schema=False)
async def index(request: Request):
    return FileResponse("./static/html/createLinks.html", media_type="text/html")


@app.get("/links/update", include_in_schema=False)
async def index(request: Request):
    return FileResponse("./static/html/editLinks.html", media_type="text/html")


@app.get("/links/{uuid}", include_in_schema=False)
async def index(request: Request,  uuid: str):
    return FileResponse("./static/html/links-analytics.html", media_type="text/html")


@app.get("/qrcodes", include_in_schema=False)
async def index(request: Request):
    return FileResponse("./static/html/qrcodes.html", media_type="text/html")


@app.get("/qrcodes/create", include_in_schema=False)
async def index(request: Request):
    return FileResponse("./static/html/createQrcodes.html", media_type="text/html")


@app.get("/qrcodes/{id}", include_in_schema=False)
async def index(request: Request, id: int):
    return FileResponse("./static/html/qrcodesDetail.html", media_type="text/html")


@app.get("/analytics", include_in_schema=False)
async def index(request: Request):
    return FileResponse("./static/html/analyticsAllLinks.html", media_type="text/html")


@app.get("/analytics/trend", include_in_schema=False)
async def index(request: Request):
    return FileResponse("./static/html/trending.html", media_type="text/html")


@app.get("/analytics/geoplot", include_in_schema=False)
async def index(request: Request):
    return FileResponse("./static/html/geoPlot.html", media_type="text/html")


@app.get("/campaign", include_in_schema=False)
async def index(request: Request):
    return FileResponse("./static/html/campaign.html", media_type="text/html")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(content={"error": True, "message": exc.detail}, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    error_message = exc.errors()
    message = error_message[0].get("msg")
    return JSONResponse(content={"error": True, "message": message}, status_code=status.HTTP_400_BAD_REQUEST)


@app.get("/{full_path:path}")
def page_not_found(full_path: str):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Page was not found")
