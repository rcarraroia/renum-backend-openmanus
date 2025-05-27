"""
Unit tests for the data simulation module.

This module contains tests for the SalesDataGenerator and SalesDataStore classes.
"""

import os
import unittest
import tempfile
from datetime import datetime, timedelta

from app.tool.data_analysis.data_simulation import SalesDataGenerator, SalesDataStore, generate_sample_data


class TestSalesDataGenerator(unittest.TestCase):
    """Tests for the SalesDataGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = SalesDataGenerator()
    
    def test_generate_sales_data(self):
        """Test generating sales data."""
        # Generate data with default parameters
        data = self.generator.generate_sales_data()
        
        # Check that the correct number of records was generated
        self.assertEqual(len(data), 1000)
        
        # Check that each record has the expected fields
        expected_fields = [
            "transaction_id", "date", "customer_id", "category", "product",
            "quantity", "unit_price", "total_amount", "discount_percent",
            "discount_amount", "final_amount", "region", "channel", "payment_method"
        ]
        
        for record in data[:5]:  # Check first 5 records
            for field in expected_fields:
                self.assertIn(field, record)
        
        # Test with custom parameters
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        data = self.generator.generate_sales_data(
            num_records=100,
            start_date=start_date,
            end_date=end_date
        )
        
        # Check that the correct number of records was generated
        self.assertEqual(len(data), 100)
        
        # Check that dates are within the specified range
        for record in data:
            record_date = datetime.strptime(record["date"], "%Y-%m-%d")
            self.assertTrue(start_date <= record_date <= end_date)
    
    def test_save_to_csv(self):
        """Test saving data to CSV."""
        # Generate sample data
        data = self.generator.generate_sales_data(num_records=10)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Save data to CSV
            self.generator.save_to_csv(data, temp_path)
            
            # Check that the file exists
            self.assertTrue(os.path.exists(temp_path))
            
            # Check that the file has content
            self.assertGreater(os.path.getsize(temp_path), 0)
            
            # Check that the file is a valid CSV
            import csv
            with open(temp_path, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)
                
                # Check header row
                self.assertEqual(len(rows[0]), len(data[0].keys()))
                
                # Check data rows
                self.assertEqual(len(rows) - 1, len(data))  # -1 for header row
        
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_save_to_json(self):
        """Test saving data to JSON."""
        # Generate sample data
        data = self.generator.generate_sales_data(num_records=10)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Save data to JSON
            self.generator.save_to_json(data, temp_path)
            
            # Check that the file exists
            self.assertTrue(os.path.exists(temp_path))
            
            # Check that the file has content
            self.assertGreater(os.path.getsize(temp_path), 0)
            
            # Check that the file is valid JSON
            import json
            with open(temp_path, 'r') as jsonfile:
                loaded_data = json.load(jsonfile)
                
                # Check that the loaded data matches the original data
                self.assertEqual(len(loaded_data), len(data))
                self.assertEqual(loaded_data[0].keys(), data[0].keys())
        
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestSalesDataStore(unittest.TestCase):
    """Tests for the SalesDataStore class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Generate sample data
        self.generator = SalesDataGenerator()
        self.data = self.generator.generate_sales_data(num_records=100)
        
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
            self.csv_path = temp_file.name
        
        # Create a temporary JSON file
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            self.json_path = temp_file.name
        
        # Save data to both formats
        self.generator.save_to_csv(self.data, self.csv_path)
        self.generator.save_to_json(self.data, self.json_path)
        
        # Create data stores
        self.csv_store = SalesDataStore(self.csv_path)
        self.json_store = SalesDataStore(self.json_path)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary files
        for path in [self.csv_path, self.json_path]:
            if os.path.exists(path):
                os.remove(path)
    
    def test_load_data(self):
        """Test loading data from files."""
        # Check that data was loaded correctly from CSV
        self.assertEqual(len(self.csv_store.data), 100)
        
        # Check that data was loaded correctly from JSON
        self.assertEqual(len(self.json_store.data), 100)
        
        # Check that numeric fields were converted correctly
        numeric_fields = [
            "quantity", "unit_price", "total_amount", 
            "discount_percent", "discount_amount", "final_amount"
        ]
        
        for field in numeric_fields:
            self.assertIsInstance(self.csv_store.data[0][field], float)
            self.assertIsInstance(self.json_store.data[0][field], float)
    
    def test_get_total_sales(self):
        """Test getting total sales."""
        # Calculate expected total
        expected_total = sum(record["final_amount"] for record in self.data)
        
        # Check total sales from CSV store
        csv_total = self.csv_store.get_total_sales()
        self.assertAlmostEqual(csv_total, expected_total, places=2)
        
        # Check total sales from JSON store
        json_total = self.json_store.get_total_sales()
        self.assertAlmostEqual(json_total, expected_total, places=2)
    
    def test_get_sales_by_category(self):
        """Test getting sales by category."""
        # Calculate expected totals by category
        expected_by_category = {}
        for record in self.data:
            category = record["category"]
            amount = record["final_amount"]
            
            if category not in expected_by_category:
                expected_by_category[category] = 0
            
            expected_by_category[category] += amount
        
        # Round values
        for category in expected_by_category:
            expected_by_category[category] = round(expected_by_category[category], 2)
        
        # Check sales by category from CSV store
        csv_by_category = self.csv_store.get_sales_by_category()
        
        for category, amount in expected_by_category.items():
            self.assertIn(category, csv_by_category)
            self.assertAlmostEqual(csv_by_category[category], amount, places=2)
        
        # Check sales by category from JSON store
        json_by_category = self.json_store.get_sales_by_category()
        
        for category, amount in expected_by_category.items():
            self.assertIn(category, json_by_category)
            self.assertAlmostEqual(json_by_category[category], amount, places=2)
    
    def test_filter_by_period(self):
        """Test filtering by time period."""
        # Test filtering by last 7 days
        last_7_days = self.csv_store._filter_by_period("last_7_days")
        
        # Check that all dates are within the last 7 days
        today = datetime.now()
        seven_days_ago = today - timedelta(days=7)
        
        for record in last_7_days:
            record_date = datetime.strptime(record["date"], "%Y-%m-%d")
            self.assertTrue(record_date >= seven_days_ago)
            self.assertTrue(record_date <= today)
    
    def test_filter_transactions_by_category(self):
        """Test filtering transactions by category."""
        # Choose a category from the data
        category = self.data[0]["category"]
        
        # Filter transactions
        filtered = self.csv_store.filter_transactions_by_category(category)
        
        # Check that all records have the correct category
        for record in filtered:
            self.assertEqual(record["category"], category)
    
    def test_filter_transactions_by_date_range(self):
        """Test filtering transactions by date range."""
        # Define a date range
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        
        # Filter transactions
        filtered = self.csv_store.filter_transactions_by_date_range(start_date, end_date)
        
        # Check that all records are within the date range
        for record in filtered:
            self.assertTrue(start_date <= record["date"] <= end_date)
    
    def test_get_sales_summary(self):
        """Test getting sales summary."""
        # Get summary
        summary = self.csv_store.get_sales_summary()
        
        # Check that the summary contains expected fields
        expected_fields = [
            "total_sales", "total_transactions", "average_transaction",
            "top_categories", "top_products", "sales_by_channel"
        ]
        
        for field in expected_fields:
            self.assertIn(field, summary)
        
        # Check that the total sales matches
        expected_total = sum(record["final_amount"] for record in self.data)
        self.assertAlmostEqual(summary["total_sales"], expected_total, places=2)
        
        # Check that the total transactions matches
        self.assertEqual(summary["total_transactions"], len(self.data))


