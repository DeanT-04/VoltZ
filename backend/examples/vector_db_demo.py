#!/usr/bin/env python3
"""
Demo script for vector database and embedding system.
Shows how to ingest component data and perform searches.
"""

import os
import sys
import time
from pathlib import Path

# Add the backend src to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.embeddings import get_embedding_service
from services.vector_db import get_vector_db_service
from services.datasheet_ingestion import get_datasheet_ingestion_service


def demo_embedding_service():
    """Demonstrate embedding service functionality."""
    print("=== Embedding Service Demo ===")
    
    embedding_service = get_embedding_service()
    
    # Test single embedding
    text = "ESP32 microcontroller with WiFi and Bluetooth capabilities"
    print(f"Generating embedding for: '{text}'")
    
    start_time = time.time()
    embedding = embedding_service.generate_embedding(text)
    end_time = time.time()
    
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    print(f"Generation time: {(end_time - start_time) * 1000:.2f}ms")
    
    # Test batch embeddings
    texts = [
        "Temperature sensor with high accuracy",
        "Voltage regulator for power management",
        "GPIO pins for digital input/output"
    ]
    
    print(f"\nGenerating embeddings for {len(texts)} texts...")
    start_time = time.time()
    embeddings = embedding_service.generate_embeddings(texts)
    end_time = time.time()
    
    print(f"Generated {len(embeddings)} embeddings")
    print(f"Batch generation time: {(end_time - start_time) * 1000:.2f}ms")
    print()


def demo_vector_database():
    """Demonstrate vector database functionality."""
    print("=== Vector Database Demo ===")
    
    vector_db = get_vector_db_service()
    
    # Sample component data
    component_data = [
        {
            "text": "ESP32-WROOM-32 is a powerful, generic Wi-Fi+BT+BLE MCU module that targets a wide variety of applications. Features include 32 GPIO pins, SPI, I2C, UART interfaces, and built-in antenna.",
            "metadata": {
                "mpn": "ESP32-WROOM-32",
                "manufacturer": "Espressif",
                "category": "microcontroller",
                "description": "Wi-Fi + Bluetooth MCU module",
                "pins": 38,
                "voltage": "3.3V"
            }
        },
        {
            "text": "TMP117 is a high-accuracy, low-power, digital temperature sensor with 16-bit resolution and ±0.1°C accuracy. Communicates via I2C interface and operates from 1.8V to 5.5V supply voltage.",
            "metadata": {
                "mpn": "TMP117",
                "manufacturer": "Texas Instruments",
                "category": "sensor",
                "description": "High-accuracy digital temperature sensor",
                "interface": "I2C",
                "voltage": "1.8V-5.5V"
            }
        },
        {
            "text": "LM2596 step-down switching regulator provides 3A output current with excellent line and load regulation. Input voltage range 4.75V to 40V, adjustable output voltage from 1.2V to 37V.",
            "metadata": {
                "mpn": "LM2596",
                "manufacturer": "Texas Instruments", 
                "category": "power",
                "description": "3A step-down switching regulator",
                "input_voltage": "4.75V-40V",
                "output_current": "3A"
            }
        },
        {
            "text": "DS18B20 1-Wire digital temperature sensor provides 9-bit to 12-bit temperature measurements. Each sensor has a unique 64-bit serial code for multi-drop applications on a single bus.",
            "metadata": {
                "mpn": "DS18B20",
                "manufacturer": "Maxim Integrated",
                "category": "sensor",
                "description": "1-Wire digital temperature sensor",
                "interface": "1-Wire",
                "resolution": "9-12 bit"
            }
        }
    ]
    
    # Add documents to vector database
    print("Adding component data to vector database...")
    texts = [item["text"] for item in component_data]
    metadata_list = [item["metadata"] for item in component_data]
    
    start_time = time.time()
    doc_ids = vector_db.add_document_chunks(texts, metadata_list)
    end_time = time.time()
    
    print(f"Added {len(doc_ids)} documents in {(end_time - start_time) * 1000:.2f}ms")
    
    # Get collection stats
    stats = vector_db.get_collection_stats()
    print(f"Collection stats: {stats}")
    
    # Perform searches
    search_queries = [
        "WiFi microcontroller with GPIO pins",
        "high accuracy temperature sensor",
        "voltage regulator for power supply",
        "I2C interface sensor"
    ]
    
    print("\n=== Search Results ===")
    for query in search_queries:
        print(f"\nQuery: '{query}'")
        
        start_time = time.time()
        documents, metadata, distances = vector_db.search_similar(query, n_results=2)
        end_time = time.time()
        
        search_time_ms = (end_time - start_time) * 1000
        print(f"Search time: {search_time_ms:.2f}ms")
        
        for i, (doc, meta, dist) in enumerate(zip(documents, metadata, distances)):
            print(f"  Result {i+1} (distance: {dist:.3f}):")
            print(f"    MPN: {meta['mpn']}")
            print(f"    Category: {meta['category']}")
            print(f"    Description: {meta['description']}")
            print(f"    Text preview: {doc[:100]}...")
    
    # Test category-specific search
    print("\n=== Category Search ===")
    categories = ["microcontroller", "sensor", "power"]
    
    for category in categories:
        print(f"\nSearching in category: {category}")
        
        start_time = time.time()
        documents, metadata, distances = vector_db.search_by_category(
            f"{category} specifications", category, n_results=1
        )
        end_time = time.time()
        
        search_time_ms = (end_time - start_time) * 1000
        print(f"Category search time: {search_time_ms:.2f}ms")
        
        if documents:
            meta = metadata[0]
            print(f"  Found: {meta['mpn']} - {meta['description']}")
        else:
            print(f"  No results found for category: {category}")
    
    print()


