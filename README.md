# server-health-checker

### Note: Environment Variable Option

Instead of config.json, users can run:

-Linux / Mac
```bash
export SERVERS="https://httpbin.org/status/200,https://httpbin.org/status/500"
python health_checker.py
```
- Windows
```bash
set SERVERS=https://httpbin.org/status/200,https://httpbin.org/status/500
python health_checker.py
```