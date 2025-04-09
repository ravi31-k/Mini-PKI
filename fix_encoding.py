# fix_encoding.py
with open("revoked.txt", "rb") as f:
    content = f.read()

# Save as UTF-8
with open("revoked.txt", "w", encoding="utf-8") as f:
    f.write(content.decode("utf-16"))
