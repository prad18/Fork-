"""
Comprehensive health check script for FastAPI backend
Tests server responsiveness, endpoints, and database connectivity
"""

import requests
import time
import json
import sys
import os
from datetime import datetime

def log_result(message, success=True):
    """Log results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "✓" if success else "✗"
    print(f"[{timestamp}] {status} {message}")

def test_server_health():
    """Test basic server connectivity"""
    base_url = "http://127.0.0.1:8000"
    
    print("="*60)
    print("FASTAPI SERVER HEALTH CHECK")
    print("="*60)
    
    # Test basic connectivity
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        log_result(f"Server responding at {base_url} - Status: {response.status_code}")
        if response.status_code == 200:
            log_result("Server is healthy")
        else:
            log_result(f"Server returned non-200 status: {response.status_code}", False)
    except requests.exceptions.ConnectionError:
        log_result("Server is not responding - Connection refused", False)
        return False
    except requests.exceptions.Timeout:
        log_result("Server response timeout", False)
        return False
    except Exception as e:
        log_result(f"Server connectivity error: {str(e)}", False)
        return False
    
    return True

def test_api_endpoints():
    """Test specific API endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    print("\n" + "="*60)
    print("API ENDPOINTS TEST")
    print("="*60)
    
    # Test OpenAPI docs
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        log_result(f"OpenAPI docs (/docs) - Status: {response.status_code}")
    except Exception as e:
        log_result(f"OpenAPI docs error: {str(e)}", False)
    
    # Test API schema
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        log_result(f"OpenAPI schema - Status: {response.status_code}")
    except Exception as e:
        log_result(f"OpenAPI schema error: {str(e)}", False)
    
    # Test invoice endpoint (GET)
    try:
        response = requests.get(f"{base_url}/api/invoices", timeout=5)
        log_result(f"Invoice endpoint (GET) - Status: {response.status_code}")
    except Exception as e:
        log_result(f"Invoice endpoint error: {str(e)}", False)
    
    # Test health endpoint if it exists
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        log_result(f"Health endpoint - Status: {response.status_code}")
    except Exception as e:
        log_result(f"Health endpoint not available or error: {str(e)}", False)

def test_database_connectivity():
    """Test database connectivity"""
    print("\n" + "="*60)
    print("DATABASE CONNECTIVITY TEST")
    print("="*60)
    
    # Check if database file exists
    db_path = "forkplus.db"
    if os.path.exists(db_path):
        log_result(f"Database file exists: {db_path}")
        
        # Check file size
        size = os.path.getsize(db_path)
        log_result(f"Database file size: {size} bytes")
        
        if size > 0:
            log_result("Database file is not empty")
        else:
            log_result("Database file is empty - may need initialization", False)
    else:
        log_result(f"Database file not found: {db_path}", False)

def test_file_upload():
    """Test file upload endpoint"""
    print("\n" + "="*60)
    print("FILE UPLOAD TEST")
    print("="*60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Check if uploads directory exists
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        log_result(f"Uploads directory exists: {uploads_dir}")
        
        # Count files in uploads
        files = os.listdir(uploads_dir)
        log_result(f"Files in uploads directory: {len(files)}")
        
        if files:
            log_result(f"Sample files: {files[:3]}")
    else:
        log_result(f"Uploads directory not found: {uploads_dir}", False)
    
    # Test upload endpoint availability
    try:
        # Create a dummy file for testing
        dummy_data = b"dummy file content"
        files = {'file': ('test.txt', dummy_data, 'text/plain')}
        
        response = requests.post(f"{base_url}/api/invoices/upload", files=files, timeout=10)
        log_result(f"Upload endpoint test - Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            log_result("Upload endpoint is working")
        elif response.status_code == 422:
            log_result("Upload endpoint validation error (expected for dummy file)")
        else:
            log_result(f"Upload endpoint returned: {response.status_code}", False)
            
    except Exception as e:
        log_result(f"Upload endpoint error: {str(e)}", False)

def check_server_logs():
    """Check server logs for errors"""
    print("\n" + "="*60)
    print("SERVER LOGS CHECK")
    print("="*60)
    
    log_file = "backend/backend.log"
    if os.path.exists(log_file):
        log_result(f"Log file exists: {log_file}")
        
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                
            log_result(f"Total log lines: {len(lines)}")
            
            # Check for errors in last 50 lines
            recent_lines = lines[-50:] if len(lines) > 50 else lines
            errors = [line for line in recent_lines if 'ERROR' in line.upper() or 'EXCEPTION' in line.upper()]
            
            if errors:
                log_result(f"Recent errors found: {len(errors)}", False)
                for error in errors[-5:]:  # Show last 5 errors
                    print(f"    {error.strip()}")
            else:
                log_result("No recent errors in logs")
                
        except Exception as e:
            log_result(f"Error reading log file: {str(e)}", False)
    else:
        log_result(f"Log file not found: {log_file}", False)

def main():
    """Run all health checks"""
    print("Starting comprehensive health check...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    server_healthy = test_server_health()
    
    if server_healthy:
        test_api_endpoints()
        test_file_upload()
    else:
        print("\n⚠️  Server is not responding. Skipping endpoint tests.")
    
    test_database_connectivity()
    check_server_logs()
    
    print("\n" + "="*60)
    print("HEALTH CHECK COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
