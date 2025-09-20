#!/usr/bin/env python3
"""
Example usage of AccessNode with local PostgreSQL database
This demonstrates practical use cases for the AccessNode SDK
"""
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from accessnode import AccessNode

# Load environment variables
load_dotenv()

class AccessNodeExample:
    def __init__(self):
        self.db = AccessNode(
            db_type="postgresql",
            database_name=os.getenv('POSTGRES_DB', 'accessnode_main'),
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=int(os.getenv('POSTGRES_PORT', '5432')),
            username=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD')
        )

    async def __aenter__(self):
        await self.db.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.db.close()

    async def setup_database_schema(self):
        """Create tables for our example application"""
        print("🔧 Setting up database schema...")

        # Users table
        await self.db.raw_query("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                full_name VARCHAR(100),
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            );
        """)

        # Posts table
        await self.db.raw_query("""
            CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                content TEXT,
                author_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                published BOOLEAN DEFAULT false,
                tags TEXT[],
                view_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Comments table
        await self.db.raw_query("""
            CREATE TABLE IF NOT EXISTS comments (
                id SERIAL PRIMARY KEY,
                post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
                author_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        print("✅ Database schema created successfully!")

    async def create_sample_users(self):
        """Create sample users using AccessNode CRUD operations"""
        print("\n👥 Creating sample users...")

        users = [
            {
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "last_login": datetime.now() - timedelta(days=1)
            },
            {
                "username": "jane_smith",
                "email": "jane@example.com",
                "full_name": "Jane Smith",
                "last_login": datetime.now() - timedelta(hours=2)
            },
            {
                "username": "bob_wilson",
                "email": "bob@example.com",
                "full_name": "Bob Wilson",
                "last_login": datetime.now() - timedelta(minutes=30)
            }
        ]

        user_ids = []
        for user_data in users:
            # Check if user already exists
            existing_user = await self.db.get("users", {"username": user_data["username"]})
            if existing_user:
                print(f"  - User {user_data['username']} already exists")
                user_ids.append(existing_user["id"])
            else:
                user_id = await self.db.insert("users", user_data)
                user_ids.append(user_id)
                print(f"  - Created user: {user_data['username']} (ID: {user_id})")

        return user_ids

    async def create_sample_posts(self, user_ids):
        """Create sample posts"""
        print("\n📝 Creating sample posts...")

        posts = [
            {
                "title": "Getting Started with AccessNode",
                "content": "AccessNode makes database operations simple and secure...",
                "author_id": user_ids[0],
                "published": True,
                "tags": ["tutorial", "database", "python"]
            },
            {
                "title": "Advanced Database Patterns",
                "content": "Learn about advanced database design patterns...",
                "author_id": user_ids[1],
                "published": True,
                "tags": ["advanced", "patterns", "database"]
            },
            {
                "title": "Draft: Performance Optimization",
                "content": "This is a draft post about performance...",
                "author_id": user_ids[2],
                "published": False,
                "tags": ["performance", "optimization"]
            }
        ]

        post_ids = []
        for post_data in posts:
            post_id = await self.db.insert("posts", post_data)
            post_ids.append(post_id)
            status = "published" if post_data["published"] else "draft"
            print(f"  - Created post: '{post_data['title']}' ({status}) (ID: {post_id})")

        return post_ids

    async def create_sample_comments(self, post_ids, user_ids):
        """Create sample comments"""
        print("\n💬 Creating sample comments...")

        comments = [
            {
                "post_id": post_ids[0],
                "author_id": user_ids[1],
                "content": "Great tutorial! Very helpful for beginners."
            },
            {
                "post_id": post_ids[0],
                "author_id": user_ids[2],
                "content": "Thanks for sharing this. Looking forward to more content."
            },
            {
                "post_id": post_ids[1],
                "author_id": user_ids[0],
                "content": "Excellent deep dive into database patterns!"
            }
        ]

        for comment_data in comments:
            comment_id = await self.db.insert("comments", comment_data)
            print(f"  - Created comment on post {comment_data['post_id']} (ID: {comment_id})")

    async def demonstrate_queries(self):
        """Demonstrate various query patterns"""
        print("\n🔍 Demonstrating query patterns...")

        # 1. Simple select with conditions
        print("\n1. Finding active users:")
        active_users = await self.db.get_all("users", {"is_active": True})
        for user in active_users:
            print(f"   - {user['full_name']} (@{user['username']})")

        # 2. Complex join query
        print("\n2. Posts with author information:")
        posts_with_authors = await self.db.raw_query("""
            SELECT p.title, p.published, p.view_count, u.full_name as author_name, u.username
            FROM posts p
            JOIN users u ON p.author_id = u.id
            ORDER BY p.created_at DESC;
        """)

        for post in posts_with_authors:
            status = "📚 Published" if post['published'] else "📝 Draft"
            print(f"   - {status}: '{post['title']}' by {post['author_name']}")

        # 3. Aggregation query
        print("\n3. Comment count per post:")
        comment_stats = await self.db.raw_query("""
            SELECT p.title, COUNT(c.id) as comment_count
            FROM posts p
            LEFT JOIN comments c ON p.id = c.post_id
            GROUP BY p.id, p.title
            ORDER BY comment_count DESC;
        """)

        for stat in comment_stats:
            print(f"   - '{stat['title']}': {stat['comment_count']} comments")

        # 4. Update operation
        print("\n4. Updating view counts:")
        await self.db.update("posts", {"published": True}, {"view_count": 42})
        print("   - Updated view counts for published posts")

        # 5. Raw query with parameters
        print("\n5. Recent users (last 7 days):")
        recent_users = await self.db.raw_query("""
            SELECT username, full_name, last_login
            FROM users
            WHERE last_login > $1
            ORDER BY last_login DESC;
        """, [datetime.now() - timedelta(days=7)])

        for user in recent_users:
            print(f"   - {user['full_name']}: {user['last_login'].strftime('%Y-%m-%d %H:%M')}")

    async def demonstrate_crud_operations(self):
        """Demonstrate Create, Read, Update, Delete operations"""
        print("\n🔄 Demonstrating CRUD operations...")

        # CREATE
        print("\n1. CREATE - Adding a new user:")
        new_user_data = {
            "username": "alice_cooper",
            "email": "alice@example.com",
            "full_name": "Alice Cooper",
            "last_login": datetime.now()
        }
        user_id = await self.db.insert("users", new_user_data)
        print(f"   - Created user with ID: {user_id}")

        # READ
        print("\n2. READ - Fetching the new user:")
        user = await self.db.get("users", {"id": user_id})
        print(f"   - Found user: {user['full_name']} ({user['email']})")

        # UPDATE
        print("\n3. UPDATE - Updating user information:")
        await self.db.update(
            "users",
            {"id": user_id},
            {"full_name": "Alice M. Cooper", "last_login": datetime.now()}
        )
        updated_user = await self.db.get("users", {"id": user_id})
        print(f"   - Updated user: {updated_user['full_name']}")

        # DELETE
        print("\n4. DELETE - Removing the user:")
        await self.db.delete("users", {"id": user_id})
        deleted_user = await self.db.get("users", {"id": user_id})
        print(f"   - User deleted: {deleted_user is None}")

    async def performance_examples(self):
        """Demonstrate performance-related features"""
        print("\n⚡ Performance examples...")

        # Batch operations
        print("\n1. Batch insert example:")
        start_time = datetime.now()

        # Insert multiple records efficiently
        batch_users = []
        for i in range(5):
            user_data = {
                "username": f"batch_user_{i}",
                "email": f"batch{i}@example.com",
                "full_name": f"Batch User {i}"
            }
            await self.db.insert("users", user_data)
            batch_users.append(user_data)

        end_time = datetime.now()
        print(f"   - Inserted {len(batch_users)} users in {(end_time - start_time).total_seconds():.3f}s")

        # Clean up batch users
        for user_data in batch_users:
            await self.db.delete("users", {"username": user_data["username"]})

async def main():
    """Main example function"""
    print("🚀 AccessNode Local Database Example")
    print("=" * 50)

    try:
        async with AccessNodeExample() as example:
            # Set up the database
            await example.setup_database_schema()

            # Create sample data
            user_ids = await example.create_sample_users()
            post_ids = await example.create_sample_posts(user_ids)
            await example.create_sample_comments(post_ids, user_ids)

            # Demonstrate various operations
            await example.demonstrate_queries()
            await example.demonstrate_crud_operations()
            await example.performance_examples()

            print("\n🎉 Example completed successfully!")
            print("\n💡 Next steps:")
            print("   - Check your pgAdmin4 to see the created tables and data")
            print("   - Modify this script to test your own use cases")
            print("   - Try the API endpoints with: uvicorn main:app --reload")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure to:")
        print("   1. Update your .env file with correct database credentials")
        print("   2. Ensure PostgreSQL is running and accessible")
        print("   3. Verify the 'accessnode_main' database exists")

if __name__ == "__main__":
    asyncio.run(main())