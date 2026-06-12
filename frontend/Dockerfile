# --- build the Vue SPA ---
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# --- serve it + proxy /api to the backend ---
FROM nginx:1.27-alpine
RUN rm -f /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/intake-demo.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
