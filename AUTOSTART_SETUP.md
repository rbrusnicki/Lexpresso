# Lexpresso Auto-Start Setup Guide

This guide explains how to set up the Lexpresso server to start automatically when Windows boots.

## Files Created

1. **start_lexpresso.bat** - Batch script to manually start the server
2. **setup_autostart.ps1** - PowerShell script to configure auto-start
3. **AUTOSTART_SETUP.md** - This guide

---

## Quick Setup (Recommended)

### Option 1: Automatic Setup via PowerShell

1. **Right-click on PowerShell** and select **"Run as Administrator"**

2. **Navigate to the Lexpresso folder:**
   ```powershell
   cd C:\Users\Administrator\Documents\Lexpresso
   ```

3. **Allow script execution** (if needed):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Run the setup script:**
   ```powershell
   .\setup_autostart.ps1
   ```

5. **Done!** The server will now start automatically when Windows boots.

### Option 2: Manual Startup (No Auto-Start)

Just double-click **start_lexpresso.bat** whenever you want to start the server manually.

---

## What the Auto-Start Does

When you run `setup_autostart.ps1`, it creates a Windows Task Scheduler task that:

- Starts the Lexpresso server automatically when Windows boots
- Runs as SYSTEM account (works even if no user is logged in)
- Automatically restarts the server if it crashes (up to 3 times)
- Runs on port 80 by default

---

## Verifying Auto-Start is Working

### Method 1: Check Task Scheduler

1. Press **Win + R**, type **taskschd.msc**, press Enter
2. Look for **"Lexpresso Server Auto-Start"** in the task list
3. Right-click the task and select **"Run"** to test it immediately

### Method 2: Test After Reboot

1. Restart your computer
2. Wait 1-2 minutes after Windows starts
3. Open your browser and go to: **http://localhost**
4. If Lexpresso loads, auto-start is working!

### Method 3: Check if Server is Running

Open Command Prompt and run:
```cmd
netstat -ano | findstr :80
```

If you see output with "LISTENING" on port 80, the server is running.

---

## Managing the Auto-Start

### To Test the Task (Without Rebooting)

Open PowerShell as Administrator and run:
```powershell
Start-ScheduledTask -TaskName "Lexpresso Server Auto-Start"
```

### To Stop the Server

1. Open Task Manager (Ctrl+Shift+Esc)
2. Go to **Details** tab
3. Find **python.exe** processes
4. Right-click and select **End Task**

Or use PowerShell:
```powershell
Stop-ScheduledTask -TaskName "Lexpresso Server Auto-Start"
```

### To Disable Auto-Start (Temporarily)

```powershell
Disable-ScheduledTask -TaskName "Lexpresso Server Auto-Start"
```

### To Enable Auto-Start Again

```powershell
Enable-ScheduledTask -TaskName "Lexpresso Server Auto-Start"
```

### To Remove Auto-Start Completely

```powershell
Unregister-ScheduledTask -TaskName "Lexpresso Server Auto-Start" -Confirm:$false
```

---

## Troubleshooting

### Server doesn't start automatically

1. **Check if the task exists:**
   - Open Task Scheduler (Win+R, type `taskschd.msc`)
   - Look for "Lexpresso Server Auto-Start"

2. **Check task history:**
   - In Task Scheduler, right-click the task
   - Select "Properties" > "History" tab
   - Look for error messages

3. **Verify Python is in PATH:**
   ```cmd
   python --version
   ```
   If this fails, add Python to your system PATH

4. **Check Windows Event Viewer:**
   - Press Win+R, type `eventvwr.msc`
   - Look under Windows Logs > Application

### Port 80 is already in use

If another program is using port 80, you can change the port:

1. **Edit server.py** (line 197):
   ```python
   port = int(os.environ.get('PORT', 8000))  # Changed from 80 to 8000
   ```

2. **Update Windows Firewall** (if needed):
   ```cmd
   netsh advfirewall firewall add rule name="Lexpresso Server" dir=in action=allow protocol=TCP localport=8000
   ```

3. **Access the server at:**
   - http://localhost:8000

