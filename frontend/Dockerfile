FROM node:24-slim

WORKDIR /app

# Install dependencies first (layer cache)
COPY package.json package-lock.json* ./
RUN npm install

# Copy source
COPY . .

EXPOSE 5173

# --host is required so Vite listens on 0.0.0.0 inside the container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]