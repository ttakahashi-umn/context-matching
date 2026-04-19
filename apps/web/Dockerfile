# syntax=docker/dockerfile:1
FROM node:24-bookworm-slim

RUN corepack enable && corepack prepare pnpm@10 --activate

ENV PNPM_HOME="/pnpm"
ENV PATH="${PNPM_HOME}:${PATH}"

WORKDIR /app

COPY package.json pnpm-lock.yaml* ./
RUN if [ -f pnpm-lock.yaml ]; then pnpm install --frozen-lockfile; else pnpm install; fi

COPY index.html vite.config.ts tsconfig.json ./
COPY src ./src

EXPOSE 5173

CMD ["pnpm", "exec", "vite", "--host", "0.0.0.0", "--port", "5173"]
