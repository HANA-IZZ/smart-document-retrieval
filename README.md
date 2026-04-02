# IR-PROJECT
# 🧠 Smart Document Retrieval System

A powerful, smart document search and analytics system built with **Python**, **Flask**, and **OpenSearch**. The system leverages Natural Language Processing (NLP) using **spaCy** to automatically extract locations, dates, and temporal expressions from text to provide advanced spatial and temporal search capabilities.

---

## ✨ Features

* **Smart Search:** Multi-faceted search combining text relevance, geographical locations (geo-points), and specific timeframes.
* **Auto-complete Search:** Instant as-you-type search suggestions using Edge N-gram filters.
* **NLP Automation:** Automatic extraction of geographical places and dates using `spaCy`.
* **Rich Analytics Dashboard:** * Top mentioned geographical references.
    * Chronological document distribution (timeline).
    * Index statistics (storage size, document count).
* **Dockerized:** Easy deployment and isolation using Docker.

---

## 🛠️ Tech Stack

* **Backend:** Python 3.10, Flask
* **Search Engine:** OpenSearch
* **NLP Library:** spaCy (`en_core_web_sm`)
* **Containerization:** Docker

---

## 📁 Project Structure

* `main.py`: Application entry point.
* `index_creation.py`: Script to define OpenSearch index mappings and custom analyzers (HTML strip, custom stop-words, stemmer, edge_ngram).
* `test.py`: Comprehensive test suite to verify all API endpoints.
* `Dockerfile`: Configuration to containerize the Flask application.

---

## 🚀 Getting Started

### Prerequisites

* Docker and Docker Compose (Recommended for running OpenSearch).
* Python 3.10+ (If running locally).

### 1. Setup OpenSearch
Make sure you have an OpenSearch instance running on `localhost:9200`. You can spin it up quickly using Docker:
```bash
docker run -p 9200:9200 -p 9600:9600 -e "discovery.type=single-node" opensearchproject/opensearch:latest
