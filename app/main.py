import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.responses import Response as StarletteResponse

from app.db import create_repository
from app.models import Ticket, TicketCreate, TicketUpdate, now_utc_iso

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("tickets-api")

app = FastAPI(title="Support Tickets API", version="1.0.0")
repository = create_repository()


@app.middleware("http")
async def request_logging_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[StarletteResponse]]
) -> StarletteResponse:
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info("%s %s status=%s duration_ms=%s", request.method, request.url.path, response.status_code, duration_ms)
    return response


@app.get("/health")
def health_check() -> JSONResponse:
    return JSONResponse({"status": "ok", "database_backend": repository.backend_name()})


@app.post("/tickets", response_model=Ticket, status_code=201)
def create_ticket(payload: TicketCreate) -> Ticket:
    ticket = Ticket(
        id=str(uuid.uuid4()),
        title=payload.title,
        description=payload.description,
        status=payload.status,
        created_at=now_utc_iso(),
        updated_at=now_utc_iso(),
    )
    return repository.create_ticket(ticket)


@app.get("/tickets", response_model=list[Ticket])
def list_tickets() -> list[Ticket]:
    return repository.list_tickets()


@app.get("/tickets/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: str) -> Ticket:
    ticket = repository.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.patch("/tickets/{ticket_id}", response_model=Ticket)
def update_ticket(ticket_id: str, payload: TicketUpdate) -> Ticket:
    current = repository.get_ticket(ticket_id)
    if not current:
        raise HTTPException(status_code=404, detail="Ticket not found")

    updates = payload.model_dump(exclude_unset=True)
    updated = Ticket(
        id=current.id,
        title=updates.get("title", current.title),
        description=updates.get("description", current.description),
        status=updates.get("status", current.status),
        created_at=current.created_at,
        updated_at=now_utc_iso(),
    )
    saved = repository.update_ticket(updated)
    if not saved:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return saved


@app.delete("/tickets/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: str) -> Response:
    deleted = repository.delete_ticket(ticket_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return Response(status_code=204)
