# 🚀 Render Deployment Guide

This guide will help you deploy your FastAPI GenAI Stock Analyzer on Render.com.

## 📋 Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **OpenAI API Key**: You'll need this for the application to work

## 🔧 Step-by-Step Deployment

### 1. **Prepare Your Repository**

Make sure your repository contains all the necessary files:
- `requirements.txt` or `requirements-render.txt`
- `runtime.txt` (specifies Python 3.11)
- `render.yaml` (deployment configuration)
- `Procfile` (process definition)
- `.render-buildpacks` (buildpack specification)
- `build.sh` (build script)

### 2. **Connect to Render**

1. Go to [render.com](https://render.com) and sign in
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Select the repository containing your FastAPI app

### 3. **Configure the Service**

Use these settings:

- **Name**: `fastapi-stock-analyzer` (or your preferred name)
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 4. **Set Environment Variables**

Add these environment variables in Render:

| Key | Value | Description |
|-----|-------|-------------|
| `OPENAI_API_KEY` | `your_openai_api_key` | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `APP_ENV` | `production` | Application environment |
| `LOG_LEVEL` | `INFO` | Logging level |
| `HOST` | `0.0.0.0` | Host binding |
| `PORT` | `$PORT` | Port (Render sets this automatically) |

### 5. **Deploy**

1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. Wait for the build to complete (usually 5-10 minutes)

## 🐛 Troubleshooting Common Issues

### **Build Failures**

#### Issue: `Cannot import 'setuptools.build_meta'`
**Solution**: 
- Make sure `setuptools>=65.0.0` is in your requirements.txt
- Use Python 3.11 instead of 3.13 (specified in runtime.txt)

#### Issue: `pip install` fails
**Solution**:
- Check that all package versions are compatible
- Use `requirements-render.txt` for Render-specific versions

#### Issue: `Module not found` errors
**Solution**:
- Ensure all dependencies are listed in requirements.txt
- Check for typos in package names

### **Runtime Errors**

#### Issue: Application won't start
**Solution**:
- Check the start command in Procfile
- Verify environment variables are set correctly
- Check logs for specific error messages

#### Issue: Port binding errors
**Solution**:
- Use `$PORT` environment variable (Render sets this)
- Bind to `0.0.0.0` not `localhost`

## 📁 File Structure for Render

```
your-repo/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── CustomAgent.py
│   ├── CustomTask.py
│   ├── CustomTool.py
│   └── SearchTool.py
├── requirements.txt
├── requirements-render.txt
├── runtime.txt
├── render.yaml
├── Procfile
├── .render-buildpacks
├── build.sh
├── README.md
└── .env.example
```

## 🔄 Automatic Deployments

Render automatically deploys when you:
- Push to your main branch
- Manually trigger a deploy
- Update environment variables

## 📊 Monitoring and Logs

### **View Logs**
1. Go to your service in Render dashboard
2. Click on "Logs" tab
3. View real-time logs and build logs

### **Health Checks**
- Your app has a `/health` endpoint
- Render will monitor this for uptime
- Configure health check path in render.yaml

## 💰 Cost Optimization

### **Free Tier Limits**
- 750 hours/month
- 512 MB RAM
- Shared CPU
- Sleeps after 15 minutes of inactivity

### **Upgrade Options**
- **Starter**: $7/month - Always on, 512 MB RAM
- **Standard**: $25/month - Always on, 1 GB RAM
- **Pro**: $50/month - Always on, 2 GB RAM

## 🚀 Production Considerations

### **Performance**
- Use `--workers 1` for free tier (memory constraints)
- Implement caching for expensive operations
- Monitor API response times

### **Security**
- Never commit `.env` files
- Use environment variables for secrets
- Implement rate limiting if needed

### **Scaling**
- Start with free tier for testing
- Upgrade when you need better performance
- Consider horizontal scaling for high traffic

## 🔧 Custom Domains

1. Go to your service settings
2. Click "Custom Domains"
3. Add your domain
4. Configure DNS records as instructed

## 📱 Testing Your Deployment

### **Health Check**
```bash
curl https://your-app.onrender.com/health
```

### **API Documentation**
- Visit: `https://your-app.onrender.com/docs`
- Test endpoints directly from the browser

### **Stock Analysis**
```bash
curl "https://your-app.onrender.com/stock/TCS"
```

## 🆘 Getting Help

### **Render Support**
- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com)
- [Render Status](https://status.render.com)

### **Common Issues**
1. **Build failures**: Check requirements.txt and Python version
2. **Runtime errors**: Check logs and environment variables
3. **Performance issues**: Consider upgrading your plan

## 🎉 Success Checklist

- [ ] Repository connected to Render
- [ ] Environment variables set
- [ ] Build successful
- [ ] Application accessible via URL
- [ ] Health check endpoint working
- [ ] API documentation accessible
- [ ] Test stock analysis endpoint

## 🔄 Update Process

1. Make changes to your code
2. Push to GitHub
3. Render automatically rebuilds and deploys
4. Monitor logs for any issues
5. Test the updated application

---

**Happy Deploying! 🚀**

If you encounter any issues, check the logs first and refer to this guide for common solutions.
