"""
PDF to Markdown Converter Service
Listens to Google Pub/Sub messages, downloads PDFs from GCS,
converts them to Markdown, and uploads the result back to GCS.
"""

import os
import json
import logging
import base64
from typing import Dict, Any
from datetime import datetime

from flask import Flask, request, jsonify
from google.cloud import storage, pubsub_v1
from pdf_processor import PDFToMarkdownConverter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
GCS_BUCKET = os.environ.get('GCS_BUCKET', 'tensrgrid-raw-data')
OUTPUT_FOLDER = os.environ.get('OUTPUT_FOLDER', 'tensrgrid/markdown-output')
PROJECT_ID = os.environ.get('GCP_PROJECT_ID')

# Initialize GCS client
storage_client = storage.Client()


def download_from_gcs(bucket_name: str, source_path: str, destination_path: str) -> bool:
    """Download a file from Google Cloud Storage."""
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_path)
        blob.download_to_filename(destination_path)
        logger.info(f"Downloaded {source_path} from GCS to {destination_path}")
        return True
    except Exception as e:
        logger.error(f"Error downloading from GCS: {e}")
        return False


def upload_to_gcs(bucket_name: str, source_path: str, destination_path: str) -> str:
    """Upload a file to Google Cloud Storage."""
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_path)
        blob.upload_from_filename(source_path)
        logger.info(f"Uploaded {source_path} to GCS at {destination_path}")
        return f"gs://{bucket_name}/{destination_path}"
    except Exception as e:
        logger.error(f"Error uploading to GCS: {e}")
        raise


def process_pdf_message(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single PDF file conversion request."""
    try:
        # Extract message details
        data_file = message_data.get('data_file', {})
        storage_info = message_data.get('storage', {})
        
        file_id = data_file.get('id')
        storage_path = data_file.get('storage_path')
        original_name = data_file.get('original_name')
        mime_type = data_file.get('mime_type')
        bucket = storage_info.get('bucket', GCS_BUCKET)
        
        logger.info(f"Processing file: {original_name} (ID: {file_id})")
        
        # Check if it's a PDF
        if mime_type != 'application/pdf':
            logger.warning(f"Skipping non-PDF file: {mime_type}")
            return {
                'status': 'skipped',
                'reason': 'Not a PDF file',
                'file_id': file_id
            }
        
        # Create temporary directories
        os.makedirs('/tmp/downloads', exist_ok=True)
        os.makedirs('/tmp/outputs', exist_ok=True)
        
        # Download PDF from GCS
        local_pdf_path = f"/tmp/downloads/{file_id}_{original_name}"
        if not download_from_gcs(bucket, storage_path, local_pdf_path):
            raise Exception("Failed to download PDF from GCS")
        
        # Convert PDF to Markdown
        converter = PDFToMarkdownConverter()
        markdown_content = converter.convert(local_pdf_path)
        
        # Save markdown locally
        md_filename = original_name.replace('.pdf', '.md')
        local_md_path = f"/tmp/outputs/{file_id}_{md_filename}"
        
        with open(local_md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Converted PDF to Markdown: {md_filename}")
        
        # Construct output path in GCS
        # Example: tensrgrid/markdown-output/2/filename.md
        data_info = message_data.get('data', {})
        data_collection_id = message_data.get('data_collection', {}).get('id')
        
        output_path = f"{OUTPUT_FOLDER}/{data_collection_id}/{md_filename}"
        
        # Upload markdown to GCS
        gcs_uri = upload_to_gcs(bucket, local_md_path, output_path)
        
        # Clean up temporary files
        os.remove(local_pdf_path)
        os.remove(local_md_path)
        
        return {
            'status': 'success',
            'file_id': file_id,
            'original_name': original_name,
            'markdown_name': md_filename,
            'gcs_uri': gcs_uri,
            'output_path': output_path,
            'processed_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing PDF: {e}", exc_info=True)
        return {
            'status': 'error',
            'error': str(e),
            'file_id': data_file.get('id') if data_file else None
        }


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Cloud Run."""
    return jsonify({'status': 'healthy', 'service': 'pdf-converter'}), 200


@app.route('/', methods=['POST'])
def pubsub_push():
    """
    Handle Pub/Sub push messages.
    Cloud Run receives Pub/Sub messages via HTTP POST.
    """
    try:
        # Verify the request
        envelope = request.get_json()
        if not envelope:
            logger.error("No Pub/Sub message received")
            return jsonify({'error': 'Bad Request: no Pub/Sub message'}), 400
        
        # Extract Pub/Sub message
        pubsub_message = envelope.get('message', {})
        
        if not pubsub_message:
            logger.error("No message field in request")
            return jsonify({'error': 'Bad Request: invalid Pub/Sub message'}), 400
        
        # Decode the message data
        message_data_encoded = pubsub_message.get('data', '')
        message_data_str = base64.b64decode(message_data_encoded).decode('utf-8')
        message_data = json.loads(message_data_str)
        
        # Log the received message
        logger.info(f"Received message: {message_data.get('event_type')}")
        
        # Check event type
        event_type = message_data.get('event_type')
        if event_type != 'data_file_uploaded':
            logger.warning(f"Ignoring event type: {event_type}")
            return jsonify({'status': 'ignored', 'event_type': event_type}), 200
        
        # Process the PDF conversion
        result = process_pdf_message(message_data)
        
        # Return success response
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error handling Pub/Sub message: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # For local development
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
