"""
Data simulation module for the Data Analysis agent.

This module provides functionality to generate and manage simulated sales/financial data
for demonstration purposes.
"""

import csv
import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union


class SalesDataGenerator:
    """
    Generator for simulated sales/financial data.
    
    This class creates realistic-looking sales data for demonstration purposes,
    including products, categories, sales amounts, dates, and growth metrics.
    """
    
    def __init__(self):
        """Initialize the SalesDataGenerator."""
        # Product categories
        self.categories = [
            "Electronics", "Clothing", "Home & Kitchen", "Books",
            "Sports & Outdoors", "Beauty", "Toys", "Grocery",
            "Health", "Automotive"
        ]
        
        # Products by category
        self.products = {
            "Electronics": [
                "Smartphone", "Laptop", "Tablet", "Headphones", 
                "Smart Watch", "Camera", "TV", "Speaker"
            ],
            "Clothing": [
                "T-Shirt", "Jeans", "Dress", "Jacket", 
                "Sweater", "Shoes", "Socks", "Hat"
            ],
            "Home & Kitchen": [
                "Blender", "Coffee Maker", "Toaster", "Microwave", 
                "Vacuum Cleaner", "Bed Sheets", "Towels", "Cookware Set"
            ],
            "Books": [
                "Fiction Novel", "Biography", "Cookbook", "Self-Help", 
                "Business", "Science", "History", "Children's Book"
            ],
            "Sports & Outdoors": [
                "Running Shoes", "Yoga Mat", "Bicycle", "Tennis Racket", 
                "Basketball", "Camping Tent", "Fishing Rod", "Golf Clubs"
            ],
            "Beauty": [
                "Shampoo", "Conditioner", "Face Cream", "Makeup Kit", 
                "Perfume", "Nail Polish", "Hair Dryer", "Razor"
            ],
            "Toys": [
                "Action Figure", "Board Game", "Puzzle", "Doll", 
                "Building Blocks", "Remote Control Car", "Stuffed Animal", "Art Set"
            ],
            "Grocery": [
                "Coffee", "Cereal", "Pasta", "Snacks", 
                "Soda", "Juice", "Bread", "Canned Goods"
            ],
            "Health": [
                "Vitamins", "Pain Reliever", "First Aid Kit", "Fitness Tracker", 
                "Thermometer", "Humidifier", "Massage Device", "Supplements"
            ],
            "Automotive": [
                "Car Wax", "Motor Oil", "Air Freshener", "Tire Inflator", 
                "Car Cover", "Jump Starter", "Dash Cam", "Floor Mats"
            ]
        }
        
        # Regions
        self.regions = ["North", "South", "East", "West", "Central"]
        
        # Sales channels
        self.channels = ["Online", "Retail", "Wholesale", "Direct"]
        
        # Payment methods
        self.payment_methods = ["Credit Card", "Debit Card", "PayPal", "Cash", "Bank Transfer"]
    
    def generate_sales_data(
        self,
        num_records: int = 1000,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate simulated sales data.
        
        Args:
            num_records: Number of sales records to generate
            start_date: Start date for the sales data (defaults to 1 year ago)
            end_date: End date for the sales data (defaults to today)
            
        Returns:
            List of dictionaries containing sales data
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)
        
        if end_date is None:
            end_date = datetime.now()
        
        date_range = (end_date - start_date).days
        
        sales_data = []
        
        for _ in range(num_records):
            # Generate random date within range
            random_days = random.randint(0, date_range)
            sale_date = start_date + timedelta(days=random_days)
            
            # Select random category and product
            category = random.choice(self.categories)
            product = random.choice(self.products[category])
            
            # Generate other random attributes
            region = random.choice(self.regions)
            channel = random.choice(self.channels)
            payment_method = random.choice(self.payment_methods)
            
            # Generate quantities and prices
            quantity = random.randint(1, 10)
            unit_price = round(random.uniform(10.0, 500.0), 2)
            total_amount = round(quantity * unit_price, 2)
            
            # Calculate discount
            discount_percent = random.randint(0, 30)
            discount_amount = round((discount_percent / 100) * total_amount, 2)
            final_amount = round(total_amount - discount_amount, 2)
            
            # Generate customer ID
            customer_id = f"CUST-{random.randint(1000, 9999)}"
            
            # Generate transaction ID
            transaction_id = f"TXN-{random.randint(10000, 99999)}"
            
            # Create sales record
            sales_record = {
                "transaction_id": transaction_id,
                "date": sale_date.strftime("%Y-%m-%d"),
                "customer_id": customer_id,
                "category": category,
                "product": product,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_amount": total_amount,
                "discount_percent": discount_percent,
                "discount_amount": discount_amount,
                "final_amount": final_amount,
                "region": region,
                "channel": channel,
                "payment_method": payment_method
            }
            
            sales_data.append(sales_record)
        
        return sales_data
    
    def save_to_csv(self, data: List[Dict[str, Any]], file_path: str) -> None:
        """
        Save sales data to a CSV file.
        
        Args:
            data: List of dictionaries containing sales data
            file_path: Path to save the CSV file
        """
        if not data:
            return
        
        # Get field names from the first record
        fieldnames = data[0].keys()
        
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    def save_to_json(self, data: List[Dict[str, Any]], file_path: str) -> None:
        """
        Save sales data to a JSON file.
        
        Args:
            data: List of dictionaries containing sales data
            file_path: Path to save the JSON file
        """
        with open(file_path, 'w') as jsonfile:
            json.dump(data, jsonfile, indent=2)


