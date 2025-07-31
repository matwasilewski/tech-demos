import asyncio
from typing import List, Optional

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from document import Document, SystematicReview, ClinicalTrial, StudyOutcome


class MongoDBManager:
    """MongoDB manager using Beanie ODM for async operations that works **only** with
    the evidence-related models declared in `document.py`. It can:

    1.   Connect / disconnect to a MongoDB instance.
    2.   Wipe the target database so we always start from a clean slate.
    3.   Populate the DB with one generic `Document`, two `SystematicReview`s (SRs)
         and two `ClinicalTrial`s (CTs) – all with distinct values.
    4.   Print everything back so you can visually confirm what was written.  
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 27019,
        username: str = "root",
        password: str = "root",
        database: str = "evidence-db-test",
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.client: Optional[AsyncIOMotorClient] = None

    # ---------------------------------------------------------------------
    # Connection helpers
    # ---------------------------------------------------------------------

    async def connect(self):
        """Connect to Mongo and initialise Beanie with our models"""

        connection_string = (
            f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}"
        )
        self.client = AsyncIOMotorClient(connection_string)

        # Validate the connection – will raise if credentials are wrong
        await self.client.server_info()
        print("✅ Successfully connected to MongoDB!")

        # Register the models with Beanie
        await init_beanie(
            database=self.client[self.database],
            document_models=[Document, SystematicReview, ClinicalTrial],
        )
        print(f"📚 Initialized Beanie with database: '{self.database}'")

    async def disconnect(self):
        """Close the underlying Motor client"""
        if self.client:
            self.client.close()
            print("🔌 Connection closed")

    # ---------------------------------------------------------------------
    # House-keeping helpers
    # ---------------------------------------------------------------------

    async def clean_database(self):
        """Drop the entire database so we always start fresh"""
        if not self.client:
            raise RuntimeError("Not connected to MongoDB – call connect() first")

        await self.client.drop_database(self.database)
        print(f"🗑️  Dropped database '{self.database}' (now squeaky clean)")

    # ---------------------------------------------------------------------
    # Sample-data helpers
    # ---------------------------------------------------------------------

    async def create_sample_data(self) -> List[Document]:
        """Create one generic Document, two SRs, and two CTs with different values"""
        print("\n🔧 Creating sample data …")

        # ── Generic base document ──────────────────────────────────────────
        generic_doc = Document(
            title="Evidence Integration Overview",
            abstract="An overview of methods to integrate heterogeneous evidence.",
            authors=["Dr. John Smith", "Dr. Jane Doe"],
        )

        # ── Systematic reviews ────────────────────────────────────────────
        sr_vaccines = SystematicReview(
            title="Efficacy of Modern Vaccines – A Systematic Review",
            abstract="A comprehensive review of 58 clinical trials on modern vaccines.",
            authors=["Alice Johnson"],
            number_of_studies=58,
            primary_outcome=StudyOutcome.positive,
        )

        sr_supplements = SystematicReview(
            title="Dietary Supplements and Weight Loss",
            abstract="Review of interventions that utilise over-the-counter supplements.",
            authors=["Bob Lee", "Carol King"],
            number_of_studies=22,
            primary_outcome=StudyOutcome.mixed,
        )

        # ── Clinical trials ───────────────────────────────────────────────
        ct_drug_a = ClinicalTrial(
            title="Phase-II Trial of Drug-A for Hypertension",
            abstract="Randomised, double-blind, placebo-controlled study assessing Drug-A.",
            authors=["David Wright"],
            number_of_participants=200,
            primary_outcome=StudyOutcome.negative,
        )

        ct_surgery_b = ClinicalTrial(
            title="Minimally-Invasive Surgery-B vs Standard Procedure",
            abstract="Prospective multicentre clinical trial comparing surgical techniques.",
            authors=["Emily Davis", "Frank Moore"],
            number_of_participants=120,
            primary_outcome=StudyOutcome.neutral,
        )

        # Insert all documents into the DB
        for doc in [
            generic_doc,
            sr_vaccines,
            sr_supplements,
            ct_drug_a,
            ct_surgery_b,
        ]:
            await doc.insert()
        print("✅ Sample documents successfully inserted")

        return [
            generic_doc,
            sr_vaccines,
            sr_supplements,
            ct_drug_a,
            ct_surgery_b,
        ]

    # ---------------------------------------------------------------------
    # Utility helpers
    # ---------------------------------------------------------------------

    async def show_all_documents(self):
        """Print every document currently stored (for quick visual confirmation)"""
        docs: List[Document] = await Document.find_all().to_list()
        print(f"\n📄 There are {len(docs)} document(s) in the database:")

        for idx, d in enumerate(docs, start=1):
            print(f"\n—— Document {idx} ———————————————")
            print(d.model_dump_json(indent=2))

    # ---------------------------------------------------------------------
    # High-level orchestration helpers (used by __main__)
    # ---------------------------------------------------------------------

    async def run_demo(self):
        """Full flow: connect → clean → seed → display → disconnect"""
        await self.connect()
        try:
            await self.clean_database()
            await self.create_sample_data()
            await self.show_all_documents()
        finally:
            await self.disconnect()


# -------------------------------------------------------------------------
# Convenience entry-point
# -------------------------------------------------------------------------

async def run_mongodb_test(_unused: str | None = None):
    """External entry point so other modules can kick off the demo quickly"""
    manager = MongoDBManager()
    await manager.run_demo()


if __name__ == "__main__":
    asyncio.run(run_mongodb_test())
