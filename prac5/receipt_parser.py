import re
import json

# 1. Read the receipt text from file
with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read()

# 2. Regex to extract products

product_pattern = re.compile(
    r"\d+\.\s*\n"
    r"(.+?)\n"
    r"([\d,]+)\s+x\s+([\d ]+,\d{2})\n"
    r"([\d ]+,\d{2})\n"
    r"Стоимость\n"
    r"([\d ]+,\d{2})",
)

products = []

for match in product_pattern.finditer(text):
    # Extract and clean data
    name = match.group(1).strip()
    total_price = match.group(5).replace(" ", "")

    products.append({
        "name": name,
        "total_price": total_price
    })

# 3. Extract total amount from the receipt
total_match = re.search(r"ИТОГО:\n([\d ]+,\d{2})", text)
total_from_receipt = total_match.group(1).replace(" ", "") if total_match else None

# 4. Extract date and time
datetime_match = re.search(r"Время:\s(.+)", text)
datetime_value = datetime_match.group(1) if datetime_match else None

# 5. Extract payment method
payment_match = re.search(r"(Банковская карта|Наличные)", text)
payment_method = payment_match.group(1) if payment_match else None

# 6. Automatically calculate total sum
calculated_total = 0.0
for item in products:
    clean_price = item["total_price"].replace(",", ".")
    calculated_total += float(clean_price)

# 7. Build final dictionary and print as JSON
result = {
    "products": products,
    "total_from_receipt": total_from_receipt,
    "calculated_total": round(calculated_total, 2),
    "datetime": datetime_value,
    "payment_method": payment_method
}

print(json.dumps(result, indent=4, ensure_ascii=False))
