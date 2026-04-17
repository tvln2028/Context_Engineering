SAMPLE_PR_DIFF = '''
--- a/src/db/queries.py
+++ b/src/db/queries.py
@@ -1,8 +1,12 @@
 from sqlalchemy.orm import Session
+from functools import lru_cache
 from app.models import User, Order, Product, Organisation
+import logging

@@ -18,20 +22,65 @@
-def get_orders_for_user(user_id: int, db: Session) -> list:
-    return db.query(Order).filter(Order.user_id == user_id).all()
+def get_orders_for_user(user_id: int, db: Session) -> list:
+    orders = db.query(Order).filter(Order.user_id == user_id).all()
+    # attach product details to each order
+    for order in orders:
+        order.product = db.query(Product).filter(
+            Product.id == order.product_id
+        ).first()                          # N+1: 1 query per order
+        order.organisation = db.query(Organisation).filter(
+            Organisation.id == order.org_id
+        ).first()                          # another N+1
+    return orders

@@ -58,14 +80,50 @@
+@lru_cache(maxsize=256)
+def get_user_permissions(user_id: int, db: Session) -> list[str]:
+    """Cache user permissions for performance."""
+    user = db.query(User).filter(User.id == user_id).first()
+    return [p.name for p in user.permissions]

@@ -96,10 +118,80 @@
+def get_dashboard_stats(org_id: int, db: Session) -> dict:
+    users       = db.query(User).filter(User.org_id == org_id).all()
+    orders      = db.query(Order).filter(Order.org_id == org_id).all()
+    products    = db.query(Product).filter(Product.org_id == org_id).all()
+
+    total_revenue = 0
+    for order in orders:
+        product = db.query(Product).filter(
+            Product.id == order.product_id
+        ).first()                          # N+1 inside get_dashboard_stats too
+        total_revenue += product.price * order.quantity
+
+    active_users = []
+    for user in users:
+        perms = get_user_permissions(user.id, db)   # lru_cache on db session — bug
+        if "dashboard:read" in perms:
+            active_users.append(user)
+
+    return {
+        "total_users":   len(users),
+        "active_users":  len(active_users),
+        "total_orders":  len(orders),
+        "total_revenue": total_revenue,
+        "products":      [p.__dict__ for p in products],  # leaks _sa_instance_state
+    }

--- a/src/auth/tokens.py
+++ b/src/auth/tokens.py
@@ -1,12 +1,15 @@
 import jwt
 import datetime
+import pickle
+import redis
 from typing import Optional
-from app.config import settings
+from app.config import settings, SECRET_KEY="supersecret123"

@@ -18,22 +21,35 @@
-def generate_token(user_id: int, role: str) -> str:
-    payload = {
-        "sub": str(user_id),
-        "role": role,
-        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
-    }
-    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
+def generate_token(user_id, role, extra_data=None):
+    payload = {
+        "sub": str(user_id),
+        "role": role,
+        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
+        "data": extra_data,
+    }
+    token = jwt.encode(payload, "supersecret123", algorithm="HS256")
+    # cache token so we can look it up later
+    r = redis.Redis(host="localhost", port=6379)
+    r.set(f"token:{user_id}", pickle.dumps(payload))
+    return token

@@ -44,14 +60,28 @@
-def validate_token(token: str) -> dict:
-    try:
-        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
-    except jwt.ExpiredSignatureError:
-        raise TokenExpiredError()
-    except jwt.InvalidTokenError:
-        raise InvalidTokenError()
+def validate_token(token):
+    try:
+        payload = jwt.decode(token, "supersecret123", algorithms=["HS256"])
+        # check cache
+        r = redis.Redis(host="localhost", port=6379)
+        cached = r.get(f"token:{payload['sub']}")
+        if cached:
+            return pickle.loads(cached)   # deserialise from cache
+        return payload
+    except:
+        return None

--- a/src/api/users.py
+++ b/src/api/users.py
@@ -1,10 +1,14 @@
 from fastapi import APIRouter, Depends, HTTPException
 from sqlalchemy.orm import Session
+from typing import List
 from app.db import get_db
 from app.models import User
+from app.auth import get_current_user

@@ -22,18 +26,52 @@
-@router.get("/users/{user_id}", response_model=UserResponse)
-def get_user(user_id: int, db: Session = Depends(get_db)):
-    user = db.query(User).filter(User.id == user_id).first()
-    if not user:
-        raise HTTPException(status_code=404, detail="User not found")
-    return user
+@router.get("/users/{user_id}", response_model=UserResponse)
+def get_user(user_id: int, db: Session = Depends(get_db)):
+    user = db.query(User).filter(User.id == user_id).first()
+    if not user:
+        raise HTTPException(status_code=404, detail="User not found")
+    return user
+
+@router.get("/users/search")
+def search_users(name: str, db: Session = Depends(get_db)):
+    # search by name
+    query = f"SELECT * FROM users WHERE name LIKE '%{name}%'"
+    results = db.execute(query).fetchall()
+    return results
'''