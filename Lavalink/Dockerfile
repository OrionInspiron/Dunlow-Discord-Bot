FROM eclipse-temurin:17-jre-alpine

WORKDIR /opt/lavalink

# Download Lavalink v4.0.8 (latest stable v4)
RUN apk add --no-cache wget && \
    wget https://github.com/lavalink-devs/Lavalink/releases/download/4.0.8/Lavalink.jar

# Copy our custom configuration
COPY application.yml application.yml

# Expose the default port
EXPOSE 2333

# Run Lavalink
CMD ["java", "-jar", "Lavalink.jar"]
