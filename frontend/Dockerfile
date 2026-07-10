FROM node:20-alpine

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

EXPOSE 5173

# Start Vite dev server on 0.0.0.0 to be accessible from host
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
