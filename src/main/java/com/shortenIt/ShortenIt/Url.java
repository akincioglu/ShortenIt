package com.shortenIt.ShortenIt;

import org.springframework.data.annotation.Id;

public class Url {
    @Id
    private String id;
    private String originalId;
    private String shortUrl;

    public Url() {
    }

    public String getId() {
        return id;
    }

    public String getOriginalUrl() {
        return originalId;
    }

    public void setOriginalUrl(String originalUrl) {
        this.originalId = originalUrl;
    }

    public String getShortUrl() {
        return shortUrl;
    }

    public void setShortUrl(String shortUrl) {
        this.shortUrl = shortUrl;
    }
}
