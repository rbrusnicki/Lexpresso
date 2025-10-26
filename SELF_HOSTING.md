# Self-Hosting Lexpresso on Your Own Computer

You can host Lexpresso on your own computer and point **www.brusnicki.com** directly to it!

## 🎯 Quick Start for FRITZ!Box Users

**You have:** FRITZ!Box router + Public IP 80.140.113.56 + Domain brusnicki.com

**Steps to get online:**

1. **Port Forwarding** (5 min)
   - Go to http://fritz.box
   - Internet → Permit Access → Port Sharing
   - Forward port 80 to your computer
   - Click Apply twice (in popup, then on main page)
   - Verify green status indicator

2. **Windows Firewall** (1 min)
   - Open Command Prompt as Administrator
   - Run: `netsh advfirewall firewall add rule name="Lexpresso Server" dir=in action=allow protocol=TCP localport=80`

3. **Test External Access** (2 min)
   - Run: `python server.py`
   - From phone (mobile data): visit http://80.140.113.56

4. **DNS Setup - Add Subdomain** (2 min)
   - Log in to Squarespace DNS Settings
   - Add A record: lexpresso → 80.140.113.56
   - Keep existing www/homepage unchanged

5. **Access Your Site** (15-30 min wait)
   - Visit: lexpresso.brusnicki.com
   - Your app is live!

6. **Auto-Start on Boot** (2 min - Recommended)
   - Open PowerShell as Administrator
   - Run: `.\setup_autostart.ps1`
   - Server now starts automatically when Windows boots!

7. **MyFRITZ! Setup** (3 min - Optional but recommended)
   - Internet → MyFRITZ! Account
   - Handles dynamic IP automatically!

**Total time: ~20 minutes + 15-30 min DNS wait**

Detailed instructions below ⬇️

---

## Pros & Cons

### ✅ Advantages
- **Free hosting** (only electricity costs)
- **Full control** over everything
- **User data stays on your computer** (already working!)
- **No monthly fees**
- **Learn networking and server administration**

### ❌ Disadvantages
- **Computer must run 24/7** (or site goes down)
- **Your home IP address exposed** (security consideration)
- **Requires router configuration** (port forwarding)
- **Home internet reliability** (if internet goes down, site goes down)
- **Dynamic IP issues** (if your ISP changes your IP, you need to update DNS)
- **Electricity costs** (~$5-15/month depending on your computer)

---

## Prerequisites

✅ You already have:
- Working Python server (`server.py`)
- Domain: **brusnicki.com** (Squarespace)
- Computer that can stay on 24/7

🔍 You need to find out:
- Your public IP address
- Does your ISP give you a static or dynamic IP?
- Router admin access

---

## Step 1: Check Your Public IP Address

### Find Your Current Public IP

1. Go to: https://whatismyipaddress.com/
2. Write down your **IPv4 address** (looks like: `123.456.789.012`) //80.140.113.56 

### Check if Your IP is Static or Dynamic

**Static IP:** Always the same (rare for home internet, often costs extra)
**Dynamic IP:** Changes occasionally (most common for home users)