### Permission denied on port 80

Port 80 requires administrator privileges on Windows. The Task Scheduler task runs as SYSTEM, which has these privileges.

If you're starting manually, run Command Prompt as Administrator:
1. Right-click **start_lexpresso.bat**
2. Select **"Run as administrator"**

### Server keeps crashing

Check the server logs to see what's causing crashes:
1. The task will automatically restart up to 3 times
2. Look at the console window (if visible) for error messages
3. Check if user_stats directory is writable

---

## Manual Task Scheduler Setup (Alternative)

If the PowerShell script doesn't work, you can set up the task manually:

1. Open **Task Scheduler** (Win+R, type `taskschd.msc`)

2. Click **"Create Task..."** (not "Create Basic Task")

3. **General tab:**
   - Name: `Lexpresso Server Auto-Start`
   - Description: `Starts Lexpresso on boot`
   - Select: **"Run whether user is logged on or not"**
   - Select: **"Run with highest privileges"**

4. **Triggers tab:**
   - Click **"New..."**
   - Begin the task: **"At startup"**
   - Click **OK**

5. **Actions tab:**
   - Click **"New..."**
   - Action: **"Start a program"**
   - Program/script: `cmd.exe`
   - Arguments: `/c "C:\Users\Administrator\Documents\Lexpresso\start_lexpresso.bat"`
   - Start in: `C:\Users\Administrator\Documents\Lexpresso`
   - Click **OK**

6. **Settings tab:**
   - Check: **"Allow task to be run on demand"**
   - Check: **"Start the task only if the computer is on AC power"** (uncheck this)
   - Check: **"Stop the task if it runs longer than:"** (uncheck this)
   - If the running task does not end when requested: **"Do not stop"**

7. Click **OK** to save

---

## Checking Server Status

### View Server Logs

The server prints logs to the console. To see them:

1. Open Task Manager
2. Find the task or python.exe process
3. The console window may be hidden - check running background processes

### Test API Endpoints

Open browser and test:
- http://localhost/api/test
- Should return: `{"status": "OK", "message": "Server is working!"}`

### List All Users

- http://localhost/api/list_users
- Returns: `{"users": ["user1", "user2", ...]}`

---

## Port Configuration

The server uses port 80 by default (standard HTTP port).

To change the port:
1. Set the `PORT` environment variable before running
2. Or edit server.py line 197

For production self-hosting with port 80:
- Ensure Windows Firewall allows port 80
- Configure router port forwarding (see SELF_HOSTING.md)

---

## Security Considerations

When running as auto-start:
- Server runs as SYSTEM account (high privileges)
- Port 80 is exposed on all network interfaces (0.0.0.0)
- Ensure your firewall is configured properly
- Consider using a reverse proxy (nginx) for production
- For external access, follow the security guidelines in SELF_HOSTING.md

---

## Next Steps

After setting up auto-start:

1. **Configure firewall** (if hosting externally):
   ```cmd
   netsh advfirewall firewall add rule name="Lexpresso Server" dir=in action=allow protocol=TCP localport=80
   ```

2. **Set up port forwarding** (for external access):
   - See SELF_HOSTING.md for detailed instructions

3. **Configure domain** (optional):
   - Point your domain to your public IP
   - See SELF_HOSTING.md Step 5

4. **Set up HTTPS** (recommended for production):
   - Use Cloudflare or Let's Encrypt
   - See SELF_HOSTING.md Step 7

---

## Uninstall

To completely remove the auto-start:

1. **Remove the scheduled task:**
   ```powershell
   Unregister-ScheduledTask -TaskName "Lexpresso Server Auto-Start" -Confirm:$false
   ```

2. **Remove the batch file** (optional):
   - Delete `start_lexpresso.bat`

3. **Remove firewall rule** (if added):
   ```cmd
   netsh advfirewall firewall delete rule name="Lexpresso Server"
   ```

---

## Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Review SELF_HOSTING.md for network configuration
3. Check Windows Event Viewer for error messages
4. Verify Python is installed and in PATH

---

**Ready to go!** Your Lexpresso server should now start automatically when Windows boots.
