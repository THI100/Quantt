import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import principal, report, set
from utils import log
from utils.stream_manager import log_stream

app = FastAPI(title="quantt_engine")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create instances of logging and app.
log.setup_logging(stream_callback=log_stream.broadcast)
app.include_router(principal.route)
app.include_router(report.r_route)
app.include_router(set.s_route)

if __name__ == "__main__":
    # Run the web server
    uvicorn.run(app, host="0.0.0.0", port=8000)
