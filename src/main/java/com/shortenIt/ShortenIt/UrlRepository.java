package com.shortenIt.ShortenIt;

import org.springframework.data.mongodb.repository.MongoRepository;

public interface UrlRepository extends MongoRepository<Url, String> {
    Url findByShortUrl(String shortUrl);
}