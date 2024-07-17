package com.shortenIt.ShortenIt;

import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class UrlService {

    @Autowired
    private UrlRepository urlRepository;

    public Url generateShortUrl(String originalUrl) {
        Url url = new Url();
        url.setOriginalUrl(originalUrl);
        url.setShortUrl(UUID.randomUUID().toString().substring(0, 6));
        return urlRepository.save(url);
    }

    public Url getOriginaUrl(String shortUrl) {
        return urlRepository.findByShortUrl(shortUrl);
    }
}
