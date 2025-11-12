import hashlib

answer = "Singapore".strip().lower()  # normalize spacing + case
hash_value = hashlib.sha256(answer.encode()).hexdigest()
print(hash_value)
