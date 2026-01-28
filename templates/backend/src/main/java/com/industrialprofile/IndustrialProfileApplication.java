package com.industrialprofile;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import com.industrialprofile.ai.AiProperties;

@SpringBootApplication
@EnableConfigurationProperties(AiProperties.class)
public class IndustrialProfileApplication {
    public static void main(String[] args) {
        SpringApplication.run(IndustrialProfileApplication.class, args);
    }
}
