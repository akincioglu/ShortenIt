package com.shortenIt.ShortenIt;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

@RestController
@RequestMapping("/api/v1/url")
public class UrlController {

    @Autowired
    private UrlService urlService;

    @PostMapping
    public Url createShortUrl(@RequestParam String originalUrl) {
        return urlService.generateShortUrl(originalUrl);
    }

    @GetMapping("/{shortUrl}")
    public Url getOriginalUrl(@PathVariable String shortUrl) {
        return urlService.getOriginaUrl(shortUrl);
    }
}
