from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password = "admin"
hashed_password = pwd_context.hash(password)

query = f"""
INSERT INTO users (first_name, last_name, national_code, phone_number, role, hashed_password)
VALUES (
    'Super',
    'Admin',
    '0000000001',
    '09123456789',
    'admin',
    '{hashed_password}'
);
"""

print(query)