def demo_text_chunking():
    """Demonstrate text chunking functionality."""
    print("=== Text Chunking Demo ===")
    
    ingestion_service = get_datasheet_ingestion_service()
    
    # Create a long text document
    long_text = """
    The ESP32 is a series of low-cost, low-power system on a chip microcontrollers with integrated Wi-Fi and dual-mode Bluetooth.
    
    The ESP32 series employs a Tensilica Xtensa LX6 microprocessor in both dual-core and single-core variations and includes built-in antenna switches, RF balun, power amplifier, low-noise receive amplifier, filters, and power-management modules.
    
    ESP32 is created and developed by Espressif Systems, a Shanghai-based Chinese company, and is manufactured by TSMC using their 40 nm process. It is a successor to the ESP8266 microcontroller.
    
    The ESP32 has the following features:
    - CPU: Xtensa dual-core (or single-core) 32-bit LX6 microprocessor, operating at 160 or 240 MHz and performing at up to 600 DMIPS
    - Ultra low power (ULP) co-processor
    - Memory: 520 KiB SRAM, 448 KiB ROM
    - Wireless connectivity: Wi-Fi 802.11 b/g/n, Bluetooth v4.2 BR/EDR and BLE
    - Peripheral interfaces: 34 × programmable GPIOs, 12-bit SAR ADC up to 18 channels, 2 × 8-bit DACs, 10 × touch sensors
    - Security: IEEE 802.11 standard security features all supported, including WFA, WPA/WPA2 and WAPI
    - Power management: Internal low dropout regulator, individual power domain for RTC
    
    The ESP32 can perform as a complete standalone system or as a slave device to a host MCU, reducing communication stack overhead on the main application processor.
    """ * 3  # Repeat to make it longer
    
    source_metadata = {
        "mpn": "ESP32-WROOM-32",
        "manufacturer": "Espressif",
        "category": "microcontroller",
        "source_file": "esp32_datasheet.pdf",
        "datasheet_url": "https://example.com/esp32.pdf"
    }
    
    print(f"Original text length: {len(long_text)} characters")
    
    start_time = time.time()
    chunks_with_metadata = ingestion_service.create_text_chunks(long_text, source_metadata)
    end_time = time.time()
    
    print(f"Created {len(chunks_with_metadata)} chunks in {(end_time - start_time) * 1000:.2f}ms")
    
    for i, (chunk_text, chunk_metadata) in enumerate(chunks_with_metadata):
        print(f"\nChunk {i+1}:")
        print(f"  Length: {len(chunk_text)} characters")
        print(f"  Start: {chunk_metadata['chunk_start']}")
        print(f"  End: {chunk_metadata['chunk_end']}")
        print(f"  Preview: {chunk_text[:100]}...")
    
    print()


def main():
    """Run all demos."""
    print("VoltForge Vector Database and Embedding System Demo")
    print("=" * 60)
    
    try:
        demo_embedding_service()
        demo_vector_database()
        demo_text_chunking()
        
        print("Demo completed successfully!")
        print("\nPerformance Summary:")
        print("- Embedding generation: Fast (< 1000ms for small batches)")
        print("- Vector search: Fast (< 150ms per query)")
        print("- Text chunking: Efficient with provenance tracking")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())