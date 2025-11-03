"""
Invoice parsing logic.
Extracts patient name, due date, line items, and computes totals.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from decimal import Decimal


def parse_invoice(text: str) -> Dict:
    """
    Parse invoice text and extract all required fields.
    
    Args:
        text: Extracted PDF text
        
    Returns:
        Dictionary with keys:
        - dentist_name: str
        - date_due: datetime object
        - patient_name: str
        - total_units: int
        - unit_price: Optional[Decimal] (single price or None if mixed)
        - alloys_extras_cost: Decimal
        - total_cost: Decimal
        
    Raises:
        ValueError: If required fields cannot be parsed
    """
    # Extract dentist name
    dentist_name = _parse_dentist_name(text)
    
    # Extract patient name and due date
    patient_name, date_due = _parse_patient_and_date(text)
    
    # Parse table and extract line items
    line_items = _parse_table(text)
    
    if not line_items:
        raise ValueError("No line items found in invoice")
    
    # Compute totals
    # Quantity is always 1
    total_units = 1
    
    # Unit price comes from first row only
    unit_price = line_items[0]['unit_price'] if line_items else Decimal('0')
    
    # Alloys/extras is sum of rows 2+ costs (if any)
    alloys_extras_cost = _compute_alloys_extras(line_items)
    
    # Calculate total cost: Unit Price + Alloys/Extras
    total_cost = unit_price + alloys_extras_cost
    
    return {
        'dentist_name': dentist_name,
        'date_due': date_due,
        'patient_name': patient_name,
        'total_units': total_units,
        'unit_price': unit_price,
        'alloys_extras_cost': alloys_extras_cost,
        'total_cost': total_cost,
    }


def _parse_patient_and_date(text: str) -> Tuple[str, datetime]:
    """
    Parse patient name and due date from invoice footer.
    
    Expected pattern: Patient: {Name}, Due {m/d/yyyy}
    
    Args:
        text: Invoice text
        
    Returns:
        Tuple of (patient_name, date_due)
        
    Raises:
        ValueError: If pattern not found
    """
    # Regex: Patient: {name}, Due {date}
    pattern = r'Patient:\s*(?P<name>.+?),\s*Due\s*(?P<date>\d{1,2}/\d{1,2}/\d{4})'
    match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
    
    if not match:
        raise ValueError("Could not find 'Patient: ..., Due ...' pattern in invoice")
    
    patient_name = match.group('name').strip()
    date_str = match.group('date')
    
    # Parse date
    try:
        date_due = datetime.strptime(date_str, '%m/%d/%Y')
    except ValueError:
        raise ValueError(f"Could not parse date: {date_str}")
    
    return patient_name, date_due


def _parse_dentist_name(text: str) -> str:
    """
    Parse dentist name from invoice header.
    
    Expected pattern: INVOICE FOR: {Dentist Name}
    
    Args:
        text: Full invoice text
        
    Returns:
        Dentist name
        
    Raises:
        ValueError: If pattern not found
    """
    # Pattern to match "INVOICE FOR:" with flexible spacing, then capture name until DESCRIPTION
    # The text has spaces between letters, so we need to be flexible
    pattern = r'I\s*N\s*V\s*O\s*I\s*C\s*E\s+F\s*O\s*R\s*:\s*(?P<name>.+?)(?=\s*D\s*E\s*S\s*C\s*R\s*I\s*P\s*T\s*I\s*O\s*N)'
    
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        raise ValueError("Could not find dentist name after 'INVOICE FOR:'")
    
    dentist_name = match.group('name').strip()
    
    # PDF extraction adds spaces between characters (e.g., "D R . B RY C E A L L D R E D G E")
    # Strategy: Remove all spaces, then intelligently re-add them
    
    # Step 1: Remove all whitespace
    no_spaces = dentist_name.replace(' ', '')
    
    # Step 2: Add space after periods (periods indicate abbreviations like "DR.")
    with_period_spaces = re.sub(r'\.', '. ', no_spaces)
    
    # Step 3: Add spaces before uppercase letters that follow lowercase (word boundaries)
    # Example: "SmithJohn" -> "Smith John"
    with_word_breaks = re.sub(r'([a-z])([A-Z])', r'\1 \2', with_period_spaces)
    
    # Step 4: If we have very long sequences of capitals (like "ALLDREDGE"), 
    # try to break them into reasonable words by checking for common patterns
    # For now, keep them together as they likely form a last name
    
    # Clean up any double spaces
    final = re.sub(r'\s+', ' ', with_word_breaks).strip()
    
    return final


def _parse_table(text: str) -> List[Dict]:
    """
    Parse the invoice table and extract line items.
    
    Table format:
    DESCRIPTION | QUANTITY | UNIT PRICE | COST
    
    Args:
        text: Invoice text
        
    Returns:
        List of dicts with keys: description, quantity, unit_price, cost
    """
    lines = text.split('\n')
    line_items = []
    
    # Find header row (handle spaced letters like "D E S C R I P T I O N")
    header_idx = None
    for i, line in enumerate(lines):
        # Remove spaces to handle spaced-out headers
        line_clean = re.sub(r'\s+', '', line.upper())
        if all(keyword.replace(' ', '') in line_clean for keyword in ['DESCRIPTION', 'QUANTITY', 'UNITPRICE', 'COST']):
            header_idx = i
            break
    
    if header_idx is None:
        return []
    
    # Parse rows after header until we hit subtotal/blank/total
    for i in range(header_idx + 1, len(lines)):
        line = lines[i].strip()
        
        # Stop at subtotal, total, or empty line
        if not line or re.search(r'\b(subtotal|total|sub-total)\b', line, re.IGNORECASE):
            break
        
        # Try to parse this line as a table row
        item = _parse_table_row(line)
        if item:
            line_items.append(item)
    
    return line_items


def _parse_table_row(line: str) -> Optional[Dict]:
    """
    Parse a single table row.
    
    Expected format: Description text | Quantity | Unit Price | Cost
    Numbers may have $ and commas.
    
    Args:
        line: Single line from table
        
    Returns:
        Dict with description, quantity, unit_price, cost or None if not parseable
    """
    # Try to find numbers in the line
    # Pattern: look for quantity (integer), unit price ($x.xx), cost ($x.xx)
    
    # Extract all money amounts from the line
    money_pattern = r'\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
    numbers = re.findall(money_pattern, line)
    
    if len(numbers) < 3:
        # Not enough numbers for quantity, unit_price, cost
        return None
    
    try:
        # Typically: description ... quantity unit_price cost
        # Take last 3 numbers as quantity, unit_price, cost
        quantity_str = numbers[-3].replace(',', '')
        unit_price_str = numbers[-2].replace(',', '')
        cost_str = numbers[-1].replace(',', '')
        
        quantity = int(float(quantity_str))
        unit_price = Decimal(unit_price_str)
        cost = Decimal(cost_str)
        
        # Extract description (everything before the numbers)
        # Find position of first number
        first_num_pos = line.find(numbers[-3])
        description = line[:first_num_pos].strip()
        
        # Remove leading separators like | or tabs
        description = re.sub(r'^[\|\t\s]+', '', description)
        
        return {
            'description': description,
            'quantity': quantity,
            'unit_price': unit_price,
            'cost': cost,
        }
    
    except (ValueError, IndexError):
        return None


def _compute_unit_price(line_items: List[Dict]) -> Optional[Decimal]:
    """
    Compute unit price.
    
    If all items have same unit price, return that.
    If multiple different prices, return None.
    
    Args:
        line_items: List of parsed line items
        
    Returns:
        Single unit price or None
    """
    unit_prices = set(item['unit_price'] for item in line_items)
    
    if len(unit_prices) == 1:
        return list(unit_prices)[0]
    else:
        return None


def _compute_alloys_extras(line_items: List[Dict]) -> Decimal:
    """
    Compute sum of alloys/extras costs.
    
    Sums the Cost column from rows 2+ only (skips first row).
    First row's Cost is not included - only its Unit Price is used.
    
    Args:
        line_items: List of parsed line items
        
    Returns:
        Sum of costs from rows 2 onwards (0 if only 1 row)
    """
    # Sum costs from rows 2+ only (index 1 onwards)
    total = Decimal('0')
    for item in line_items[1:]:  # Skip first row
        total += item['cost']
    
    return total


def _calculate_total_cost(total_units: int, unit_price: Optional[Decimal], 
                          alloys_extras_cost: Decimal) -> Decimal:
    """
    Calculate total cost using the formula:
    Total Cost = Quantity × (Unit Price + Alloys/Extras Cost)
    
    If unit_price is None (mixed prices), use 0.
    
    Args:
        total_units: Total quantity from all line items
        unit_price: Single unit price or None if mixed
        alloys_extras_cost: Sum of all alloys/extras costs
        
    Returns:
        Calculated total cost
    """
    # Use unit price if available, otherwise 0
    price = unit_price if unit_price is not None else Decimal('0')
    
    # Formula: Quantity × (Unit Price + Alloys/Extras)
    total_cost = Decimal(total_units) * (price + alloys_extras_cost)
    
    return total_cost


def format_date_display(date_obj: datetime) -> str:
    """Format date as m/d/yyyy for display."""
    return date_obj.strftime('%-m/%-d/%Y')


def format_date_iso(date_obj: datetime) -> str:
    """Format date as YYYY-MM-DD for sorting/storage."""
    return date_obj.strftime('%Y-%m-%d')