class TestGenerateSampleData(unittest.TestCase):
    """Tests for the generate_sample_data function."""
    
    def test_generate_sample_data_csv(self):
        """Test generating sample data in CSV format."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Generate sample data
            generate_sample_data(temp_path, format="csv", num_records=50)
            
            # Check that the file exists
            self.assertTrue(os.path.exists(temp_path))
            
            # Check that the file has content
            self.assertGreater(os.path.getsize(temp_path), 0)
            
            # Try loading the data
            data_store = SalesDataStore(temp_path)
            
            # Check that the correct number of records was loaded
            self.assertEqual(len(data_store.data), 50)
        
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_generate_sample_data_json(self):
        """Test generating sample data in JSON format."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Generate sample data
            generate_sample_data(temp_path, format="json", num_records=50)
            
            # Check that the file exists
            self.assertTrue(os.path.exists(temp_path))
            
            # Check that the file has content
            self.assertGreater(os.path.getsize(temp_path), 0)
            
            # Try loading the data
            data_store = SalesDataStore(temp_path)
            
            # Check that the correct number of records was loaded
            self.assertEqual(len(data_store.data), 50)
        
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_generate_sample_data_invalid_format(self):
        """Test generating sample data with an invalid format."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Try to generate sample data with an invalid format
            with self.assertRaises(ValueError):
                generate_sample_data(temp_path, format="txt", num_records=50)
        
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
