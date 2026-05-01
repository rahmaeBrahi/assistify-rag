# Use an official Node runtime as a parent image
FROM node:18-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY package*.json /app/
RUN npm install

# Copy project
COPY . /app/

# Expose port
EXPOSE 3000

# Start application
CMD ["npm", "start"]
