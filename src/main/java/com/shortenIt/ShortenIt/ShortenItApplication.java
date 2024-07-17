package com.shortenIt.ShortenIt;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;

@SpringBootApplication(exclude = { DataSourceAutoConfiguration.class })
public class ShortenItApplication {

	public static void main(String[] args) {
		SpringApplication.run(ShortenItApplication.class, args);
	}

}
