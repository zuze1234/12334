# 🧪 Testing Guide

This guide helps you test the clap detection application.

## Manual Testing Checklist

### Backend Tests

#### 1. Configuration Module
```bash
python3 -c "from config import Config; c = Config(); print('✓ Config loaded')"
```

#### 2. Audio Detector Module
```bash
python3 -c "from audio_detector import AudioDetector; print('Available devices:'); [print(f'  - {d}') for d in AudioDetector.get_available_devices()]; print('✓ Audio detector working')"
```

#### 3. Yandex API Module
```bash
# Set your token first
export YANDEX_TOKEN=your_token_here
python3 -c "from yandex_api import YandexHomeAPI; from config import Config; api = YandexHomeAPI(Config().get_yandex_token()); devices = api.get_devices(); print(f'✓ Found {len(devices)} devices')"
```

### Web Interface Tests

#### 1. Start Server
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

#### 2. Test Endpoints

Open another terminal:

```bash
# Test status endpoint
curl http://localhost:5000/api/status

# Test audio devices endpoint
curl http://localhost:5000/api/audio-devices

# Test settings endpoint
curl http://localhost:5000/api/settings

# Test Yandex devices endpoint
curl http://localhost:5000/api/devices
```

#### 3. Web UI Tests

Open browser to `http://localhost:5000` and verify:

- [ ] Page loads correctly
- [ ] Theme toggle works (light/dark)
- [ ] Microphone dropdown populates
- [ ] Status indicators show correct state
- [ ] All buttons are clickable
- [ ] Settings sliders work
- [ ] Event log displays

### Audio Detection Tests

#### 1. Microphone Selection
- Select different microphones from dropdown
- Verify audio level bar responds
- Check that selected device persists after refresh

#### 2. Calibration
1. Click "Start Calibration"
2. Clap 3-4 times during 3-second window
3. Verify calibration results appear
4. Check suggested threshold is reasonable (typically 0.1-0.5)
5. Apply suggested threshold

#### 3. Clap Detection
1. Click "Start Listening"
2. Status should change to "Listening" (green)
3. Single clap: Should show audio level spike
4. Double clap (within 100-500ms): Should trigger device toggle
5. Check event log for detection events

#### 4. Sensitivity Testing

Test different sensitivity levels:

| Sensitivity | Expected Behavior |
|-------------|-------------------|
| 0-20% | Very sensitive, may have false positives |
| 30-50% | Moderate sensitivity (recommended) |
| 60-80% | Less sensitive, needs louder claps |
| 80-100% | Very insensitive, needs very loud sounds |

#### 5. Interval Testing

Test clap timing:

| Interval | Expected Result |
|----------|-----------------|
| < 100ms | Too fast, should not trigger |
| 100-500ms | Should trigger double-clap |
| > 500ms | Too slow, should not trigger |

### Device Control Tests

#### 1. Manual Toggle
- Click "Toggle" button for each device
- Verify device state changes
- Check event log for toggle events

#### 2. Double-Clap Toggle
- Perform double-clap
- Verify all configured devices toggle
- Check WebSocket events in browser console
- Verify event log shows device toggle

#### 3. Multiple Devices
- Test with 1, 2, and 3 devices configured
- Verify all devices toggle simultaneously

### WebSocket Tests

Open browser console (F12) and check for WebSocket events:

```javascript
// Should see these events when listening
// audio_level - continuous
// clap_detected - when clapping
// device_toggled - when devices change
// event - general events
```

### Error Handling Tests

#### 1. No Token
```bash
# Remove token temporarily
unset YANDEX_TOKEN
python main.py
# Should see warning in console
```

#### 2. Invalid Token
```bash
export YANDEX_TOKEN=invalid_token
python main.py
# Should handle gracefully
```

#### 3. No Microphone Access
- Deny microphone permissions
- Verify error message appears
- Check event log

#### 4. Network Failure
- Disconnect internet
- Try to toggle devices
- Verify error handling

### Performance Tests

#### 1. Audio Processing
- Monitor CPU usage during listening
- Should be < 10% on modern systems
- Check `app.log` for performance issues

#### 2. WebSocket Performance
- Open multiple browser tabs
- Verify all receive real-time updates
- Check for memory leaks (leave running for hours)

#### 3. Event Log Performance
- Generate many events (> 100)
- Verify UI remains responsive
- Check that only 50 events are kept

### Integration Tests

#### Full Workflow Test
1. Start application
2. Select microphone
3. Calibrate
4. Start listening
5. Perform double-clap
6. Verify devices toggle
7. Check Yandex app to confirm device states
8. Stop listening
9. Close application

#### Cross-Platform Tests
- [ ] Test on Windows
- [ ] Test on macOS
- [ ] Test on Linux (Ubuntu/Debian)
- [ ] Test in Docker

### Browser Compatibility

Test in multiple browsers:
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge
- [ ] Mobile browsers

### Mobile Responsiveness

Test on different screen sizes:
- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

## Automated Testing (Future)

### Unit Tests Template

```python
# test_audio_detector.py
import unittest
from audio_detector import AudioDetector

class TestAudioDetector(unittest.TestCase):
    def test_get_devices(self):
        devices = AudioDetector.get_available_devices()
        self.assertIsInstance(devices, list)
    
    def test_rms_calculation(self):
        # Add RMS calculation tests
        pass

if __name__ == '__main__':
    unittest.main()
```

### Load Testing

```bash
# Test with multiple concurrent users
# (requires apache-bench or similar)
ab -n 1000 -c 10 http://localhost:5000/api/status
```

## Common Issues

### Issue: High CPU Usage
**Cause**: Large chunk size or high sample rate
**Solution**: Reduce chunk_size in config.py

### Issue: Delayed Detection
**Cause**: Small chunk size or slow processing
**Solution**: Increase chunk_size or optimize signal processing

### Issue: WebSocket Disconnects
**Cause**: Network issues or timeout
**Solution**: Check firewall, increase timeout

## Logging

Check logs for debugging:

```bash
# View real-time logs
tail -f app.log

# Search for errors
grep ERROR app.log

# Search for clap events
grep "Double clap" app.log
```

## Metrics to Monitor

- Audio level range (0.0 - 1.0 typical)
- Clap detection accuracy (% of intended claps detected)
- False positive rate (unintended triggers)
- API response time (should be < 1s)
- WebSocket latency (should be < 100ms)

## Test Environment Setup

For consistent testing, use:
- Quiet room (< 40dB ambient noise)
- Standard distance from microphone (30-60cm)
- Consistent clapping volume
- Same microphone across tests

## Reporting Issues

When reporting issues, include:
1. Operating system and version
2. Python version
3. Relevant logs from `app.log`
4. Browser console output
5. Steps to reproduce
6. Expected vs actual behavior

---

**Happy testing! 🧪**
