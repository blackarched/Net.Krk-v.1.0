# 📱 Net.Krk Pydroid Setup Guide

## Step 1: Test Basic Setup
Run this in Pydroid first:
```python
exec(open('test_pydroid.py').read())
```

## Step 2: If Test Fails
Check these common issues:

### Issue 1: Missing Dependencies
```python
# Run this to install missing packages
import subprocess
import sys

packages = ['flask', 'scapy', 'psutil', 'flask-cors']
for package in packages:
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print(f"✅ Installed {package}")
    except:
        print(f"❌ Failed to install {package}")
```

### Issue 2: Port Already in Use
```python
# Check what's using port 5000
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('localhost', 5000))
if result == 0:
    print("❌ Port 5000 is in use")
else:
    print("✅ Port 5000 is available")
sock.close()
```

### Issue 3: Permission Issues
```python
# Check current directory and permissions
import os
print(f"Current directory: {os.getcwd()}")
print(f"Can write files: {os.access('.', os.W_OK)}")
```

## Step 3: Start Simple Dashboard
Once the test passes, run:
```python
exec(open('simple_dashboard.py').read())
```

## Step 4: Access Dashboard
Open your Android browser and go to:
- **Main Dashboard**: `http://localhost:5000`
- **Advanced Tools**: `http://localhost:5000/advanced`

## Troubleshooting Common Issues

### "Module not found" errors
```python
# Install missing modules
import subprocess
import sys
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask', 'flask-cors'])
```

### "Address already in use" error
```python
# Kill any existing processes on port 5000
import subprocess
subprocess.run(['pkill', '-f', 'python.*5000'])
```

### "Permission denied" errors
- Check Pydroid permissions in Android settings
- Make sure Pydroid has storage and network access

### Dashboard loads but buttons don't work
- Check browser console for JavaScript errors
- Try a different browser (Chrome, Firefox)
- Clear browser cache

## Alternative: Direct HTML Access
If Flask doesn't work, you can access the HTML files directly:

1. Copy the HTML files to your Android storage
2. Open them directly in your browser
3. Note: Some features may not work without the backend

## Quick Fix Script
Run this if nothing else works:
```python
import os
import sys
import subprocess

# Install everything
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask', 'flask-cors', 'scapy', 'psutil'])

# Start simple dashboard
os.system('python simple_dashboard.py')
```