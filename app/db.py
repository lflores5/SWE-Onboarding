import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from azure.cosmos import PartitionKey
from azure.cosmos.cosmos_client import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError

from app.models import Ticket

logger = logging.getLogger(__name__)


class TicketRepository(ABC):
    @abstractmethod
    def list_tickets(self) -> List[Ticket]:
        raise NotImplementedError

    @abstractmethod
    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        raise NotImplementedError

    @abstractmethod
    def create_ticket(self, ticket: Ticket) -> Ticket:
        raise NotImplementedError

    @abstractmethod
    def update_ticket(self, ticket: Ticket) -> Optional[Ticket]:
        raise NotImplementedError

    @abstractmethod
    def delete_ticket(self, ticket_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def backend_name(self) -> str:
        raise NotImplementedError


class InMemoryTicketRepository(TicketRepository):
    def __init__(self) -> None:
        self._tickets: Dict[str, Ticket] = {}

    def list_tickets(self) -> List[Ticket]:
        return list(self._tickets.values())

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        return self._tickets.get(ticket_id)

    def create_ticket(self, ticket: Ticket) -> Ticket:
        self._tickets[ticket.id] = ticket
        return ticket

    def update_ticket(self, ticket: Ticket) -> Optional[Ticket]:
        if ticket.id not in self._tickets:
            return None
        self._tickets[ticket.id] = ticket
        return ticket

    def delete_ticket(self, ticket_id: str) -> bool:
        return self._tickets.pop(ticket_id, None) is not None

    def backend_name(self) -> str:
        return "memory"


class CosmosTicketRepository(TicketRepository):
    def __init__(self) -> None:
        endpoint = os.environ["COSMOS_DB_ENDPOINT"]
        key = os.environ["COSMOS_DB_KEY"]
        db_name = os.getenv("COSMOS_DB_NAME", "support")
        container_name = os.getenv("COSMOS_CONTAINER_NAME", "tickets")

        client = CosmosClient(endpoint, credential=key)
        db = client.create_database_if_not_exists(id=db_name)
        self.container = db.create_container_if_not_exists(
            id=container_name,
            partition_key=PartitionKey(path="/id"),
        )

    def list_tickets(self) -> List[Ticket]:
        rows = self.container.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True,
        )
        return [Ticket.model_validate(row) for row in rows]

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        try:
            doc = self.container.read_item(item=ticket_id, partition_key=ticket_id)
            return Ticket.model_validate(doc)
        except CosmosResourceNotFoundError:
            return None

    def create_ticket(self, ticket: Ticket) -> Ticket:
        doc = self.container.create_item(body=ticket.model_dump())
        return Ticket.model_validate(doc)

    def update_ticket(self, ticket: Ticket) -> Optional[Ticket]:
        if not self.get_ticket(ticket.id):
            return None
        doc = self.container.upsert_item(body=ticket.model_dump())
        return Ticket.model_validate(doc)

    def delete_ticket(self, ticket_id: str) -> bool:
        if not self.get_ticket(ticket_id):
            return False
        self.container.delete_item(item=ticket_id, partition_key=ticket_id)
        return True

    def backend_name(self) -> str:
        return "azure-cosmos"


def create_repository() -> TicketRepository:
    if os.getenv("COSMOS_DB_ENDPOINT") and os.getenv("COSMOS_DB_KEY"):
        try:
            return CosmosTicketRepository()
        except Exception as exc:
            logger.exception("Cosmos initialization failed; falling back to memory: %s", exc)
    return InMemoryTicketRepository()
