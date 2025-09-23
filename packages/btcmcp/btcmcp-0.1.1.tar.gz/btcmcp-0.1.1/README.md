# BTC MCP Server

Bitcoin price MCP server deployed on Vercel with GitHub auto-deployment.

## 🚀 Features

- Real-time Bitcoin price from Binance API
- RESTful API endpoints
- Automatic deployment from GitHub
- Health monitoring

## 📡 API Endpoints

- `GET /api/get_btc_price` - Get current Bitcoin price
- `GET /api/health` - Health check
- `GET /api/tools` - List available tools
- `GET /` - API documentation

## 🛠️ Local Development

```bash
# Install dependencies
uv sync

# Run locally
uv run python api/index.py

# Test
uv run python test_btcmcp.py
```

## 🚀 Deployment

### Automatic Deployment (GitHub + Vercel)

1. **Setup Vercel Secrets in GitHub:**
   - Go to your GitHub repository → Settings → Secrets and variables → Actions
   - Add these secrets:
     - `VERCEL_TOKEN`: Your Vercel API token
     - `ORG_ID`: Your Vercel organization ID
     - `PROJECT_ID`: Your Vercel project ID

2. **Push to main branch:**
   ```bash
   git add .
   git commit -m "Deploy to Vercel"
   git push origin main
   ```

3. **Automatic deployment:**
   - GitHub Actions will automatically deploy to Vercel
   - Your API will be available at: `https://your-app.vercel.app`

### Manual Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

## 📊 Example Usage

```bash
# Get Bitcoin price
curl https://your-app.vercel.app/api/get_btc_price

# Health check
curl https://your-app.vercel.app/api/health
```

## 🔧 Configuration

The server uses:
- **Flask** for web API
- **Binance API** for Bitcoin price data
- **Vercel** for hosting
- **GitHub Actions** for CI/CD