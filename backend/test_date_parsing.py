"""
Test the fixed date parsing functionality
"""
from datetime import datetime

def test_date_parsing():
    """Test date parsing with the specific format that was failing"""
    
    # Test dates that were causing issues
    test_dates = [
        "June 28, 2025",  # The specific one that failed
        "May 25, 2022",   # Previous failure
        "2022-05-25",     # ISO format
        "05/25/2022",     # US format
        "25/05/2022"      # EU format
    ]
    
    date_formats = [
        "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", 
        "%B %d, %Y", "%b %d, %Y",
        "%d %B %Y", "%d %b %Y",
        "%m-%d-%Y", "%d-%m-%Y"
    ]
    
    print("Testing date parsing functionality:")
    print("=" * 50)
    
    for date_str in test_dates:
        print(f"\nTesting: '{date_str}'")
        
        # Try ISO format first (like in the actual code)
        try:
            parsed_date = datetime.fromisoformat(date_str)
            print(f"  [SUCCESS] ISO format: {parsed_date}")
            continue
        except ValueError:
            pass
        
        # Try alternative formats
        parsed_date = None
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                print(f"  [SUCCESS] Format '{fmt}': {parsed_date}")
                break
            except ValueError:
                continue
        
        if not parsed_date:
            print(f"  [ERROR] Could not parse: {date_str}")
    
    print("\n" + "=" * 50)
    print("Date parsing test completed!")

if __name__ == "__main__":
    test_date_parsing()
