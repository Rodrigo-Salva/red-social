import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app import crud, schemas, models
from app.core import security
from datetime import timedelta

def seed_data():
    db = SessionLocal()
    try:
        # 1. Crear usuarios de prueba
        test_users = [
            {
                "email": "kernel@tech.com",
                "username": "kernel_panic",
                "full_name": "Kernel Master",
                "password": "password123",
                "bio": "Low level enthusiast. C/C++ and Assembly deep learner."
            },
            {
                "email": "neural@tech.com",
                "username": "neural_net",
                "full_name": "AI Researcher",
                "password": "password123",
                "bio": "Transforming data into insights. PyTorch & JAX explorer."
            },
            {
                "email": "zero@tech.com",
                "username": "zero_day",
                "full_name": "Security Expert",
                "password": "password123",
                "bio": "Finding vulnerabilities before they find us. Red Teamer."
            }
        ]

        created_users = []
        for u_data in test_users:
            user = crud.crud_user.get_user_by_email(db, email=u_data["email"])
            if not user:
                user_in = schemas.user.UserCreate(
                    email=u_data["email"],
                    username=u_data["username"],
                    full_name=u_data["full_name"],
                    password=u_data["password"]
                )
                user = crud.crud_user.create_user(db, user=user_in)
                # Actualizar bio manualmente ya que UserCreate no suele incluirla por defecto en simples setups
                user.is_private = False
                db.add(user)
                db.commit()
                db.refresh(user)
            created_users.append(user)

        # 2. Crear publicaciones de prueba
        posts_data = [
            {
                "content": "Just optimized a hot path in my custom memory allocator. \n\n```c\nvoid* alloc(size_t size) {\n    // Magic happens here\n    return segment + offset;\n}\n```\nFeeling productive! #LowLevel #Performance",
                "user_idx": 0
            },
            {
                "content": "Training a 7B parameter model on a single GPU using 4-bit quantization. The loss curve looks amazing! 📉 #MachineLearning #LLM",
                "user_idx": 1
            },
            {
                "content": "Pro-tip: Always sanitize your inputs. Found a nasty RCE in a legacy system today. 🛡️ #CyberSecurity #BugBounty",
                "user_idx": 2
            },
            {
                "content": "Check out this clean React architecture I'm building. \n\n![Arch](https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&q=80&w=1000)\n\nSeparation of concerns is key. #ReactJS #WebDev",
                "user_idx": 0
            }
        ]

        for p_data in posts_data:
            post_in = schemas.post.PostCreate(
                title="Update",
                content=p_data["content"]
            )
            crud.crud_post.create_user_post(db, post=post_in, owner_id=created_users[p_data["user_idx"]].id)

        # 3. Simular interacciones (seguidores)
        if len(created_users) >= 3:
            # User 0 follows 1 and 2
            crud.crud_user.follow_user(db, follower=created_users[0], to_follow=created_users[1])
            crud.crud_user.follow_user(db, follower=created_users[0], to_follow=created_users[2])
            # User 1 follows 0
            crud.crud_user.follow_user(db, follower=created_users[1], to_follow=created_users[0])

        print("Successfully seeded test data!")

    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