**How to check:**
1. Note your IP today
2. Check again in a few days
3. If it changed → you have a **dynamic IP** (we'll handle this in Step 6 with MyFRITZ!)

---

## Step 2: Configure Port Forwarding on Your FRITZ!Box Router

You need to tell your FRITZ!Box to forward incoming web traffic (port 80) to your computer.

### Find Your Computer's Local IP Address

First, we need to know your computer's local IP address.

Open Command Prompt:
```bash
ipconfig
```

Look for "IPv4 Address" under your active network adapter (usually Ethernet or Wi-Fi)
- Should look like: `192.168.178.60` (FRITZ!Box default range)
- **Write this down** - you'll need it below

Example:
```
IPv4 Address. . . . . . . . . . . : 192.168.178.60
```

### Access FRITZ!Box Admin Interface

FRITZ!Box routers have a very user-friendly interface called "FRITZ!Box Fon".

1. Open your browser and go to one of these addresses:
   - **http://fritz.box** (easiest - works on most FRITZ!Box routers)
   - Or **http://192.168.178.1** (default FRITZ!Box IP)

2. Login with your FRITZ!Box password
   - If you never changed it, check the sticker on the bottom of your router
   - Default username is usually blank or "admin"

### Set Up Port Forwarding (Port Sharing)

**You're already on the correct page!** Go to: **Internet → Permit Access → Port Sharing** tab

**Follow these exact steps:**

#### Step 1: Select Your Device

1. Click **"Add Device for Sharing"** button (at the bottom of the page)

2. In the **"Device"** dropdown:
   - Click on it (it says "Please select...")
   - Find your computer under **"Active devices"**
   - Select your computer (e.g., "R2D2" or the name of your PC)
   - The IPv4 address will automatically fill in

#### Step 2: Create Port Sharing

1. Scroll down to the **"Sharing"** section

2. Click the **"New Sharing"** button

3. A popup will appear with two options:
   - Select **"Port Sharing"** (NOT "MyFRITZ! sharing")

#### Step 3: Fill Out the Port Sharing Form

In the form that appears, enter:

- **Application:** Select **"Other application"** from dropdown
- **Name:** Type **Lexpresso**
- **Protocol:** Select **TCP**
- **Port to device:** Type **80**
- **through port:** Type **80**
- **Port requested externally:** Type **80**

⚠️ **You'll see a warning:** "Opening port 80 for the internet is highly risky..."
- This is normal - port 80 is the standard web port
- It's safe for hosting your language learning app
- You can add encryption (HTTPS) later if needed

**Enable sharing:**
- ✅ Check the **"Enable sharing"** checkbox

**Internet access:**
- Select **"Internet access via IPv4 and IPv6"**
- (Or just "IPv4" if you prefer - both work)

#### Step 4: Configure Device Settings

After clicking OK, you'll see the main device configuration page. You should see:

**Device Information:**
- Device: R2D2 (or your computer name)
- IPv4 address: 192.168.178.60 (or your IP)
- MAC address: (your MAC)
- IPv6 interface ID: (displayed)

**Leave these checkboxes UNCHECKED:**

1. ❌ **"Permit independent port sharing for this device"**
   - This is for automatic UPnP/PCP port sharing
   - We're using manual port forwarding, so leave this unchecked

2. Under **IPv4 Settings:**
   - ❌ **"Open this device completely for internet sharing via IPv4 (exposed host)"**
   - This would expose ALL ports, which is dangerous
   - We only want port 80, which we already configured

3. Under **IPv6 Settings:**
   - ❌ **"Enable PING6"** - Not needed for basic setup
   - ❌ **"Open firewall for delegated IPv6 prefixes"** - Not needed
   - ❌ **"Open this device completely via IPv6"** - Not needed

**In the Sharing table, you should see:**
```
Status       | Name      | Protocol | IP Address in the Internet
Gray ball    | Lexpresso | TCP      | Click on "Apply" to save this sharing...
```

#### Step 5: Apply and Activate (Twice!)

1. **Click the "OK" button** in the Port Sharing popup to save the sharing configuration

2. **You'll return to the main device page** - Click the **"Apply" button** at the bottom

3. **Go back to "Permit Access" page** - Navigate back to **Internet → Permit Access → Port Sharing** tab

4. **Click the "Apply" button again** on this page

5. **Verify the status:**
   - You should see **"Lexpresso"** in the Sharing table
   - The status indicator should be a **GREEN circle** ✅ (for both IPv4 and IPv6)
   - Port 80 is now forwarded to your computer!

**Success! Port forwarding is now active.**

### Important FRITZ!Box Settings

**Enable MyFRITZ! (Optional but Helpful)**

FRITZ!Box has a built-in dynamic DNS service called MyFRITZ!:

1. Go to **"Internet"** → **"MyFRITZ! Account"**
2. Click **"New MyFRITZ! Account"** (if you don't have one)
3. Create account with email address
4. Enable **"MyFRITZ! Internet Access"**
5. You'll get a free hostname like: `yourname.myfritz.net`

**This is useful if your IP address changes!** (See Step 6 for more details)

### Check FRITZ!Box WAN IP

Verify FRITZ!Box sees the same public IP:

1. In FRITZ!Box interface, go to **"Overview"** (home screen)
2. Under **"Internet"** section, you should see:
   - **IPv4 Address:** 80.140.113.56 (should match your public IP)
3. If it shows a different IP (like 192.168.x.x), you might be behind **carrier-grade NAT** (more complex - let me know if this happens)

**Port forwarding is now complete!** Proceed to Step 3 to configure Windows Firewall, then Step 4 to test.

---

## Step 3: Configure Windows Firewall

Windows Firewall blocks incoming connections by default. We need to allow port 80:

### Quick Method (Recommended)

**Open Command Prompt as Administrator:**
1. Press **Windows key**
2. Type **"cmd"**
3. Right-click **"Command Prompt"**
4. Select **"Run as administrator"**

**Run this command:**
```bash
netsh advfirewall firewall add rule name="Lexpresso Server" dir=in action=allow protocol=TCP localport=80
```

You should see: `Ok.`

**Done!** Port 80 is now allowed through Windows Firewall.

### Alternative: GUI Method

If you prefer using the graphical interface:

1. Open **Windows Defender Firewall with Advanced Security**
   - Press Windows key, search "Windows Defender Firewall"
   - Click "Advanced settings" on the left

2. Click **Inbound Rules** → **New Rule...**

3. Configure the rule:
   - **Rule Type:** Port
   - **Protocol:** TCP
   - **Specific local ports:** 80
   - **Action:** Allow the connection
   - **Profile:** Check all (Domain, Private, Public)
   - **Name:** Lexpresso Server

4. Click Finish

---

## Step 4: Test External Access

Now let's verify everything works before configuring DNS!

### Start the Lexpresso Server

1. **Open Command Prompt** (regular, not admin)

2. **Navigate to Lexpresso folder:**
   ```bash
   cd C:\Users\Administrator\Documents\Lexpresso
   ```

3. **Start the server:**
   ```bash
   python server.py
   ```

4. **You should see:**
   ```
   ============================================================
                 Lexpresso Server Running
   ============================================================
     Local:      http://localhost:80
     Network:    http://192.168.178.60:80

     User data saved to: user_stats/
     Press Ctrl+C to stop
   ============================================================
   ```

**Keep this window open!** The server must run for the next test.

### Test from External Network

**IMPORTANT:** Use your phone with **MOBILE DATA** (turn off WiFi!)

1. **On your phone:** Turn off WiFi, use mobile data only

2. **Open browser** on your phone

3. **Navigate to:** `http://80.140.113.56`

4. **Expected result:**
   - ✅ **SUCCESS:** Lexpresso app loads, you see the login/word learning interface
   - ❌ **Connection timeout:** Check port forwarding or firewall
   - ❌ **Connection refused:** Server not running

### Troubleshooting

**If it doesn't work:**

1. **Check port forwarding:** Go back to FRITZ!Box → Internet → Permit Access → Port Sharing
   - Verify green status for Lexpresso
   - Verify port 80 is correctly configured

2. **Check firewall:** Run this in Command Prompt (as Admin):
   ```bash
   netsh advfirewall firewall show rule name="Lexpresso Server"
   ```
   - Should show: `Enabled: Yes` and `Direction: In`

3. **Check server is running:** Look for the server window with the "Lexpresso Server Running" message

4. **Verify public IP:** Go to https://whatismyipaddress.com/ and confirm it's still 80.140.113.56

**If everything works:** Congratulations! Your server is accessible from the internet! 🎉

Leave the server running and proceed to Step 5 to configure your domain.

---

## Step 5: Point Your Domain to Your Computer

Now we'll create a subdomain for Lexpresso. This approach lets you keep your existing homepage and add Lexpresso as a subdomain.

### Why Use a Subdomain?

**Recommended structure:**
- **www.brusnicki.com** → Your homepage (Blogspot, custom page, etc.)
- **lexpresso.brusnicki.com** → Your Lexpresso app (self-hosted)
- **Future projects:** project2.brusnicki.com, etc.

**Benefits:**
- ✅ Keep your existing homepage unchanged
- ✅ No code modifications needed
- ✅ Each project is independent
- ✅ Professional and scalable
- ✅ Easy to add more projects later

### On Squarespace (DNS Settings)

1. Go to: https://account.squarespace.com/domains
2. Find **brusnicki.com** → Click "DNS Settings" (left menu)

3. **Add a subdomain A Record:**
   - Click **"Add record"** under "Custom records"
   - **Host:** `lexpresso` (or your project name)
   - **Type:** `A`
   - **Data:** Your public IP address (e.g., `80.140.113.56`)
   - **TTL:** `4 hrs` (or default)
   - Click **Save**

4. **Leave other records as they are** (don't modify www or @ if you have an existing site)

### Wait for DNS Propagation (15-30 minutes)

Check if it's working:
- Go to: https://www.whatsmydns.net/#A/lexpresso.brusnicki.com
- Enter your subdomain (e.g., `lexpresso.brusnicki.com`)
- Wait until you see your IP address appear

### Test Your Subdomain

After DNS propagates (usually 15-30 minutes, sometimes faster):

1. **Visit:** `http://lexpresso.brusnicki.com` (use your subdomain)
2. **Expected:** Lexpresso app loads just like it did with the IP address
3. **Also verify:** Your existing homepage (www.brusnicki.com) still works
4. **Success!** Your app is now accessible via subdomain! 🎉

**Note:** `server.py` is already configured to run on port 80 by default, so no changes needed.

### Adding More Projects Later

To add more self-hosted projects, just repeat Step 5:
- Add another A record: `project2` → `80.140.113.56`
- Access at: `http://project2.brusnicki.com`

You can host multiple projects on the same computer using different ports and nginx reverse proxy (more advanced setup).

---

## Step 6: Handle Dynamic IP (If Your IP Changes)

If your ISP gives you a dynamic IP (changes occasionally), your domain will break when the IP changes.

### Solution: Use MyFRITZ! (Easiest - Built into FRITZ!Box!)

**FRITZ!Box has free Dynamic DNS built-in!** This is much easier than third-party services.

**If you already set up MyFRITZ! in Step 2, you're done!** Otherwise:

1. In FRITZ!Box interface: **"Internet"** → **"MyFRITZ! Account"**

2. Create a free MyFRITZ! account:
   - Click **"New MyFRITZ! Account"**
   - Enter your email address
   - Follow registration steps

3. Enable **"MyFRITZ! Internet Access"**

4. You'll get a free hostname, for example:
   - `brusnicki-home.myfritz.net`

5. **Point your domain to MyFRITZ!** - In Squarespace DNS:
   - **Type:** CNAME
   - **Host:** www
   - **Value:** brusnicki-home.myfritz.net (use your actual MyFRITZ! address)
   - **TTL:** 3600

**How it works:**
- FRITZ!Box automatically updates MyFRITZ! whenever your IP changes
- Your domain (www.brusnicki.com) points to MyFRITZ! hostname
- MyFRITZ! always points to your current IP
- Everything happens automatically - no software to install!

### Alternative: Other DDNS Services (If you prefer)

**Option A: No-IP (Popular, Free)**

1. Sign up at https://www.noip.com/
2. Create hostname like: `brusnicki.no-ip.org`
3. In FRITZ!Box: **"Internet"** → **"Permit Access"** → **"DynDNS"** tab
4. Select **"No-IP"** from dropdown
5. Enter your No-IP credentials
6. FRITZ!Box will update No-IP automatically!

**Option B: DuckDNS (Simple, Free)**

1. Go to https://www.duckdns.org/
2. Sign in with GitHub/Google
3. Create subdomain
4. Use their update URL in a script (more manual)

**Recommendation: Use MyFRITZ!** - It's already in your router, free, and works perfectly with FRITZ!Box.

---

## Step 7: Set Up HTTPS (Optional but Recommended)

Right now you only have HTTP (not secure). For HTTPS, you need an SSL certificate.

### Options for SSL:

**Option A: Use Cloudflare (Easiest)**

1. Sign up at https://cloudflare.com (free)
2. Add your domain: brusnicki.com
3. Change nameservers in Squarespace to Cloudflare's
4. Cloudflare provides free SSL automatically
5. Set up "Flexible SSL" mode
6. Bonus: Cloudflare hides your home IP address!

**Option B: Use Let's Encrypt + Certbot (Advanced)**

- Get free SSL certificates from Let's Encrypt
- Requires more setup on Windows
- Certificates expire every 90 days (auto-renewal needed)

**For now, I recommend starting with HTTP only, then adding Cloudflare later.**

---

## Step 8: Keep Your Computer Running 24/7

### Power Settings

1. **Disable sleep mode:**
   - Settings → System → Power & Sleep
   - Set "When plugged in, PC goes to sleep after" → **Never**

2. **Prevent automatic updates/restarts:**
   - Settings → Windows Update → Advanced options
   - Disable automatic restart

3. **Auto-start server on boot:**
   - Use the automated setup script included with Lexpresso
   - See AUTOSTART_SETUP.md for complete instructions

### Automated Auto-Start Setup (Recommended)

Lexpresso includes an automated setup script that configures Windows Task Scheduler:

**Quick Setup:**
1. Open PowerShell as Administrator
2. Navigate to: `C:\Users\Administrator\Documents\Lexpresso`
3. Run: `.\setup_autostart.ps1`

This creates a Windows Task Scheduler task that:
- Starts server automatically on boot
- Runs as SYSTEM account (works without user login)
- Auto-restarts if it crashes (up to 3 times)
- Works even when no user is logged in

**For detailed instructions, troubleshooting, and manual setup options:**
- See **AUTOSTART_SETUP.md** in the Lexpresso folder

---

## Testing Checklist

After setup, verify these:

- [x] Port forwarding configured in FRITZ!Box (green status)
- [x] Windows Firewall allows port 80
- [x] Server runs on your computer (port 80)
- [x] You can access from local network (http://192.168.178.60)
- [x] You can access from external network using public IP (http://80.140.113.56)
- [x] Subdomain lexpresso.brusnicki.com resolves to your IP (DNS configured in Step 5)
- [x] You can access site via subdomain from outside your network
- [x] Existing homepage (www.brusnicki.com) still works
- [ ] User data saves properly - test by creating account and learning words
- [x] Server auto-starts if computer reboots (see Step 8 and AUTOSTART_SETUP.md)

---

## Troubleshooting

### Can't access from outside network
- Check port forwarding is correct
- Check firewall allows port 80
- Verify public IP is correct
- Test with phone on mobile data (not WiFi)

### Domain not working
- Wait 30+ minutes for DNS propagation
- Clear browser cache
- Check DNS with: https://www.whatsmydns.net

### Site slow or unreliable
- Check your home internet speed
- Consider upgrading internet plan
- Or switch to cloud hosting ($5-7/month)

### IP address changed
- Set up DDNS (see Step 6)
- Update DNS records in Squarespace

### Security concerns
- Use Cloudflare to hide your real IP
- Keep Windows updated
- Don't expose other ports
- Monitor access logs

---

## Cost Comparison

| Method | Initial Cost | Monthly Cost | Reliability |
|--------|--------------|--------------|-------------|
| **Self-Hosted** | $0 | ~$10 (electricity) | Depends on home internet |
| **Railway** | $0 | $5 (after free tier) | 99.9% uptime |
| **Render** | $0 | $0 (free tier) or $7 | 99.9% uptime |

---

## My Recommendation

**For learning/personal use:** Self-hosting is great! You learn a lot and save money.

**For production/reliable access:** Use Railway ($5/month) or Render (free tier).

**Best of both worlds:**
1. Start self-hosting to learn
2. Use Cloudflare for SSL and IP hiding
3. If your home internet is unreliable, switch to cloud hosting later

---

## Quick Setup Summary

```bash
# 1. Find your public IP
# Go to: whatismyipaddress.com
# Example: 80.140.113.56

# 2. Find your local IP
ipconfig
# Look for IPv4 Address, e.g., 192.168.178.60

# 3. Configure port forwarding in FRITZ!Box
# - Go to: http://fritz.box
# - Internet → Permit Access → Port Sharing
# - Add Device for Sharing → Select your computer
# - New Sharing → Port Sharing
# - Application: Other application
# - Name: Lexpresso
# - Protocol: TCP
# - Ports: 80 / 80 / 80
# - Enable sharing ✓
# - Internet access via IPv4 and IPv6
# - Click OK, then Apply
# - Go back to Port Sharing tab and click Apply again
# - Verify green status indicator ✅

# 4. Allow through Windows Firewall (as Administrator)
netsh advfirewall firewall add rule name="Lexpresso Server" dir=in action=allow protocol=TCP localport=80

# 5. Start server
cd C:\Users\Administrator\Documents\Lexpresso
python server.py

# 6. Test from phone (mobile data, not WiFi!)
# Visit: http://80.140.113.56

# 7. Add subdomain in Squarespace DNS
# Add record:
#   Host: lexpresso
#   Type: A
#   Data: 80.140.113.56
# (Leave www and @ records alone if you have existing homepage)

# 8. Wait 15-30 minutes, then visit lexpresso.brusnicki.com
# Success! Your app is live on the internet!

# 9. Set up auto-start on Windows boot (recommended)
# Open PowerShell as Administrator, then:
cd C:\Users\Administrator\Documents\Lexpresso
.\setup_autostart.ps1
# This creates a Task Scheduler task to start the server automatically
# See AUTOSTART_SETUP.md for details
```

---

**Need help with any step?** Let me know where you get stuck!