class SalesDataStore:
    """
    Store for managing simulated sales data.
    
    This class provides methods for loading, querying, and analyzing sales data.
    """
    
    def __init__(self, data_path: str):
        """
        Initialize the SalesDataStore.
        
        Args:
            data_path: Path to the sales data file (CSV or JSON)
        """
        self.data_path = data_path
        self.data = []
        self._load_data()
    
    def _load_data(self) -> None:
        """
        Load sales data from the data file.
        
        Supports both CSV and JSON formats.
        """
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        
        file_ext = os.path.splitext(self.data_path)[1].lower()
        
        if file_ext == '.csv':
            self._load_from_csv()
        elif file_ext == '.json':
            self._load_from_json()
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _load_from_csv(self) -> None:
        """Load sales data from a CSV file."""
        with open(self.data_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            self.data = list(reader)
        
        # Convert numeric fields
        self._convert_numeric_fields()
    
    def _load_from_json(self) -> None:
        """Load sales data from a JSON file."""
        with open(self.data_path, 'r') as jsonfile:
            self.data = json.load(jsonfile)
        
        # Convert numeric fields
        self._convert_numeric_fields()
    
    def _convert_numeric_fields(self) -> None:
        """Convert string numeric fields to actual numeric types."""
        numeric_fields = [
            "quantity", "unit_price", "total_amount", 
            "discount_percent", "discount_amount", "final_amount"
        ]
        
        for record in self.data:
            for field in numeric_fields:
                if field in record and isinstance(record[field], str):
                    try:
                        record[field] = float(record[field])
                    except ValueError:
                        pass
    
    def get_total_sales(self, period: Optional[str] = None) -> float:
        """
        Get the total sales amount for a specified period.
        
        Args:
            period: Time period for filtering (e.g., "last_7_days", "last_30_days", 
                   "last_90_days", "last_year", or a specific YYYY-MM format)
            
        Returns:
            Total sales amount
        """
        filtered_data = self._filter_by_period(period)
        
        total = sum(record.get("final_amount", 0) for record in filtered_data)
        return round(total, 2)
    
    def get_sales_by_category(self, period: Optional[str] = None) -> Dict[str, float]:
        """
        Get sales amounts grouped by category.
        
        Args:
            period: Time period for filtering
            
        Returns:
            Dictionary mapping categories to sales amounts
        """
        filtered_data = self._filter_by_period(period)
        
        sales_by_category = {}
        for record in filtered_data:
            category = record.get("category")
            amount = record.get("final_amount", 0)
            
            if category:
                if category not in sales_by_category:
                    sales_by_category[category] = 0
                sales_by_category[category] += amount
        
        # Round values
        for category in sales_by_category:
            sales_by_category[category] = round(sales_by_category[category], 2)
        
        return sales_by_category
    
    def get_sales_by_product(self, category: Optional[str] = None, period: Optional[str] = None) -> Dict[str, float]:
        """
        Get sales amounts grouped by product.
        
        Args:
            category: Filter by product category
            period: Time period for filtering
            
        Returns:
            Dictionary mapping products to sales amounts
        """
        filtered_data = self._filter_by_period(period)
        
        if category:
            filtered_data = [record for record in filtered_data if record.get("category") == category]
        
        sales_by_product = {}
        for record in filtered_data:
            product = record.get("product")
            amount = record.get("final_amount", 0)
            
            if product:
                if product not in sales_by_product:
                    sales_by_product[product] = 0
                sales_by_product[product] += amount
        
        # Round values
        for product in sales_by_product:
            sales_by_product[product] = round(sales_by_product[product], 2)
        
        return sales_by_product
    
    def get_sales_by_region(self, period: Optional[str] = None) -> Dict[str, float]:
        """
        Get sales amounts grouped by region.
        
        Args:
            period: Time period for filtering
            
        Returns:
            Dictionary mapping regions to sales amounts
        """
        filtered_data = self._filter_by_period(period)
        
        sales_by_region = {}
        for record in filtered_data:
            region = record.get("region")
            amount = record.get("final_amount", 0)
            
            if region:
                if region not in sales_by_region:
                    sales_by_region[region] = 0
                sales_by_region[region] += amount
        
        # Round values
        for region in sales_by_region:
            sales_by_region[region] = round(sales_by_region[region], 2)
        
        return sales_by_region
    
    def get_sales_by_channel(self, period: Optional[str] = None) -> Dict[str, float]:
        """
        Get sales amounts grouped by channel.
        
        Args:
            period: Time period for filtering
            
        Returns:
            Dictionary mapping channels to sales amounts
        """
        filtered_data = self._filter_by_period(period)
        
        sales_by_channel = {}
        for record in filtered_data:
            channel = record.get("channel")
            amount = record.get("final_amount", 0)
            
            if channel:
                if channel not in sales_by_channel:
                    sales_by_channel[channel] = 0
                sales_by_channel[channel] += amount
        
        # Round values
        for channel in sales_by_channel:
            sales_by_channel[channel] = round(sales_by_channel[channel], 2)
        
        return sales_by_channel
    
    def get_product_with_highest_growth(self, compare_periods: str = "month_over_month") -> Dict[str, Any]:
        """
        Get the product with the highest sales growth.
        
        Args:
            compare_periods: How to compare periods ("month_over_month", "quarter_over_quarter", "year_over_year")
            
        Returns:
            Dictionary with product information and growth metrics
        """
        if compare_periods == "month_over_month":
            current_period = "last_30_days"
            previous_period = "previous_30_days"
        elif compare_periods == "quarter_over_quarter":
            current_period = "last_90_days"
            previous_period = "previous_90_days"
        elif compare_periods == "year_over_year":
            current_period = "last_year"
            previous_period = "previous_year"
        else:
            current_period = "last_30_days"
            previous_period = "previous_30_days"
        
        # Get sales by product for current period
        current_sales = self.get_sales_by_product(period=current_period)
        
        # Get sales by product for previous period
        previous_sales = self.get_sales_by_product(period=previous_period)
        
        # Calculate growth for each product
        growth_by_product = {}
        for product, current_amount in current_sales.items():
            previous_amount = previous_sales.get(product, 0)
            
            if previous_amount > 0:
                growth_percent = ((current_amount - previous_amount) / previous_amount) * 100
            else:
                growth_percent = 100  # If no previous sales, consider it 100% growth
            
            growth_by_product[product] = {
                "current_sales": current_amount,
                "previous_sales": previous_amount,
                "growth_amount": round(current_amount - previous_amount, 2),
                "growth_percent": round(growth_percent, 2)
            }
        
        # Find product with highest growth
        if not growth_by_product:
            return {"error": "No products found with sales data"}
        
        highest_growth_product = max(
            growth_by_product.items(),
            key=lambda x: x[1]["growth_percent"]
        )
        
        return {
            "product": highest_growth_product[0],
            "metrics": highest_growth_product[1],
            "comparison": compare_periods
        }
    
    def filter_transactions_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Filter transactions by category.
        
        Args:
            category: Product category to filter by
            
        Returns:
            List of transactions in the specified category
        """
        return [record for record in self.data if record.get("category") == category]
    
    def filter_transactions_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Filter transactions by date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of transactions within the specified date range
        """
        return [
            record for record in self.data 
            if start_date <= record.get("date", "") <= end_date
        ]
    
    def get_sales_summary(self, period: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a summary of sales metrics.
        
        Args:
            period: Time period for filtering
            
        Returns:
            Dictionary with sales summary metrics
        """
        filtered_data = self._filter_by_period(period)
        
        if not filtered_data:
            return {"error": "No data found for the specified period"}
        
        # Calculate metrics
        total_sales = sum(record.get("final_amount", 0) for record in filtered_data)
        total_transactions = len(filtered_data)
        average_transaction = total_sales / total_transactions if total_transactions > 0 else 0
        
        # Get top categories
        sales_by_category = self.get_sales_by_category(period)
        top_categories = sorted(
            sales_by_category.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Get top products
        sales_by_product = self.get_sales_by_product(period=period)
        top_products = sorted(
            sales_by_product.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Get sales by channel
        sales_by_channel = self.get_sales_by_channel(period)
        
        return {
            "total_sales": round(total_sales, 2),
            "total_transactions": total_transactions,
            "average_transaction": round(average_transaction, 2),
            "top_categories": [{"category": cat, "amount": amt} for cat, amt in top_categories],
            "top_products": [{"product": prod, "amount": amt} for prod, amt in top_products],
            "sales_by_channel": [{"channel": ch, "amount": amt} for ch, amt in sales_by_channel.items()]
        }
    
    def _filter_by_period(self, period: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Filter data by time period.
        
        Args:
            period: Time period for filtering
            
        Returns:
            Filtered list of records
        """
        if not period:
            return self.data
        
        today = datetime.now()
        
        if period == "last_7_days":
            start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
        elif period == "last_30_days":
            start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
        elif period == "previous_30_days":
            start_date = (today - timedelta(days=60)).strftime("%Y-%m-%d")
            end_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        elif period == "last_90_days":
            start_date = (today - timedelta(days=90)).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
        elif period == "previous_90_days":
            start_date = (today - timedelta(days=180)).strftime("%Y-%m-%d")
            end_date = (today - timedelta(days=90)).strftime("%Y-%m-%d")
        elif period == "last_year":
            start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
        elif period == "previous_year":
            start_date = (today - timedelta(days=730)).strftime("%Y-%m-%d")
            end_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
        elif "-" in period:  # Assume YYYY-MM format
            try:
                year, month = map(int, period.split("-"))
                start_date = f"{year}-{month:02d}-01"
                
                # Calculate end date (last day of the month)
                if month == 12:
                    end_date = f"{year+1}-01-01"
                else:
                    end_date = f"{year}-{month+1:02d}-01"
                
                # Adjust end date to be the last day of the month
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=1)
                end_date = end_date_obj.strftime("%Y-%m-%d")
            except ValueError:
                # Invalid format, return all data
                return self.data
        else:
            # Unknown period, return all data
            return self.data
        
        return self.filter_transactions_by_date_range(start_date, end_date)


def generate_sample_data(output_path: str, format: str = "csv", num_records: int = 1000) -> None:
    """
    Generate sample sales data and save to a file.
    
    Args:
        output_path: Path to save the output file
        format: Output format ("csv" or "json")
        num_records: Number of records to generate
    """
    generator = SalesDataGenerator()
    data = generator.generate_sales_data(num_records=num_records)
    
    if format.lower() == "csv":
        generator.save_to_csv(data, output_path)
    elif format.lower() == "json":
        generator.save_to_json(data, output_path)
    else:
        raise ValueError(f"Unsupported format: {format}")


if __name__ == "__main__":
    # Example usage
    output_file = "sample_sales_data.csv"
    generate_sample_data(output_file, format="csv", num_records=1000)
    print(f"Generated sample data: {output_file}")
    
    # Load and analyze the data
    data_store = SalesDataStore(output_file)
    summary = data_store.get_sales_summary()
    print(f"Total sales: ${summary['total_sales']}")
    print(f"Total transactions: {summary['total_transactions']}")
    print(f"Average transaction: ${summary['average_transaction']}")
    
    # Get product with highest growth
    growth = data_store.get_product_with_highest_growth()
    print(f"Product with highest growth: {growth['product']}")
    print(f"Growth percentage: {growth['metrics']['growth_percent']}%")
