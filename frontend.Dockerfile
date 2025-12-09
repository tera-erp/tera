# 1. Base Image
FROM node:20-alpine

# 2. Set Working Directory
WORKDIR /app

# 3. Copy dependency definitions from 'ui' subdirectory
COPY ui/package.json ui/package-lock.json ./

# 4. Install dependencies
RUN npm install

# 5. Copy all frontend source code from 'ui' subdirectory
COPY ui/ ./

# 6. Expose port and set command
EXPOSE 8080
CMD ["npm", "run", "dev"]
