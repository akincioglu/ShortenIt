# ShortenIt

ShortenIt is a simple URL shortening application that converts long URLs into short ones. This application is developed using Java Spring Boot and MongoDB.

## Features

- Convert long URLs to short URLs.
- Retrieve original URLs using short URLs.
- Store URL records in the database.

## Technologies Used

- Spring Boot
- MongoDB
- Spring Data JPA
- Spring Web

## Usage

To run the application and use its APIs, follow these steps:

1. Start MongoDB database.
2. Navigate to the project directory and run `./gradlew bootRun` command to start the application.
3. Use the following endpoints for API interaction:

   - **Create Short URL**: `POST /api/v1/url?originalUrl={originalUrl}`
   - **Retrieve Original URL**: `GET /api/v1/url/{shortUrl}`

## Installation

1. Clone the project:

   ```bash
   git clone https://github.com/akincioglu/ShortenIt.git

2. Navigate into the project directory:
  
   ```bash
   cd ShortenIt

3. Configure MongoDB connection in application.properties or application.yml:

   ```bash
   spring.data.mongodb.uri=mongodb://localhost:27017/shortenItDB
   
5. Use Gradle to install project dependencies:

   ```bash
   ./gradlew build

7. Start the application:

   ```bash
   ./gradlew bootRun
