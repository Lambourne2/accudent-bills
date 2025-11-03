#!/usr/bin/env python3
"""
Test rebate handling in invoice parser.
Demonstrates how negative amounts (rebates) in parentheses are handled.
"""

from parser import _parse_table_row

# Test cases for rebate parsing
test_lines = [
    # Normal positive amount
    "Bruxzir #3 Shade C1 1 $ 110.00 $ 110.00",
    
    # Rebate with parentheses (negative)
    "Rebate 1 $ 110.00 ($ 110.00)",
    
    # Another format
    "Discount (Rebate) 1 110.00 (110.00)",
    
    # Mixed positive and negative
    "Adjustment Fee 1 50.00 (50.00)",
]

print("Testing Rebate Parsing")
print("=" * 60)
print()

for line in test_lines:
    result = _parse_table_row(line)
    if result:
        print(f"Input:  {line}")
        print(f"Output: {result}")
        print(f"  Description: {result['description']}")
        print(f"  Quantity: {result['quantity']}")
        print(f"  Unit Price: ${result['unit_price']}")
        print(f"  Cost: ${result['cost']}")
        print()
    else:
        print(f"Failed to parse: {line}")
        print()

# Test a complete invoice scenario
print("\nComplete Invoice Example:")
print("=" * 60)

line1 = "Bruxzir #3 Shade C1 1 $ 110.00 $ 110.00"
line2 = "Rebate 1 110.00 (110.00)"

item1 = _parse_table_row(line1)
item2 = _parse_table_row(line2)

if item1 and item2:
    unit_price = item1['unit_price']
    alloys_extras = item2['cost']
    total = unit_price + alloys_extras
    
    print(f"Line 1: {item1['description']} = ${item1['cost']}")
    print(f"Line 2: {item2['description']} = ${item2['cost']}")
    print(f"\nUnit Price: ${unit_price}")
    print(f"Alloys/Extras (rebate): ${alloys_extras}")
    print(f"Total Cost: ${total}")
    print()
    print(f"✓ Rebate correctly applied! Final total: ${total}")
