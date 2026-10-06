# Expense Tracker

A terminal app for logging grocery receipts and querying them later. You enter each receipt once (date, store, total paid, notes and one line per product). After that you can look up and delete your purchases by period, store, product or category.

Prices are in Mexican pesos (MXN). Quantities aren't tracked: each product is a single line on a receipt, no matter how many units or kilos you bought.

## Why

I keep my grocery receipts, but on paper they're useless: I can't tell how much I've spent on meat this month, how often I buy shampoo, or whether chicken costs more than it did in July. This app turns those receipts into data I can ask questions about. I use it with my own receipts, from 3–4 stores at about 20 lines per receipt.

## Requirements

- Python 3.8 or newer (developed on Python 3.14)
- No third-party packages; it uses only the standard library

## Getting started

```bash
git clone https://github.com/adybreijo/expense_tracker.git
cd expense_tracker
python3 main.py
```

On the first run there is no data file. That's expected: the app starts empty and creates `expenses.json` next to the code the first time you save something.

### Try it with sample data

The repo includes `sample_expenses.json`: four fake receipts from August and September 2026, from three stores. To start with it, copy it to the file the app reads:

```bash
cp sample_expenses.json expenses.json
python3 main.py
```

Things to try:
- **2 → 2** (Purchase for period) with `01-08-2026` to `30-09-2026` lists every receipt, or narrow it to one month.
- **2 → 1 → 2** (Delete a product) on the August 2 receipt. It has two identical `milk` lines, and only the one you pick is removed.
- **1 → 1** (Add complete receipt): known stores and products are offered in a list instead of being typed again.

To go back to an empty tracker, delete `expenses.json`.

## Example session

Listing the receipts from the first ten days of September, with the sample data:

```Menu:
1. Add (Enter new receipts, modify information...)
2. Log (View or delete your receipts)
3. Expenses (Show your expenses)
4. Quit
>>: 2

Menu:
1. Delete
2. Purchase for period
3. Go back to main menu
Chose an option from menu: 2

--Purchase for period--
Your receipts go to 2026-08-02 - 2026-09-20
Enter the first date: 01-09-2026
Enter the second date: 10-09-2026

In this period you have 1 receipts
Receipt # 1:
    Store: Soriana
    Date: 2026-09-06
    Total paid: $361.60
    Notes:
    # 1 - Product: Chicken
        Category: Meat
        Unit_price: $129.00
        Paid: $103.20
    # 2 - Product: Coffee
        Category: Drinks
        Unit_price: $145.00
        Paid: $145.00
    # 3 - Product: Rice
        Category: Grains
        Unit_price: $33.50
        Paid: $33.50
    # 4 - Product: Shampoo
        Category: Personal care
        Unit_price: $79.90
        Paid: $79.90

```

## Usage

### 1. Add
- **Add complete receipt**: asks once for the fields shared by the whole receipt (date, store, total paid, notes), then asks for each product (name, category, unit price, amount paid). You can correct any field before the receipt is saved.
- **Add products to a receipt**: appends more product lines to a receipt you already saved.

For stores, categories and products the app already knows, it offers them in a numbered list so you don't have to type them again. A new product gets suggestions from the existing categories. If you give a known product a different category, the app asks whether to change it in every receipt, so a product never ends up split across two categories.

### 2. Log
- **Delete**: removes a whole receipt or a single product line. Every line has its own id, so you delete exactly the one you picked, even if an identical line sits next to it. You're asked to confirm before anything is deleted.
- **Purchase for period**: shows every receipt between two dates.

### 3. Expenses
Totals by period, store, product and category. *This section is still in progress.*

### Input rules
- **Dates** are typed as `DD-MM-YYYY`. Impossible dates (`45-13-2026`) and future dates are rejected.
- **Names** are stored in lowercase, so `Chicken`, `chicken` and `CHICKEN` count as the same product.
- **Invalid input** (letters where a number is expected, a blank required field, negative numbers) is asked for again, with a message saying what was wrong.
- **Cancel**: type `q`, `quit` or `cancel` at any prompt to abandon the current operation. `Ctrl-C` exits the program cleanly.

## Data storage

Everything lives in a single file, `expenses.json`. It's rewritten after every operation, so if the program stops halfway, what you already saved is safe. Writes go to a temp file first and then replace the original, so the file is never left half-written.

`expenses.json` is in `.gitignore` because it holds personal data. Use `sample_expenses.json` as a reference for the format:

```json
{
  "receipts": [
    {
      "receipt_id": 1,
      "date": "2026-08-02",
      "store": "walmart",
      "total_paid": 278.55,
      "notes": "weekly shopping",
      "products": [
        {
          "product_id": 1,
          "product": "chicken",
          "category": "meat",
          "unit_price": 119.0,
          "paid_product": 95.2
        }
      ]
    }
  ],
  "catalog": { "chicken": "meat" },
  "next_receipt_id": 2
}
```


- Dates are stored as `YYYY-MM-DD`, so sorting them alphabetically also sorts them by date.
- `receipt_id` is unique across all receipts. `product_id` is unique only within its own receipt.
- `catalog` remembers each product's category so it can be suggested next time.
- `next_receipt_id` makes sure a deleted receipt's id is never reused.

If `expenses.json` contains invalid JSON, it's moved to `expenses.json.bak` and the app starts empty, so your original data is never overwritten. If the file is valid JSON but doesn't have the expected structure, the app stops without changing anything.

## Project structure

```
main.py               Main menu loop
cli.py                User input: validated numbers, strings, dates, lists, cancel handling
dates.py              Date parsing and validation
storage.py            Load/save of expenses.json
sample_expenses.json  Fake data for trying the app
tracker/
  purchases.py        Adding receipts and products
  log_info.py         Viewing and deleting receipts
  queries.py          Pure data helpers: filters, ids, categories, periods
  expenses.py         Expense summaries (in progress)
```

The modules follow one rule: `cli.py` talks to the user and knows nothing about receipts, `queries.py` works on receipts with no input or output (data in, data out), and the `tracker` feature modules connect the two.

## Status

Working: adding, correcting, listing and deleting receipts and products, with data that survives crashes and bad files.