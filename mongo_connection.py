from pymongo import MongoClient
import json
from bson import ObjectId
import datetime


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle MongoDB ObjectId and other BSON types"""

    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, (datetime.datetime, datetime.date)):
            # Represent datetimes as ISO-8601 strings (JSON has no native datetime)
            return obj.isoformat()
        return super().default(obj)


def connect_and_query_mongodb() -> list | None:  # noqa: D401
    """Connect to MongoDB, find documents by ``pmc_id`` and print them in full.

    Changes from the previous version:
    1.  Searches **only** the ``evidence-db-test`` database instead of looping
        through every non-system database.
    2.  When a document is retrieved it is printed in its entirety (already done
        via ``json.dumps`` – left intact).
    3.  When no matching document is found we still print a *full* sample
        document to help understand the collection structure (not just its
        keys).
    """

    # Connection details – change as necessary
    host = "localhost"
    port = 27018
    username = "root"
    password = "root"

    # Search parameters
    target_pmc_id = "PMC10300813"
    db_name = "evidence-db-test"

    client: MongoClient | None = None
    try:
        # Build and verify the connection
        connection_string = f"mongodb://{username}:{password}@{host}:{port}"
        client = MongoClient(connection_string)
        client.admin.command("ping")
        print("✅ Successfully connected to MongoDB!")

        # Select the target database
        db = client[db_name]
        collections = db.list_collection_names()
        print(f"\n📚 Using database: '{db_name}'. Collections: {collections}")

        all_results: list[dict] = []
        for collection_name in collections:
            collection = db[collection_name]
            documents = list(collection.find({"pmc_id": target_pmc_id}))

            if documents:
                print(
                    f"\n✨ Found {len(documents)} document(s) in "
                    f"{db_name}.{collection_name}"
                )
                all_results.extend(documents)

                # Display each document in full
                for i, doc in enumerate(documents, 1):
                    print(f"\n--- Document {i} ({collection_name}) ---")
                    print(json.dumps(doc, indent=2, cls=CustomJSONEncoder))

        # If nothing found, show one sample document in full for reference
        if not all_results:
            print(
                f"\n❌ No documents found with pmc_id: {target_pmc_id} in '{db_name}'."
            )
            print("\n🔍 Showing a sample document to understand structure:")
            for collection_name in collections:
                sample_doc = db[collection_name].find_one()
                if sample_doc:
                    print(f"\nSample from {db_name}.{collection_name}:")
                    print(json.dumps(sample_doc, indent=2, cls=CustomJSONEncoder))
                    break

        return all_results

    except Exception as e:  # pragma: no cover – simple script, not unit-tested
        print(f"❌ Error: {e}")
        return None

    finally:
        if client is not None:
            client.close()
            print("\n🔌 Connection closed")


if __name__ == "__main__":
    connect_and_query_mongodb()
