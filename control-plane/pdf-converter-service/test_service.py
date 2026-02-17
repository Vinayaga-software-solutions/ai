"""
Test script for the PDF Converter Service
Tests the service locally or remotely
"""

import json
import base64
import requests
import argparse
import sys


def create_test_message(pdf_path: str = "test.pdf", file_id: int = 1) -> dict:
    """Create a test Pub/Sub message."""
    message_data = {
        "event_type": "data_file_uploaded",
        "occurred_at": "2026-02-17T13:50:49+00:00",
        "data_file": {
            "id": file_id,
            "data_id": 7,
            "original_name": "test_document.pdf",
            "storage_path": pdf_path,
            "mime_type": "application/pdf",
            "size": 105000,
            "created_at": "2026-02-17T13:50:49+00:00"
        },
        "data": {
            "id": 7,
            "name": "TestData",
            "type": "document",
            "storage_path": "tensrgrid/documents/test",
            "data_collection_id": 2,
            "created_by": 1
        },
        "data_collection": {
            "id": 2,
            "name": "TEST_COLLECTION",
            "project_id": 16
        },
        "project": {
            "id": 16,
            "name": "Test Project"
        },
        "storage": {
            "disk": "gcs",
            "bucket": "tensrgrid-raw-data",
            "gcs_uri": f"gs://tensrgrid-raw-data/{pdf_path}"
        }
    }
    
    return message_data


def create_pubsub_envelope(message_data: dict) -> dict:
    """Create a Pub/Sub push envelope."""
    message_json = json.dumps(message_data)
    message_b64 = base64.b64encode(message_json.encode('utf-8')).decode('utf-8')
    
    return {
        "message": {
            "data": message_b64,
            "attributes": {
                "event_type": "data_file_uploaded",
                "data_id": str(message_data["data_file"]["data_id"]),
                "data_file_id": str(message_data["data_file"]["id"])
            },
            "messageId": "test-message-id",
            "publishTime": "2026-02-17T13:50:49.000Z"
        },
        "subscription": "projects/test-project/subscriptions/test-subscription"
    }


def test_service(url: str, pdf_path: str, file_id: int):
    """Test the PDF converter service."""
    print(f"Testing PDF Converter Service at {url}")
    print(f"PDF Path: {pdf_path}")
    print("-" * 60)
    
    # Create test message
    message_data = create_test_message(pdf_path, file_id)
    envelope = create_pubsub_envelope(message_data)
    
    # Send request
    try:
        response = requests.post(
            url,
            json=envelope,
            headers={"Content-Type": "application/json"},
            timeout=300
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✓ Test passed!")
            return True
        else:
            print("\n✗ Test failed!")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Request failed: {e}")
        return False


def test_health(url: str):
    """Test the health endpoint."""
    health_url = f"{url.rstrip('/')}/health"
    print(f"Testing health endpoint: {health_url}")
    
    try:
        response = requests.get(health_url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✓ Health check passed!")
            return True
        else:
            print("✗ Health check failed!")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Health check failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test the PDF Converter Service")
    parser.add_argument(
        "--url",
        default="http://localhost:8080",
        help="Service URL (default: http://localhost:8080)"
    )
    parser.add_argument(
        "--pdf-path",
        default="tensrgrid/documents/2/test.pdf",
        help="GCS path to test PDF"
    )
    parser.add_argument(
        "--file-id",
        type=int,
        default=1,
        help="Test file ID"
    )
    parser.add_argument(
        "--health-only",
        action="store_true",
        help="Only test the health endpoint"
    )
    
    args = parser.parse_args()
    
    if args.health_only:
        success = test_health(args.url)
    else:
        # Test health first
        print("Step 1: Testing health endpoint")
        health_ok = test_health(args.url)
        print("\n" + "=" * 60 + "\n")
        
        if not health_ok:
            print("Warning: Health check failed, but continuing with conversion test...")
        
        # Test conversion
        print("Step 2: Testing PDF conversion")
        success = test_service(args.url, args.pdf_path, args.file_id)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
