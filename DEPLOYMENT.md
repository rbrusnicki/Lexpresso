# Deploying Lexpresso to www.brusnicki.com

This guide will help you deploy Lexpresso to your domain using Railway.app (recommended) or Render.com.

---

## Prerequisites

- Domain: **www.brusnicki.com** (managed by Squarespace)
- GitHub account (for deployment)
- Git installed on your computer

---

## Option 1: Railway.app (Recommended - Easiest)

### Cost
- Free tier: $5 credit/month (enough for testing)
- Paid: $5/month for 500 hours runtime
- Includes: Free SSL certificate, automatic deployments

### Step 1: Prepare Your Project

1. Open terminal in your Lexpresso folder
2. Initialize git (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Prepare for deployment"
   ```

3. Create GitHub repository:
   - Go to https://github.com/new
   - Name it "lexpresso"
   - Don't initialize with README (you already have files)
   - Click "Create repository"

4. Push your code to GitHub:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/lexpresso.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy to Railway

1. **Sign up:** Go to https://railway.app
   - Click "Login" → Sign in with GitHub

2. **Create New Project:**
   - Click "+ New Project"
   - Select "Deploy from GitHub repo"
   - Choose your "lexpresso" repository
   - Click "Deploy Now"

3. **Wait for deployment** (1-2 minutes)
   - Railway will automatically detect Python
   - It will run `python server.py`
   - You'll see build logs in the dashboard

4. **Get your Railway URL:**
   - Click on your deployment
   - Click "Settings" tab
   - Under "Domains" you'll see something like: `lexpresso-production.up.railway.app`
   - Click it to test - your app should work!

### Step 3: Connect Your Custom Domain (brusnicki.com)

#### On Railway:

1. In Railway dashboard, click "Settings"
2. Scroll to "Domains" section
3. Click "+ Custom Domain"
4. Enter: `www.brusnicki.com`
5. Railway will show you DNS records to add (something like):
   ```
   Type: CNAME
   Name: www
   Value: lexpresso-production.up.railway.app
   ```
6. **Keep this window open** - you'll need these values for Squarespace

#### On Squarespace (Domain Settings):

1. Go to https://account.squarespace.com/domains
2. Find **brusnicki.com** and click "Manage DNS Settings"
3. Add a new record:
   - **Type:** CNAME
   - **Host:** www
   - **Value:** (paste the value from Railway)
   - **TTL:** 3600 (or default)
4. Click "Add" or "Save"

#### Wait for DNS propagation
- Can take 5 minutes to 24 hours (usually 15-30 minutes)
- Check status at: https://www.whatsmydns.net/#CNAME/www.brusnicki.com

#### Enable SSL (Free)
- Railway automatically provisions SSL certificates
- Wait ~5-10 minutes after DNS propagation
- Your site will be accessible at: `https://www.brusnicki.com`

---

## Option 2: Render.com (Alternative)

### Cost
- Free tier available (app sleeps after 15 min of inactivity)
- Paid: $7/month for always-on
- Includes: Free SSL certificate

### Step 1: Prepare Your Project

Same as Railway - push to GitHub (see above)

### Step 2: Deploy to Render

1. **Sign up:** Go to https://render.com
   - Sign up with GitHub

2. **Create New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select "lexpresso" repository
   - Click "Connect"

3. **Configure Service:**
   - **Name:** lexpresso
   - **Environment:** Python 3
   - **Build Command:** (leave empty)
   - **Start Command:** `python server.py`
   - **Instance Type:** Free (or Starter $7/month)
   - Click "Create Web Service"

4. **Wait for deployment** (2-3 minutes)
   - You'll get a URL like: `https://lexpresso.onrender.com`
   - Test it - your app should work!

### Step 3: Connect Custom Domain

#### On Render:

1. Go to your service dashboard
2. Click "Settings" tab
3. Scroll to "Custom Domain"
4. Click "Add Custom Domain"
5. Enter: `www.brusnicki.com`
6. Render will show DNS instructions:
   ```
   Type: CNAME
   Name: www
   Value: lexpresso.onrender.com
   ```

#### On Squarespace:

Same as Railway instructions above - add CNAME record pointing to Render

---

## Troubleshooting

### DNS Not Working?
- Wait 30 minutes and try again
- Clear your browser cache (Ctrl+Shift+Delete)
- Check propagation: https://www.whatsmydns.net/#CNAME/www.brusnicki.com

### App Not Loading?
- Check deployment logs in Railway/Render dashboard
- Make sure server.py uses `PORT` environment variable (already fixed)

### User Data Not Saving?
- Cloud platforms have ephemeral storage
- **IMPORTANT:** For production, you'll need to add a database
- Current file-based storage works but resets on redeployment
- Future upgrade: Use PostgreSQL or MongoDB (I can help with this)

---

## Next Steps After Deployment

### 1. Test Your Site
- Visit: https://www.brusnicki.com
- Create a test user
- Try learning some words
- Check if progress saves

### 2. Set Up Persistent Storage (Recommended)
Your current app saves user data to files, which work locally but get reset when the cloud server restarts.

**Options:**
- **Railway Volumes:** Add persistent storage ($0.25/GB/month)
- **Database:** Switch to PostgreSQL (free on Railway)
- **Cloud Storage:** Use AWS S3 or similar

Let me know if you want help adding persistent storage!

### 3. Monitor Your App
- Railway/Render show logs and metrics
- Set up alerts for downtime
- Monitor usage to avoid unexpected costs

---

## Cost Summary

| Platform | Free Tier | Paid Tier | SSL | Custom Domain |
|----------|-----------|-----------|-----|---------------|
| Railway  | $5 credit/month | $5/month (500 hrs) | ✅ Free | ✅ Free |
| Render   | Yes (sleeps after 15min) | $7/month (always-on) | ✅ Free | ✅ Free |

**Recommendation:** Start with Railway's free tier, upgrade to paid ($5/month) if you need it always-on.

---

## Need Help?

If you run into issues:
1. Check deployment logs in Railway/Render dashboard
2. Verify DNS settings in Squarespace
3. Wait 30 minutes for DNS propagation
4. Ask me for help with specific error messages!

---

**Ready to deploy?** Start with Railway Option 1 above - it's the easiest!
