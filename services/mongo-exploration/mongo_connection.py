import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from document import Article, Author, Tag
import json
from datetime import datetime
from typing import List, Optional


class MongoDBManager:
    """MongoDB manager using Beanie ODM for async operations"""
    
    def __init__(self, host: str = "localhost", port: int = 27019, 
                 username: str = "root", password: str = "root", 
                 database: str = "evidence-db-test"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.client: Optional[AsyncIOMotorClient] = None
    
    async def connect(self):
        """Initialize Beanie and connect to MongoDB"""
        try:
            # Build connection string (fixed port to match docker-compose)
            connection_string = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}"
            self.client = AsyncIOMotorClient(connection_string)
            
            # Test connection
            await self.client.server_info()
            print("✅ Successfully connected to MongoDB!")
            
            # Initialize Beanie with document models
            await init_beanie(
                database=self.client[self.database], 
                document_models=[Article, Author, Tag]
            )
            print(f"📚 Initialized Beanie with database: '{self.database}'")
            
        except Exception as e:
            print(f"❌ Connection error: {e}")
            raise
    
    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("🔌 Connection closed")
    
    async def create_sample_data(self):
        """Create sample data to demonstrate Beanie functionality"""
        print("\n🔧 Creating sample data...")
        
        # Create authors
        author1 = Author(
            name="Dr. John Smith", 
            email="john.smith@university.edu",
            affiliation="University Research Lab"
        )
        author2 = Author(
            name="Dr. Jane Doe",
            email="jane.doe@institute.org", 
            affiliation="Medical Research Institute"
        )
        
        await author1.insert()
        await author2.insert()
        print(f"✅ Created authors: {author1.name}, {author2.name}")
        
        # Create tags
        tag1 = Tag(name="Research", color="blue", description="Research articles")
        tag2 = Tag(name="Medical", color="green", description="Medical studies")
        
        await tag1.insert()
        await tag2.insert()
        print(f"✅ Created tags: {tag1.name}, {tag2.name}")
        
        # Create article with links to authors and tags
        article = Article(
            title="Sample Research Article",
            content="This is a sample article demonstrating Beanie ODM functionality.",
            pmc_id="PMC10300813",  # Using the same PMC ID from the original script
            authors=[author1, author2],  # Link to authors
            tags=[tag1, tag2],  # Link to tags
            published_at=datetime.utcnow(),
            is_published=True,
            view_count=42
        )
        
        await article.insert()
        print(f"✅ Created article: {article.title} (ID: {article.id})")
        
        return article, [author1, author2], [tag1, tag2]
    
    async def find_articles_by_pmc_id(self, pmc_id: str) -> List[Article]:
        """Find articles by PMC ID and fetch linked documents"""
        print(f"\n🔍 Searching for articles with PMC ID: {pmc_id}")
        
        articles = await Article.find(Article.pmc_id == pmc_id).to_list()
        
        if articles:
            print(f"✨ Found {len(articles)} article(s)")
            
            for i, article in enumerate(articles, 1):
                print(f"\n--- Article {i} ---")
                print(f"Title: {article.title}")
                print(f"Content: {article.content}")
                print(f"PMC ID: {article.pmc_id}")
                print(f"Published: {article.published_at}")
                print(f"Views: {article.view_count}")
                
                # Fetch linked authors (this might demonstrate Beanie linking issues)
                await article.fetch_all_links()
                
                print(f"Authors ({len(article.authors)}):")
                for author in article.authors:
                    print(f"  - {author.name} ({author.email})")
                
                print(f"Tags ({len(article.tags)}):")
                for tag in article.tags:
                    print(f"  - {tag.name} ({tag.color})")
                
                print(f"Raw document: {article.model_dump_json(indent=2)}")
        else:
            print(f"❌ No articles found with PMC ID: {pmc_id}")
            
            # Show sample data
            sample_article = await Article.find_one()
            if sample_article:
                await sample_article.fetch_all_links()
                print(f"🔍 Sample article for reference:")
                print(f"Raw document: {sample_article.model_dump_json(indent=2)}")
        
        return articles
    
    async def demonstrate_beanie_issue(self):
        """Demonstrate potential Beanie linking or aggregation issues"""
        print("\n🐛 Demonstrating potential Beanie issues...")
        
        # This might showcase problems with:
        # 1. Link fetching
        # 2. Aggregation with linked documents  
        # 3. Serialization issues
        # 4. Performance with many links
        
        try:
            # Find all articles and try to fetch their links
            articles = await Article.find_all().to_list()
            print(f"Found {len(articles)} total articles")
            
            for article in articles:
                print(f"\nProcessing article: {article.title}")
                
                # This might fail or behave unexpectedly
                await article.fetch_all_links()
                
                # Check if links are properly loaded
                print(f"Authors loaded: {len(article.authors)} authors")
                print(f"Tags loaded: {len(article.tags)} tags")
                
                # Try serialization (common issue area)
                try:
                    json_data = article.model_dump_json()
                    print("✅ Serialization successful")
                except Exception as e:
                    print(f"❌ Serialization failed: {e}")
                
        except Exception as e:
            print(f"❌ Beanie operation failed: {e}")
            raise


async def run_mongodb_test(pmc_id: str = "PMC10300813"):
    """Main function to run the MongoDB test with Beanie"""
    manager = MongoDBManager()
    
    try:
        await manager.connect()
        
        # Create sample data
        await manager.create_sample_data()
        
        # Search for documents
        await manager.find_articles_by_pmc_id(pmc_id)
        
        # Demonstrate potential issues
        await manager.demonstrate_beanie_issue()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
    finally:
        await manager.disconnect()


if __name__ == "__main__":
    asyncio.run(run_mongodb_test())
