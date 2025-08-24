FROM node:20-alpine
ARG api_base_url
WORKDIR /app

# Clear npm cache
RUN npm cache clean --force

# Copy package files
COPY package*.json ./

# Install dependencies with legacy peer deps for React version compatibility
RUN npm install --legacy-peer-deps --verbose

# Copy rest of application
COPY . .

# Set environment variable for Vite
RUN echo "VITE_API_BASE_URL=${api_base_url}" > .env

EXPOSE 5173
CMD ["npm", "run", "dev"]