# Wikipedia Parser Evolution Project

A sophisticated Wikipedia parser that demonstrates the progression from simple synchronous parsing to high-performance asynchronous implementation. This project showcases different approaches to web scraping, implementing various Python technologies and concurrency patterns.

## 🚀 Features

- Multiple implementation levels showcasing different approaches to parsing
- Configurable parsing depth for Wikipedia articles
- Performance benchmarks for each implementation
- Docker support with PostgreSQL and Redis integration
- Code quality enforcement using Ruff linter

## 📊 Performance Comparison

| Implementation | Time (seconds) | Technologies Used                                                  |
|----------------|---------------|--------------------------------------------------------------------|
| Simple | 357.45 | sqlite, urllib, re                                                 |
| Intermediate | 275.67 | redis, psycopg, requests, bs4, lxml, re                            |
| Upper-Intermediate | 71.81 | threading, multiprocessing, psycopg, redis, requests,bs4, lxml, re |
| Advanced | 28.35 | asyncio, aiohttp, asyncpg, bs4, lxml, multiprocessing, re          |

*Test case: Parsing https://en.wikipedia.org/wiki/Python_(programming_language) with depth level 3*

## 🛠️ Implementation Levels

### Simple Parser
- Basic implementation using standard Python libraries
- Foundation for understanding web scraping concepts
- Usage instructions available in `/simple` directory

### Intermediate Parser
- Integration with Redis for caching
- PostgreSQL database integration using Psycopg
- Enhanced HTML parsing with BeautifulSoup
- Improved request handling with Requests library
- Usage instructions available in `/intermediate` directory

### Upper-Intermediate Parser
- Concurrent execution using ThreadPoolExecutor
- Parallel processing with ProcessPoolExecutor
- Custom DependenciesContainer implementation using dataclasses
- Improved architecture and dependency management
- Usage instructions available in `/upper_intermediate` directory

### Advanced Parser
- Full asynchronous implementation using asyncio
- High-performance database operations with asyncpg
- Maximum parsing efficiency and throughput
- Maintained clean architecture while adding async capabilities
- Usage instructions available in `/advanced` directory

## 🐳 Docker Integration

- Docker and Docker Compose configuration for:
  - PostgreSQL database
  - Redis cache
- Easy setup and deployment
- Isolated development environment

## 📚 Technical Foundation

This project was developed based on insights from:
- "Python Concurrency with Asyncio" by Matthew Fowler
- "Fluent Python" by Luciano Ramalho

## 🔍 Code Quality

- Ruff linter integration ensures:
  - Consistent code style
  - Best practices enforcement
  - Clean and maintainable codebase

## 📈 Performance Improvement

The project demonstrates significant performance improvements through its evolution:
- 12.6x speed improvement from Simple to Advanced implementation
- Efficient resource utilization through caching and concurrent processing
- Optimized database operations with async capabilities

