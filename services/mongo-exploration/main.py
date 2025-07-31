#!/usr/bin/env python3
"""
MongoDB Beanie Test CLI

A simple CLI script to demonstrate Beanie ODM functionality and potential issues.
This script creates sample data with linked documents and tests various Beanie operations.
"""

import asyncio
import argparse
import sys
from mongo_connection import run_mongodb_test, MongoDBManager


def main():
    parser = argparse.ArgumentParser(
        description="MongoDB Beanie Test - Demonstrate ODM functionality and potential issues"
    )
    parser.add_argument(
        "--pmc-id", 
        default="PMC10300813",
        help="PMC ID to search for (default: PMC10300813)"
    )
    parser.add_argument(
        "--host",
        default="localhost", 
        help="MongoDB host (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=27019,
        help="MongoDB port (default: 27019)"
    )
    parser.add_argument(
        "--database",
        default="evidence-db-test",
        help="Database name (default: evidence-db-test)"
    )
    parser.add_argument(
        "--create-only",
        action="store_true",
        help="Only create sample data, don't run tests"
    )
    parser.add_argument(
        "--search-only", 
        action="store_true",
        help="Only search for existing data, don't create new data"
    )
    
    args = parser.parse_args()
    
    print("🚀 Starting MongoDB Beanie Test")
    print(f"   Database: {args.database}")
    print(f"   Connection: {args.host}:{args.port}")
    print(f"   PMC ID: {args.pmc_id}")
    print()

    if args.create_only:
        asyncio.run(create_sample_data_only(args))
    elif args.search_only:
        asyncio.run(search_data_only(args))
    else:
        asyncio.run(run_mongodb_test(args.pmc_id))


async def create_sample_data_only(args):
    """Create sample data only"""
    manager = MongoDBManager(
        host=args.host,
        port=args.port, 
        database=args.database
    )
    
    try:
        await manager.connect()
        await manager.create_sample_data()
        print("\n✅ Sample data creation completed!")
    except Exception as e:
        print(f"\n❌ Failed to create sample data: {e}")
        sys.exit(1)
    finally:
        await manager.disconnect()


async def search_data_only(args):
    """Search for existing data only"""
    manager = MongoDBManager(
        host=args.host,
        port=args.port,
        database=args.database
    )
    
    try:
        await manager.connect()
        articles = await manager.find_articles_by_pmc_id(args.pmc_id)
        
        if articles:
            print(f"\n✅ Found {len(articles)} article(s)")
        else:  
            print(f"\n❌ No articles found with PMC ID: {args.pmc_id}")
            
    except Exception as e:
        print(f"\n❌ Search failed: {e}")
        sys.exit(1)
    finally:
        await manager.disconnect()


if __name__ == "__main__":
    main()
